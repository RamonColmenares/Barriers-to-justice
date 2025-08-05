#!/bin/bash

echo "=== EC2 RECOVERY SCRIPT ==="
echo "Quick recovery for unresponsive EC2 instances"
echo ""

# Parse command line arguments
EC2_IP=""
ACTION=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --ip)
            EC2_IP="$2"
            shift 2
            ;;
        -i)
            EC2_IP="$2"
            shift 2
            ;;
        --action)
            ACTION="$2"
            shift 2
            ;;
        -a)
            ACTION="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--ip EC2_IP] [--action ACTION]"
            echo ""
            echo "Options:"
            echo "  --ip, -i EC2_IP      EC2 instance public IP address"
            echo "  --action, -a ACTION  Recovery action: restart-api, restart-services, cleanup, monitor"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Actions:"
            echo "  restart-api      Restart only the API container"
            echo "  restart-services Restart Nginx and API container"
            echo "  cleanup          Free up resources and restart services"
            echo "  monitor          Show real-time resource monitoring"
            echo ""
            echo "Example:"
            echo "  $0 --ip 54.123.45.67 --action cleanup"
            echo "  $0 -i 54.123.45.67 -a restart-api"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Try to get IP from Terraform if not provided
if [ -z "$EC2_IP" ] && [ -d "terraform-testing" ]; then
    echo "🔍 Getting EC2 IP from Terraform..."
    cd terraform-testing
    EC2_IP=$(terraform output -raw ec2_public_ip 2>/dev/null)
    cd ..
fi

if [ -z "$EC2_IP" ]; then
    echo "❌ EC2 IP is required. Use --ip parameter or run from directory with terraform-testing folder."
    exit 1
fi

# Default action if none provided
if [ -z "$ACTION" ]; then
    echo "🤔 No action specified. Available actions:"
    echo "  1. restart-api      - Restart only the API container"
    echo "  2. restart-services - Restart Nginx and API container"
    echo "  3. cleanup          - Free up resources and restart services"
    echo "  4. monitor          - Show real-time resource monitoring"
    echo ""
    read -p "Choose action (1-4): " choice
    case $choice in
        1) ACTION="restart-api" ;;
        2) ACTION="restart-services" ;;
        3) ACTION="cleanup" ;;
        4) ACTION="monitor" ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
fi

echo "🎯 Target: $EC2_IP"
echo "🔧 Action: $ACTION"
echo ""

# Test basic connectivity first
echo "🔍 Testing connectivity..."
if ! ping -c 2 $EC2_IP >/dev/null 2>&1; then
    echo "❌ Cannot ping EC2 instance. Check:"
    echo "   - Instance is running in AWS Console"
    echo "   - Security groups allow ICMP"
    echo "   - Network connectivity"
    exit 1
fi

if ! nc -z -w5 $EC2_IP 22 2>/dev/null; then
    echo "❌ SSH port not accessible. Check:"
    echo "   - Security group allows SSH from your IP"
    echo "   - Instance is not overloaded"
    echo "   - SSH service is running"
    exit 1
fi

echo "✅ Basic connectivity OK"
echo ""

# Execute recovery action
case $ACTION in
    "restart-api")
        echo "🔄 Restarting API container..."
        ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 ubuntu@$EC2_IP "
            echo 'Restarting API container...'
            sudo docker restart juvenile-api
            sleep 10
            if sudo docker ps | grep -q juvenile-api; then
                echo '✅ API container restarted successfully'
                curl -f -s http://localhost:5000/health >/dev/null && echo '✅ Health check passed' || echo '❌ Health check failed'
            else
                echo '❌ Failed to restart API container'
                sudo docker logs --tail 20 juvenile-api
            fi
        "
        ;;
        
    "restart-services")
        echo "🔄 Restarting all services..."
        ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 ubuntu@$EC2_IP "
            echo 'Restarting Nginx...'
            sudo systemctl restart nginx
            echo 'Restarting API container...'
            sudo docker restart juvenile-api
            sleep 15
            echo ''
            echo 'Service status:'
            sudo systemctl status nginx --no-pager | head -5
            sudo docker ps | grep juvenile-api
            echo ''
            echo 'Testing endpoints:'
            curl -f -s http://localhost:5000/health >/dev/null && echo '✅ API health check passed' || echo '❌ API health check failed'
            curl -f -s http://localhost/health >/dev/null && echo '✅ Nginx proxy check passed' || echo '❌ Nginx proxy check failed'
        "
        ;;
        
    "cleanup")
        echo "🧹 Cleaning up resources and restarting services..."
        ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 ubuntu@$EC2_IP "
            echo 'System cleanup in progress...'
            
            # Free up memory
            echo 'Clearing system caches...'
            sudo sync
            sudo echo 1 > /proc/sys/vm/drop_caches
            
            # Clean Docker resources
            echo 'Cleaning Docker resources...'
            sudo docker system prune -f
            sudo docker volume prune -f
            
            # Clean logs
            echo 'Cleaning system logs...'
            sudo journalctl --vacuum-size=50M
            sudo truncate -s 0 /var/log/nginx/access.log
            sudo truncate -s 0 /var/log/nginx/error.log
            
            # Restart services
            echo 'Restarting services...'
            sudo systemctl restart nginx
            sudo docker restart juvenile-api
            
            sleep 15
            
            echo ''
            echo 'System status after cleanup:'
            free -h
            df -h /
            sudo docker stats --no-stream juvenile-api
            
            echo ''
            echo 'Testing endpoints:'
            curl -f -s http://localhost:5000/health >/dev/null && echo '✅ API health check passed' || echo '❌ API health check failed'
            curl -f -s http://localhost/health >/dev/null && echo '✅ Nginx proxy check passed' || echo '❌ Nginx proxy check failed'
        "
        ;;
        
    "monitor")
        echo "📊 Real-time system monitoring (press Ctrl+C to stop)..."
        ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 ubuntu@$EC2_IP "
            echo 'Starting monitoring... (press Ctrl+C to stop)'
            echo ''
            while true; do
                clear
                echo '=== $(date) ==='
                echo ''
                echo 'SYSTEM RESOURCES:'
                free -h
                echo ''
                df -h / | tail -1
                echo ''
                uptime
                echo ''
                echo 'DOCKER CONTAINER:'
                if sudo docker ps | grep -q juvenile-api; then
                    sudo docker stats --no-stream juvenile-api
                else
                    echo 'Container not running'
                fi
                echo ''
                echo 'API HEALTH:'
                if curl -f -s http://localhost:5000/health >/dev/null; then
                    echo '✅ API is healthy'
                else
                    echo '❌ API is not responding'
                fi
                echo ''
                echo 'TOP PROCESSES:'
                ps aux --sort=-%mem | head -5
                echo ''
                echo 'Press Ctrl+C to stop monitoring...'
                sleep 5
            done
        " 2>/dev/null
        ;;
        
    *)
        echo "❌ Unknown action: $ACTION"
        exit 1
        ;;
esac

echo ""
echo "✅ Recovery action completed!"
echo ""
echo "🔗 Quick verification:"
HOSTNAME_SSLIP="$(echo "$EC2_IP" | tr '.' '-')".sslip.io

if curl -f -s --connect-timeout 10 "http://$HOSTNAME_SSLIP/health" >/dev/null; then
    echo "✅ API is accessible via HTTP"
else
    echo "❌ API is not accessible via HTTP"
fi

if curl -f -s --connect-timeout 10 -k "https://$HOSTNAME_SSLIP/health" >/dev/null; then
    echo "✅ API is accessible via HTTPS"
else
    echo "❌ API is not accessible via HTTPS"
fi
