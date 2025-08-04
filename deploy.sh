#!/bin/bash

echo "=== JUVENILE IMMIGRATION API - EC2 DEPLOYMENT ==="
echo "Python 3.13.4 | Docker | EC2 t2.micro Free Tier"
echo ""

# Check dependencies
command -v terraform >/dev/null 2>&1 || { echo "Error: terraform is required but not installed." >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "Error: aws cli is required but not installed." >&2; exit 1; }

# Check AWS credentials
aws sts get-caller-identity >/dev/null 2>&1 || { echo "Error: AWS credentials not configured." >&2; exit 1; }

# Load secrets (e.g., CONTACT_EMAIL) from env or from a user file outside the repo
if [ -z "$CONTACT_EMAIL" ] && [ -f "$HOME/.juvenile_api_deploy" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.juvenile_api_deploy"
fi

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
terraform plan
terraform apply -auto-approve

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
    Dockerfile docker-entrypoint.py ubuntu@$EC2_IP:~/ 2>/dev/null || {
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

# Create Nginx site for the API
sudo rm -f /etc/nginx/sites-enabled/default
sudo tee /etc/nginx/sites-available/juvenile-api >/dev/null <<NGINX
server {
    listen 80;
    server_name ${HOSTNAME_SSLIP};

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 60;
        proxy_send_timeout 300;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/juvenile-api /etc/nginx/sites-enabled/juvenile-api
sudo nginx -t && sudo systemctl reload nginx

# Quick HTTP check on port 80 before attempting TLS
if curl -fsS "http://$HOSTNAME_SSLIP/health" >/dev/null; then
    echo "✓ HTTP (80) proxy reachable"
else
    echo "⚠️  HTTP (80) proxy not reachable at http://$HOSTNAME_SSLIP/health"
fi

# Obtain/renew a Let's Encrypt certificate for the sslip.io hostname
# The CONTACT_EMAIL is exported from the local environment prior to this heredoc.
if [ -n "$CONTACT_EMAIL" ]; then
    sudo certbot --nginx --agree-tos -m "$CONTACT_EMAIL" --no-eff-email --redirect -d "$HOSTNAME_SSLIP" --non-interactive || true
else
    sudo certbot --nginx --agree-tos --register-unsafely-without-email --redirect -d "$HOSTNAME_SSLIP" --non-interactive || true
fi

echo "Nginx is serving: ${HOSTNAME_SSLIP}"

# Clean up old Docker containers and images...
sudo docker stop juvenile-api 2>/dev/null || true
sudo docker rm juvenile-api 2>/dev/null || true
sudo docker rmi juvenile-immigration-api 2>/dev/null || true

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
    --restart unless-stopped \
    juvenile-immigration-api || {
    echo "❌ Failed to start container"
    exit 1
}

# Wait and test
sleep 20
if sudo docker ps | grep -q juvenile-api; then
    echo "✓ Container is running"
    
    # Test endpoints
    echo "🔍 Testing API endpoints..."
    
    if curl -f -s http://localhost:5000/health >/dev/null; then
        echo "✓ Health endpoint working"
    else
        echo "⚠️  Health endpoint not responding"
    fi
    
    if curl -f -s -k https://localhost/health >/dev/null; then
        echo "✓ HTTPS proxy working"
    else
        echo "⚠️  HTTPS proxy not responding"
    fi
    
    # Show container logs (last 10 lines)
    echo "📋 Container logs:"
    sudo docker logs --tail 10 juvenile-api
else
    echo "❌ Container failed to start"
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

    # Then, wait for certificate and HTTPS (port 443)
    ATTEMPTS=30
    SLEEP=5
    until curl -fsS "https://$HOSTNAME_SSLIP/health" >/dev/null || [ $ATTEMPTS -le 0 ]; do
        echo "   ... waiting for certificate and server (attempts left: $ATTEMPTS)"
        sleep $SLEEP
        ATTEMPTS=$((ATTEMPTS-1))
    done

    if curl -fsS "https://$HOSTNAME_SSLIP/health" >/dev/null; then
        echo "✓ HTTPS health check OK"
    else
        echo "⚠️  HTTPS health check failed at https://$HOSTNAME_SSLIP/health"
    fi

    # Test a key API endpoint as well
    if curl -fsS "https://$HOSTNAME_SSLIP/api/findings/outcome-percentages" -o /dev/null; then
        echo "✓ Findings endpoint OK"
    else
        echo "⚠️  Findings endpoint check failed at https://$HOSTNAME_SSLIP/api/findings/outcome-percentages"
    fi

    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo ""
    echo "📡 API Endpoints (hostname with valid cert):"
    echo "   Health Check: https://$HOSTNAME_SSLIP/health"
    echo "   Overview:     https://$HOSTNAME_SSLIP/api/overview"
    echo "   Basic Stats:  https://$HOSTNAME_SSLIP/api/data/basic-stats"
    echo "   Findings:     https://$HOSTNAME_SSLIP/api/findings/*"
    echo ""
    echo "📡 API Endpoints (by IP, for debugging):"
    echo "   Health Check: https://$EC2_IP/health"
    echo "   Overview:     https://$EC2_IP/api/overview"
    echo "   Basic Stats:  https://$EC2_IP/api/data/basic-stats"
    echo "   Findings:     https://$EC2_IP/api/findings/*"
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
else
    echo "❌ DEPLOYMENT FAILED!"
    echo "Check the logs above for details."
    exit 1
fi
