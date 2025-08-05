#!/bin/bash

echo "=== JUVENILE IMMIGRATION API - EC2 DEPLOYMENT ==="
echo "Python 3.13.4 | Docker | EC2 t2.micro Free Tier"
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
cd terraform-ec2
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

# Configure 1GB swap to prevent OOM issues
if [ ! -f /swapfile ]; then
    echo "Configuring 1GB swap..."
    sudo fallocate -l 1G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

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

# Build Docker image
echo "🐳 Building Docker image with Python 3.13.4..."
sudo docker build -t juvenile-immigration-api . || {
    echo "❌ Docker build failed"
    exit 1
}

# Run the container first
echo "🚀 Starting Docker container..."
sudo docker run -d \
    --name juvenile-api \
    -p 5000:5000 \
    --memory="512m" --cpus="0.5" \
    --restart unless-stopped \
    -e CONTACT_EMAIL="$CONTACT_EMAIL" \
    juvenile-immigration-api || {
    echo "❌ Failed to start container"
    exit 1
}

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 15

# Test if the API is responding locally
if curl -f -s http://localhost:5000/health >/dev/null; then
    echo "✓ API container is responding"
else
    echo "❌ API container is not responding"
    sudo docker logs juvenile-api
    exit 1
fi

# Create Nginx site for the API
echo "🌐 Configuring Nginx reverse proxy..."
sudo rm -f /etc/nginx/sites-enabled/default
sudo tee /etc/nginx/sites-available/juvenile-api >/dev/null <<NGINX
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _ ${HOSTNAME_SSLIP};

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 10;
        proxy_send_timeout 30;
        proxy_read_timeout 30;
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
sudo docker stop juvenile-api 2>/dev/null || true
sudo docker rm juvenile-api 2>/dev/null || true
sudo docker rmi juvenile-immigration-api 2>/dev/null || true

sudo docker system prune -af --volumes || true
sudo journalctl --vacuum-size=100M || true
sudo apt-get clean -y || true

# Build Docker image
echo "Building Docker image with Python 3.13.4..."
sudo docker build -t juvenile-immigration-api . || {
    echo "❌ Docker build failed"
    exit 1
}

# Run the container
sudo docker run -d \
    --name juvenile-api \
    -p 5000:5000 \
    --memory="512m" --cpus="0.5" \
    --restart unless-stopped \
    -e CONTACT_EMAIL="$CONTACT_EMAIL" \
    juvenile-immigration-api || {
    echo "❌ Failed to start container"
    exit 1
}

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
    
    # Show container logs (last 10 lines)
    echo "📋 Container logs:"
    sudo docker logs --tail 10 juvenile-api
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
    echo "   Docker Logs:  docker logs juvenile-api"
    echo "   Restart API:  docker restart juvenile-api"
    if [ "$CERTBOT_SUCCESS" = false ]; then
        echo "   Setup SSL:    sudo certbot --nginx -d $HOSTNAME_SSLIP"
    fi
else
    echo "❌ DEPLOYMENT FAILED!"
    echo "Check the logs above for details."
    exit 1
fi
