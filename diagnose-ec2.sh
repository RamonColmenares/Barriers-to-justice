#!/bin/bash

echo "=== EC2 API DIAGNOSTICS SCRIPT ==="
echo ""

# Parse command line arguments
EC2_IP=""
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
        --help|-h)
            echo "Usage: $0 [--ip EC2_IP] [-i EC2_IP]"
            echo ""
            echo "Options:"
            echo "  --ip, -i EC2_IP      EC2 instance public IP address"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --ip 54.123.45.67"
            echo "  $0 -i 54.123.45.67"
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
    echo "🔍 Trying to get EC2 IP from Terraform..."
    cd terraform-testing
    EC2_IP=$(terraform output -raw ec2_public_ip 2>/dev/null)
    cd ..
fi

if [ -z "$EC2_IP" ]; then
    echo "❌ EC2 IP is required. Use --ip parameter or run from directory with terraform-testing folder."
    exit 1
fi

echo "🎯 Diagnosing EC2 instance: $EC2_IP"
echo ""

# Basic connectivity tests
echo "🔗 Testing basic connectivity..."
if ping -c 3 $EC2_IP >/dev/null 2>&1; then
    echo "✅ ICMP ping successful"
else
    echo "❌ ICMP ping failed"
fi

if nc -z -w5 $EC2_IP 22 2>/dev/null; then
    echo "✅ SSH port (22) is open"
else
    echo "❌ SSH port (22) is not responding"
fi

if nc -z -w5 $EC2_IP 80 2>/dev/null; then
    echo "✅ HTTP port (80) is open"
else
    echo "❌ HTTP port (80) is not responding"
fi

if nc -z -w5 $EC2_IP 443 2>/dev/null; then
    echo "✅ HTTPS port (443) is open"
else
    echo "❌ HTTPS port (443) is not responding"
fi

echo ""

# Try HTTP health check
echo "🏥 Testing API health endpoints..."
HOSTNAME_SSLIP="$(echo "$EC2_IP" | tr '.' '-')".sslip.io

# Test direct container connection (port 5000)
echo "🐳 Testing direct container connection..."
if nc -z -w5 $EC2_IP 5000 2>/dev/null; then
    echo "✅ Container port (5000) is accessible"
    if curl -f -s --connect-timeout 5 "http://$EC2_IP:5000/health" >/dev/null; then
        echo "✅ Direct container health check successful"
    else
        echo "❌ Direct container health check failed"
    fi
else
    echo "❌ Container port (5000) is not accessible"
fi

echo ""
echo "🌐 Testing through Nginx proxy..."

# Test HTTP through Nginx
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "http://$EC2_IP/health" 2>/dev/null)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ HTTP health check (by IP) successful"
elif [ "$HTTP_STATUS" = "502" ]; then
    echo "❌ HTTP health check (by IP) failed - 502 Bad Gateway (Nginx can't reach container)"
elif [ -n "$HTTP_STATUS" ]; then
    echo "❌ HTTP health check (by IP) failed - HTTP $HTTP_STATUS"
else
    echo "❌ HTTP health check (by IP) failed - No response"
fi

HTTP_STATUS_HOST=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "http://$HOSTNAME_SSLIP/health" 2>/dev/null)
if [ "$HTTP_STATUS_HOST" = "200" ]; then
    echo "✅ HTTP health check (by hostname) successful"
elif [ "$HTTP_STATUS_HOST" = "502" ]; then
    echo "❌ HTTP health check (by hostname) failed - 502 Bad Gateway"
elif [ -n "$HTTP_STATUS_HOST" ]; then
    echo "❌ HTTP health check (by hostname) failed - HTTP $HTTP_STATUS_HOST"
else
    echo "❌ HTTP health check (by hostname) failed - No response"
fi

HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 -k "https://$HOSTNAME_SSLIP/health" 2>/dev/null)
if [ "$HTTPS_STATUS" = "200" ]; then
    echo "✅ HTTPS health check successful"
elif [ "$HTTPS_STATUS" = "502" ]; then
    echo "❌ HTTPS health check failed - 502 Bad Gateway"
elif [ -n "$HTTPS_STATUS" ]; then
    echo "❌ HTTPS health check failed - HTTP $HTTPS_STATUS"
else
    echo "❌ HTTPS health check failed - No response"
fi

echo ""
echo "🧪 Testing API endpoints with detailed responses..."

# Test a findings endpoint to check for CORS and API functionality
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 "https://$HOSTNAME_SSLIP/api/findings/outcome-percentages" 2>/dev/null)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ API findings endpoint working"
elif [ "$API_STATUS" = "502" ]; then
    echo "❌ API findings endpoint - 502 Bad Gateway"
elif [ "$API_STATUS" = "504" ]; then
    echo "❌ API findings endpoint - 504 Gateway Timeout"
elif [ -n "$API_STATUS" ]; then
    echo "❌ API findings endpoint - HTTP $API_STATUS"
else
    echo "❌ API findings endpoint - No response"
fi

# Check CORS headers
echo ""
echo "🔄 Checking CORS configuration..."
CORS_RESPONSE=$(curl -s -I -H "Origin: https://d30ap9o2ygmovh.cloudfront.net" "https://$HOSTNAME_SSLIP/api/findings/outcome-percentages" 2>/dev/null | grep -i "access-control-allow-origin" || echo "No CORS header found")
echo "CORS header: $CORS_RESPONSE"

echo ""

# Try SSH connection and run diagnostics
echo "🔧 Attempting SSH diagnostics..."
if ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=10 ubuntu@$EC2_IP "echo 'SSH connection successful'" 2>/dev/null; then
    echo "✅ SSH connection successful"
    echo ""
    echo "🔍 Running remote diagnostics..."
    
    ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 ubuntu@$EC2_IP "bash -s" << 'EOF'
echo "=== SYSTEM RESOURCES ==="
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h /
echo ""
echo "CPU load:"
uptime
echo ""
echo "Top memory consumers:"
ps aux --sort=-%mem | head -10
echo ""

echo "=== DOCKER STATUS ==="
if command -v docker >/dev/null 2>&1; then
    echo "Docker service status:"
    sudo systemctl status docker --no-pager | head -10
    echo ""
    
    echo "Docker containers:"
    sudo docker ps -a
    echo ""
    
    if sudo docker ps | grep -q juvenile-api; then
        echo "✅ API container is running"
        echo ""
        echo "Container resource usage:"
        sudo docker stats --no-stream juvenile-api
        echo ""
        echo "Container health status:"
        sudo docker inspect juvenile-api --format='{{.State.Health.Status}}' 2>/dev/null || echo "No health check configured"
        echo ""
        echo "Testing direct container connection:"
        curl -f -s --connect-timeout 5 http://localhost:5000/health >/dev/null && echo "✅ Container responds locally" || echo "❌ Container not responding locally"
        echo ""
        echo "Container logs (last 30 lines):"
        sudo docker logs --tail 30 juvenile-api
    else
        echo "❌ API container is not running"
        echo ""
        echo "Last container logs:"
        sudo docker logs --tail 50 juvenile-api 2>/dev/null || echo "No logs available"
        echo ""
        echo "Attempting to start container..."
        sudo docker start juvenile-api && echo "Container started" || echo "Failed to start container"
    fi
else
    echo "❌ Docker is not installed"
fi
echo ""

echo "=== NGINX STATUS ==="
if command -v nginx >/dev/null 2>&1; then
    echo "Nginx service status:"
    sudo systemctl status nginx --no-pager | head -10
    echo ""
    echo "Nginx configuration test:"
    sudo nginx -t
    echo ""
    echo "Nginx access logs (last 5 lines):"
    sudo tail -5 /var/log/nginx/access.log 2>/dev/null || echo "No nginx access logs"
    echo ""
    echo "Nginx error logs (last 10 lines):"
    sudo tail -10 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error logs"
    echo ""
    echo "Testing Nginx -> Container connection:"
    curl -f -s --connect-timeout 5 http://localhost/health >/dev/null && echo "✅ Nginx proxy working" || echo "❌ Nginx proxy failing"
else
    echo "❌ Nginx is not installed"
fi
echo ""

echo "=== NETWORK STATUS ==="
echo "Active connections:"
sudo netstat -tlnp | grep -E ':80|:443|:5000|:22'
echo ""
echo "Process listening on port 5000:"
sudo lsof -i :5000 2>/dev/null || echo "No process on port 5000"
echo ""

echo "=== SYSTEM LOGS ==="
echo "Recent Nginx errors:"
sudo journalctl -u nginx --no-pager -n 5 -p err || echo "No recent Nginx errors"
echo ""
echo "Recent Docker errors:"
sudo journalctl -u docker --no-pager -n 5 -p err || echo "No recent Docker errors"
echo ""
echo "Recent system errors:"
sudo journalctl -p err --no-pager -n 10 --since "5 minutes ago" || echo "No recent errors"

echo ""
echo "=== MONITORING LOGS ==="
if [ -f /var/log/api-monitor.log ]; then
    echo "API monitoring logs (last 15 lines):"
    sudo tail -15 /var/log/api-monitor.log
else
    echo "No monitoring logs found"
fi

echo ""
echo "=== CORS AND API CONFIGURATION ==="
echo "Checking if Flask CORS is configured..."
sudo docker exec juvenile-api python3 -c "
import sys
try:
    import flask_cors
    print('✅ Flask-CORS is available')
except ImportError:
    print('❌ Flask-CORS not found')

try:
    from api.config import Config
    if hasattr(Config, 'CORS_ORIGINS'):
        print(f'CORS Origins: {Config.CORS_ORIGINS}')
    else:
        print('No CORS_ORIGINS in config')
except Exception as e:
    print(f'Error checking config: {e}')
" 2>/dev/null || echo "Cannot check CORS configuration"
EOF

else
    echo "❌ SSH connection failed"
    echo ""
    echo "🔧 Troubleshooting suggestions:"
    echo "1. Check if the EC2 instance is running in AWS Console"
    echo "2. Verify the security group allows SSH (port 22) from your IP"
    echo "3. Ensure the SSH key file exists: ~/.ssh/juvenile-immigration-key.pem"
    echo "4. Check if the instance has enough resources (CPU/Memory)"
    echo "5. Try restarting the instance from AWS Console"
fi

echo ""
echo "🚀 Recovery commands (if SSH is accessible):"
echo "# Restart the API container:"
echo "ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo docker restart juvenile-api'"
echo ""
echo "# Restart all services:"
echo "ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo systemctl restart nginx && sudo docker restart juvenile-api'"
echo ""
echo "# Check resource usage:"
echo "ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'free -h && df -h && sudo docker stats --no-stream'"
echo ""
echo "# View logs:"
echo "ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo docker logs juvenile-api'"
