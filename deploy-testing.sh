#!/bin/bash

echo "=== JUVENILE IMMIGRATION API - EC2 DEPLOYMENT ==="
echo "Python 3.13.4 | Docker | EC2 t3.small (2GB RAM)"
echo ""

# Parse command line arguments
CONTACT_EMAIL=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --email)
            CONTACT_EMAIL="$2"
            shift 2
            ;;
        -e)
            CONTACT_EMAIL="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--email EMAIL] [-e EMAIL]"
            echo ""
            echo "Options:"
            echo "  --email, -e EMAIL    Contact email for SES and Let's Encrypt certificates"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --email contact@yourdomain.com"
            echo "  $0 -e contact@yourdomain.com"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check dependencies
command -v terraform >/dev/null 2>&1 || { echo "Error: terraform is required but not installed." >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "Error: aws cli is required but not installed." >&2; exit 1; }

# Check AWS credentials
aws sts get-caller-identity >/dev/null 2>&1 || { echo "Error: AWS credentials not configured." >&2; exit 1; }

# Load secrets from env file if email not provided as parameter
if [ -z "$CONTACT_EMAIL" ] && [ -f "$HOME/.juvenile_api_deploy" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.juvenile_api_deploy"
fi

# Prompt for email if still not provided
if [ -z "$CONTACT_EMAIL" ]; then
    echo "📧 Contact email is required for:"
    echo "   - AWS SES email service configuration"
    echo "   - Let's Encrypt SSL certificate registration"
    echo ""
    read -p "Enter your contact email: " CONTACT_EMAIL
    
    if [ -z "$CONTACT_EMAIL" ]; then
        echo "❌ Contact email is required for deployment"
        exit 1
    fi
    
    # Ask if user wants to save the email for future deployments
    echo ""
    read -p "Save this email for future deployments? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "CONTACT_EMAIL=$CONTACT_EMAIL" > "$HOME/.juvenile_api_deploy"
        echo "✓ Email saved to $HOME/.juvenile_api_deploy"
    fi
fi

echo "✓ Using contact email: $CONTACT_EMAIL"

# Disable AWS CLI pager to avoid opening outputs in "less"
export AWS_PAGER=""

# Check if SSH key exists, if not create one
if [ ! -f ~/.ssh/juvenile-immigration-key.pem ]; then
    echo "Creating SSH key pair..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/juvenile-immigration-key.pem -N ""
    echo "✓ SSH key created at ~/.ssh/juvenile-immigration-key.pem"
fi

# Ensure the key has correct permissions
chmod 400 ~/.ssh/juvenile-immigration-key.pem
chmod 644 ~/.ssh/juvenile-immigration-key.pem.pub

echo "✓ SSH keys configured"

# Clean up any previous builds
echo "🧹 Cleaning up previous builds..."
rm -rf build/ api.zip

# Initialize and apply Terraform
echo "🚀 Deploying infrastructure with Terraform..."
cd terraform-testing
terraform init
terraform plan -var="contact_email=$CONTACT_EMAIL"
terraform apply -var="contact_email=$CONTACT_EMAIL" -auto-approve

# Get outputs
EC2_IP=$(terraform output -raw ec2_public_ip 2>/dev/null)
S3_BUCKET=$(terraform output -raw s3_bucket_name 2>/dev/null)
CLOUDFRONT_URL=$(terraform output -raw cloudfront_url 2>/dev/null)

if [ -z "$EC2_IP" ]; then
    echo "❌ Failed to get EC2 IP from Terraform"
    exit 1
fi

# Compute sslip.io hostname for the current public IP
HOSTNAME_SSLIP="$(echo "$EC2_IP" | tr '.' '-')".sslip.io

echo "✓ Infrastructure deployed"
echo "  EC2 Instance IP: $EC2_IP"
echo "  S3 Bucket: $S3_BUCKET"
echo "  Hostname: $HOSTNAME_SSLIP"

# Build and deploy frontend
echo "🎨 Building and deploying frontend..."
cd ../frontend
echo "PUBLIC_API_URL=https://$HOSTNAME_SSLIP/api" > .env.production

if [ -f "package.json" ]; then
    npm install --silent
    npm run build
    
    if [ "$S3_BUCKET" != "null" ] && [ -n "$S3_BUCKET" ]; then
        aws s3 sync build/ s3://$S3_BUCKET --delete --quiet
        echo "✓ Frontend deployed to S3"
        
        # Invalidate CloudFront cache if distribution exists
        if [ "$CLOUDFRONT_URL" != "null" ] && [ -n "$CLOUDFRONT_URL" ]; then
            echo "🔄 Invalidating CloudFront cache..."
            DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?DomainName=='$CLOUDFRONT_URL'].Id" --output text)
            if [ ! -z "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
                aws cloudfront create-invalidation --no-cli-pager --distribution-id $DISTRIBUTION_ID --paths "/*" --query 'Invalidation.Id' --output text
                echo "✓ CloudFront cache invalidated"
            else
                echo "⚠️  Could not find CloudFront distribution for invalidation"
            fi
        fi
    else
        echo "⚠️  S3 bucket not available, skipping frontend deployment"
    fi
else
    echo "⚠️  No package.json found, skipping frontend build"
fi

# Wait for EC2 instance to be ready
echo "⏳ Waiting for EC2 instance to be ready..."

# Copy files to EC2
echo "📦 Deploying backend to EC2..."
cd ..

scp -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 \
    Dockerfile main.py ubuntu@$EC2_IP:~/ 2>/dev/null || {
    echo "❌ Failed to copy Docker files. EC2 instance might not be ready yet."
    exit 1
}

scp -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 \
    -r api ubuntu@$EC2_IP:~/ 2>/dev/null || {
    echo "❌ Failed to copy API files"
    exit 1
}

echo "✓ Files copied to EC2"

# Deploy application on EC2
echo "🐳 Building and running Docker container..."
ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 ubuntu@$EC2_IP "export CONTACT_EMAIL='$CONTACT_EMAIL'; export EC2_IP='$EC2_IP'; export HOSTNAME_SSLIP='$HOSTNAME_SSLIP'; bash -s" << 'EOF'
# Initialize variables
CERTBOT_SUCCESS=false

# Ensure Docker is installed and running (Ubuntu 24.04 - use Docker's official repo)
if ! command -v docker >/dev/null 2>&1; then
    echo "⚙️ Installing Docker Engine from Docker's official repository ..."
    set -e
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
    fi
    UBUNTU_CODENAME="$(. /etc/os-release && echo $VERSION_CODENAME)"
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || {
        echo "⚠️ Installing docker-ce failed; falling back to Ubuntu 'docker.io' package ..."
        sudo apt-get install -y docker.io || true
    }
    sudo systemctl enable --now docker || true
    set +e
fi

# Ensure Docker service is up
if ! systemctl is-active --quiet docker; then
    echo "🔧 Starting Docker service..."
    sudo systemctl start docker || {
        echo "❌ Could not start docker.service"
        sudo journalctl -u docker --no-pager -n 100 || true
        exit 1
    }
fi

# Wait for Docker to be ready
timeout=300
while { ! command -v docker >/dev/null 2>&1 || ! systemctl is-active --quiet docker; } && [ $timeout -gt 0 ]; do
    echo "Waiting for Docker to start... $timeout seconds remaining"
    sleep 5
    timeout=$((timeout-5))
done

if { ! command -v docker >/dev/null 2>&1 || ! systemctl is-active --quiet docker; }; then
    echo "❌ Docker failed to start within timeout"
    sudo systemctl status docker || true
    exit 1
fi

# Configure 2GB swap for t3.small (more conservative approach)
if [ ! -f /swapfile ]; then
    echo "Configuring 2GB swap for t3.small stability..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    # Conservative swap settings to prevent system freezing
    echo 'vm.swappiness=5' | sudo tee -a /etc/sysctl.conf
    echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
    echo 'vm.dirty_ratio=10' | sudo tee -a /etc/sysctl.conf
    echo 'vm.dirty_background_ratio=5' | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p
fi

# Install system monitoring tools
echo "📊 Installing system monitoring tools..."
sudo apt-get install -y htop iotop sysstat

# Install and configure Nginx as reverse proxy with Let's Encrypt (sslip.io hostname)
echo "🌐 Installing Nginx and certbot..."
sudo apt-get update -y
sudo apt-get install -y nginx python3-certbot-nginx

# Prefer values exported from the local machine; if missing, try IMDSv2
if [ -z "$HOSTNAME_SSLIP" ]; then
    # Try to get public IP via IMDSv2
    TOKEN=$(curl -s --connect-timeout 2 -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" || true)
    EC2_PUBLIC_IP=$(curl -fsS --connect-timeout 2 -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/public-ipv4" 2>/dev/null || true)
    # Fallback to EC2_IP provided by the deploy script
    if [ -z "$EC2_PUBLIC_IP" ] && [ -n "$EC2_IP" ]; then
        EC2_PUBLIC_IP="$EC2_IP"
    fi
    if [ -n "$EC2_PUBLIC_IP" ]; then
        HOSTNAME_SSLIP="${EC2_PUBLIC_IP//./-}.sslip.io"
    fi
fi

if [ -z "$HOSTNAME_SSLIP" ]; then
    echo "❌ Could not determine HOSTNAME_SSLIP (empty). Aborting Nginx/Certbot setup."
    exit 1
fi

# Clean up old Docker containers and images first
echo "🧹 Cleaning up old containers..."
sudo docker stop juvenile-api 2>/dev/null || true
sudo docker rm juvenile-api 2>/dev/null || true
sudo docker rmi juvenile-immigration-api 2>/dev/null || true

sudo docker system prune -af --volumes || true
sudo journalctl --vacuum-size=100M || true
sudo apt-get clean -y || true

# Build Docker image with memory optimizations
echo "🐳 Building Docker image with memory optimizations for t3.small..."
sudo docker build -t juvenile-immigration-api . || {
    echo "❌ Docker build failed"
    exit 1
}

# Run the container with ultra-conservative resources for t3.small (2GB RAM)
echo "🚀 Starting Docker container with ultra-conservative resource limits..."
sudo docker run -d \
    --name juvenile-api \
    -p 5000:5000 \
    --memory="900m" --memory-swap="1800m" --cpus="1.0" \
    --oom-kill-disable=false \
    --restart unless-stopped \
    -e CONTACT_EMAIL="$CONTACT_EMAIL" \
    --shm-size=64m \
    --ulimit memlock=-1 \
    --ulimit nofile=65536:65536 \
    --security-opt seccomp=unconfined \
    --health-cmd="curl -f http://localhost:5000/health || exit 1" \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    --health-start-period=60s \
    juvenile-immigration-api || {
    echo "❌ Failed to start container"
    exit 1
}

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 15

# Install system monitoring script
echo "📊 Installing system monitoring script..."
sudo tee /usr/local/bin/monitor-api.sh >/dev/null <<'MONITOR'
#!/bin/bash
# API Health Monitor for t3.small instances - AGGRESSIVE MEMORY MANAGEMENT

LOGFILE="/var/log/api-monitor.log"
MAX_MEMORY_PERCENT=80  # Reduced from 85
MAX_CPU_PERCENT=85     # Reduced from 90

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | sudo tee -a "$LOGFILE"
}

check_container_health() {
    if ! sudo docker ps | grep -q juvenile-api; then
        log_message "ERROR: Container juvenile-api is not running"
        sudo docker start juvenile-api 2>/dev/null
        return 1
    fi
    
    # Check container resource usage
    STATS=$(sudo docker stats --no-stream --format "table {{.MemPerc}}\t{{.CPUPerc}}" juvenile-api 2>/dev/null | tail -n +2)
    if [ -n "$STATS" ]; then
        MEM_USAGE=$(echo "$STATS" | awk '{print $1}' | sed 's/%//')
        CPU_USAGE=$(echo "$STATS" | awk '{print $2}' | sed 's/%//')
        
        # More aggressive memory management
        if (( $(echo "$MEM_USAGE > $MAX_MEMORY_PERCENT" | bc -l) )); then
            log_message "WARNING: High memory usage: ${MEM_USAGE}% - Triggering cleanup"
            # Clear system caches
            sudo sync
            sudo echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true
            # Force garbage collection in container
            sudo docker exec juvenile-api python3 -c "import gc; gc.collect()" 2>/dev/null || true
        fi
        
        # Restart if memory is critically high
        if (( $(echo "$MEM_USAGE > 90" | bc -l) )); then
            log_message "CRITICAL: Memory usage: ${MEM_USAGE}% - Restarting container"
            sudo docker restart juvenile-api
        fi
        
        if (( $(echo "$CPU_USAGE > $MAX_CPU_PERCENT" | bc -l) )); then
            log_message "WARNING: High CPU usage: ${CPU_USAGE}%"
        fi
    fi
}

check_api_health() {
    if ! curl -f -s --connect-timeout 5 http://localhost:5000/health >/dev/null; then
        log_message "ERROR: API health check failed"
        sudo docker restart juvenile-api
        sleep 30
        if ! curl -f -s --connect-timeout 5 http://localhost:5000/health >/dev/null; then
            log_message "CRITICAL: API still not responding after restart"
        else
            log_message "INFO: API recovered after restart"
        fi
    fi
}

check_system_resources() {
    # Check system memory usage with more aggressive thresholds
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$MEM_USAGE" -gt 85 ]; then  # Reduced from 90
        log_message "WARNING: System memory usage at ${MEM_USAGE}%"
        # Clear caches if memory is high
        if [ "$MEM_USAGE" -gt 90 ]; then  # Reduced from 95
            sudo sync
            sudo echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true
            sudo echo 2 > /proc/sys/vm/drop_caches 2>/dev/null || true
            sudo echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
            log_message "INFO: Cleared system caches due to high memory usage"
        fi
    fi
    
    # Clean up old logs more frequently
    if [ $(du -s /var/log | cut -f1) -gt 102400 ]; then  # If logs > 100MB
        sudo journalctl --vacuum-size=50M >/dev/null 2>&1
        sudo truncate -s 1M /var/log/nginx/access.log 2>/dev/null || true
        sudo truncate -s 1M /var/log/nginx/error.log 2>/dev/null || true
        log_message "INFO: Cleaned up system logs"
    fi
}

# Main monitoring loop
check_container_health
check_api_health
check_system_resources
MONITOR

sudo chmod +x /usr/local/bin/monitor-api.sh

# Set up monitoring cron job (every 2 minutes)
echo "⏰ Setting up monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/2 * * * * /usr/local/bin/monitor-api.sh") | sudo crontab -

# Test if the API is responding locally
if curl -f -s http://localhost:5000/health >/dev/null; then
    echo "✓ API container is responding"
else
    echo "❌ API container is not responding"
    sudo docker logs juvenile-api
    exit 1
fi

# Create Nginx site for the API
echo "🌐 Configuring Nginx reverse proxy with optimized timeouts..."
sudo rm -f /etc/nginx/sites-enabled/default
sudo tee /etc/nginx/sites-available/juvenile-api >/dev/null <<NGINX
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _ ${HOSTNAME_SSLIP};

    # Increase timeouts for slow API responses (reduced from 300s to 120s)
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
    proxy_buffering off;
    proxy_buffer_size 64k;
    proxy_buffers 8 64k;
    proxy_busy_buffers_size 128k;

    # API routes with CORS
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Extended timeouts for API endpoints (reduced from 300s to 120s)
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        proxy_buffering off;
        proxy_buffer_size 64k;
        proxy_buffers 8 64k;
        proxy_busy_buffers_size 128k;
        
        # Do NOT add CORS headers here - Flask handles them
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Default catch-all
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/juvenile-api /etc/nginx/sites-enabled/juvenile-api

# Test nginx configuration
if sudo nginx -t; then
    echo "✓ Nginx configuration is valid"
    sudo systemctl reload nginx
else
    echo "❌ Nginx configuration is invalid"
    exit 1
fi

# Quick HTTP check on port 80 before attempting TLS
echo "🔍 Testing HTTP proxy..."
sleep 5
if curl -fsS "http://$HOSTNAME_SSLIP/health" >/dev/null; then
    echo "✓ HTTP (80) proxy reachable"
else
    echo "⚠️  HTTP (80) proxy not reachable at http://$HOSTNAME_SSLIP/health"
    echo "Checking nginx status..."
    sudo systemctl status nginx --no-pager
    exit 1
fi

# Obtain/renew a Let's Encrypt certificate for the sslip.io hostname
echo "🔐 Obtaining SSL certificate..."
CERTBOT_SUCCESS=false
if [ -n "$CONTACT_EMAIL" ]; then
    if sudo certbot --nginx --agree-tos -m "$CONTACT_EMAIL" --no-eff-email --redirect -d "$HOSTNAME_SSLIP" --non-interactive; then
        CERTBOT_SUCCESS=true
        echo "✓ SSL certificate obtained successfully"
    else
        echo "❌ Failed to obtain SSL certificate with email"
    fi
else
    if sudo certbot --nginx --agree-tos --register-unsafely-without-email --redirect -d "$HOSTNAME_SSLIP" --non-interactive; then
        CERTBOT_SUCCESS=true
        echo "✓ SSL certificate obtained successfully"
    else
        echo "❌ Failed to obtain SSL certificate without email"
    fi
fi

if [ "$CERTBOT_SUCCESS" = false ]; then
    echo "⚠️  SSL certificate setup failed, but continuing with HTTP only"
    echo "You can manually run: sudo certbot --nginx -d $HOSTNAME_SSLIP"
fi

echo "✓ Nginx is serving: ${HOSTNAME_SSLIP}"

# Test endpoints and show status
echo "🔍 Testing API endpoints..."

if sudo docker ps | grep -q juvenile-api; then
    echo "✓ Container is running"
    
    if curl -f -s http://localhost:5000/health >/dev/null; then
        echo "✓ Health endpoint working locally"
    else
        echo "⚠️  Health endpoint not responding locally"
    fi
    
    # Test HTTPS if certificate was obtained
    if [ "$CERTBOT_SUCCESS" = true ]; then
        if curl -f -s -k https://localhost/health >/dev/null; then
            echo "✓ HTTPS proxy working"
        else
            echo "⚠️  HTTPS proxy not responding"
        fi
    fi
    
    # Show container logs (last 10 lines) and resource usage
    echo "📋 Container logs (last 10 lines):"
    sudo docker logs --tail 10 juvenile-api
    echo ""
    echo "📊 System resource usage:"
    free -h
    df -h /
    sudo docker stats --no-stream juvenile-api
else
    echo "❌ Container is not running"
    echo "📋 Container logs:"
    sudo docker logs juvenile-api
    exit 1
fi
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🔎 Verifying HTTP/HTTPS on $HOSTNAME_SSLIP ..."
    
    # First, verify HTTP (port 80) works through Nginx
    if curl -fsS "http://$HOSTNAME_SSLIP/health" >/dev/null; then
        echo "✓ HTTP health check OK"
    else
        echo "⚠️  HTTP health check failed at http://$HOSTNAME_SSLIP/health"
    fi

    # Then, test HTTPS if certificate was obtained
    if [ "$CERTBOT_SUCCESS" = true ]; then
        echo "🔒 Testing HTTPS connectivity..."
        ATTEMPTS=20
        SLEEP=3
        until curl -fsS "https://$HOSTNAME_SSLIP/health" >/dev/null || [ $ATTEMPTS -le 0 ]; do
            echo "   ... waiting for HTTPS to be ready (attempts left: $ATTEMPTS)"
            sleep $SLEEP
            ATTEMPTS=$((ATTEMPTS-1))
        done

        if curl -fsS "https://$HOSTNAME_SSLIP/health" >/dev/null; then
            echo "✓ HTTPS health check OK"
        else
            echo "⚠️  HTTPS health check failed at https://$HOSTNAME_SSLIP/health"
            echo "You may need to wait a few more minutes for the certificate to propagate"
        fi

        # Test a key API endpoint as well
        if curl -fsS "https://$HOSTNAME_SSLIP/api/findings/outcome-percentages" -o /dev/null; then
            echo "✓ Findings endpoint OK"
        else
            echo "⚠️  Findings endpoint check failed at https://$HOSTNAME_SSLIP/api/findings/outcome-percentages"
        fi
    else
        echo "⚠️  HTTPS not available - certificate setup failed"
        echo "📡 Using HTTP endpoints only:"
        echo "   Health Check: http://$HOSTNAME_SSLIP/health"
        echo "   Overview:     http://$HOSTNAME_SSLIP/api/overview"
    fi

    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo ""
    
    if [ "$CERTBOT_SUCCESS" = true ]; then
        echo "📡 API Endpoints (HTTPS with valid cert):"
        echo "   Health Check: https://$HOSTNAME_SSLIP/health"
        echo "   Overview:     https://$HOSTNAME_SSLIP/api/overview"
        echo "   Basic Stats:  https://$HOSTNAME_SSLIP/api/data/basic-stats"
        echo "   Findings:     https://$HOSTNAME_SSLIP/api/findings/*"
        echo ""
    fi
    
    echo "📡 API Endpoints (HTTP):"
    echo "   Health Check: http://$HOSTNAME_SSLIP/health"
    echo "   Overview:     http://$HOSTNAME_SSLIP/api/overview"
    echo "   Basic Stats:  http://$HOSTNAME_SSLIP/api/data/basic-stats"
    echo "   Findings:     http://$HOSTNAME_SSLIP/api/findings/*"
    echo ""
    echo "📡 API Endpoints (by IP, for debugging):"
    echo "   Health Check: http://$EC2_IP/health"
    echo "   Overview:     http://$EC2_IP/api/overview"
    echo "   Basic Stats:  http://$EC2_IP/api/data/basic-stats"
    echo "   Findings:     http://$EC2_IP/api/findings/*"
    echo ""
    
    if [ "$S3_BUCKET" != "null" ] && [ -n "$S3_BUCKET" ]; then
        echo "🌐 Frontend URLs:"
        echo "   S3 Website:   http://$S3_BUCKET.s3-website-us-east-1.amazonaws.com"
        if [ "$CLOUDFRONT_URL" != "null" ] && [ -n "$CLOUDFRONT_URL" ]; then
            echo "   CloudFront:   https://$CLOUDFRONT_URL"
        fi
        echo ""
    fi
    
    echo "🔧 Management:"
    echo "   SSH Access:   ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP"
    echo "   Docker Logs:  ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo docker logs juvenile-api'"
    echo "   Restart API:  ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo docker restart juvenile-api'"
    echo "   System Stats: ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'free -h && df -h'"
    echo "   Diagnostics:  ./diagnose-ec2.sh --ip $EC2_IP"
    if [ "$CERTBOT_SUCCESS" = false ]; then
        echo "   Setup SSL:    ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo certbot --nginx -d $HOSTNAME_SSLIP'"
    fi
    echo ""
    echo "📊 Resource Usage Tips:"
    echo "   - Container limited to 1.2GB RAM (60% of total)"
    echo "   - 2GB swap configured for stability"
    echo "   - API monitoring runs every 2 minutes"
    echo "   - Auto-restart on container failure"
    echo "   - Nginx timeouts reduced to 120s"
    echo ""
    echo "🚨 If EC2 becomes unresponsive:"
    echo "   1. Run: ./diagnose-ec2.sh --ip $EC2_IP"
    echo "   2. Check AWS Console for instance status"
    echo "   3. Consider restarting the instance if necessary"
else
    echo "❌ DEPLOYMENT FAILED!"
    echo "Check the logs above for details."
    exit 1
fi
