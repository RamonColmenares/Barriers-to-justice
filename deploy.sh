#!/bin/bash

echo "=== JUVENILE IMMIGRATION API - EC2 DEPLOYMENT ==="
echo "Python 3.13.4 | Docker | EC2 t2.micro Free Tier"
echo ""

# Check dependencies
command -v terraform >/dev/null 2>&1 || { echo "Error: terraform is required but not installed." >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "Error: aws cli is required but not installed." >&2; exit 1; }

# Check AWS credentials
aws sts get-caller-identity >/dev/null 2>&1 || { echo "Error: AWS credentials not configured." >&2; exit 1; }

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

echo "✓ Infrastructure deployed"
echo "  EC2 Instance IP: $EC2_IP"
echo "  S3 Bucket: $S3_BUCKET"

# Build and deploy frontend
echo "🎨 Building and deploying frontend..."
cd ../frontend
echo "PUBLIC_API_URL=http://$EC2_IP" > .env.production

if [ -f "package.json" ]; then
    npm install --silent
    npm run build
    
    if [ "$S3_BUCKET" != "null" ] && [ -n "$S3_BUCKET" ]; then
        aws s3 sync build/ s3://$S3_BUCKET --delete --quiet
        echo "✓ Frontend deployed to S3"
    else
        echo "⚠️  S3 bucket not available, skipping frontend deployment"
    fi
else
    echo "⚠️  No package.json found, skipping frontend build"
fi

# Wait for EC2 instance to be ready
echo "⏳ Waiting for EC2 instance to be ready..."
sleep 90

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
ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 ubuntu@$EC2_IP << 'EOF'
# Wait for Docker to be ready
timeout=300
while ! docker ps >/dev/null 2>&1 && [ $timeout -gt 0 ]; do
    echo "Waiting for Docker to start... ($timeout seconds remaining)"
    sleep 5
    timeout=$((timeout-5))
done

if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker failed to start within timeout"
    exit 1
fi

# Build Docker image
echo "Building Docker image with Python 3.13.4..."
docker build -t juvenile-immigration-api . || {
    echo "❌ Docker build failed"
    exit 1
}

# Stop and remove existing container
docker stop juvenile-api 2>/dev/null || true
docker rm juvenile-api 2>/dev/null || true

# Run the container
docker run -d \
    --name juvenile-api \
    -p 5000:5000 \
    --restart unless-stopped \
    juvenile-immigration-api || {
    echo "❌ Failed to start container"
    exit 1
}

# Wait and test
sleep 20
if docker ps | grep -q juvenile-api; then
    echo "✓ Container is running"
    
    # Test endpoints
    echo "🔍 Testing API endpoints..."
    
    if curl -f -s http://localhost:5000/health >/dev/null; then
        echo "✓ Health endpoint working"
    else
        echo "⚠️  Health endpoint not responding"
    fi
    
    if curl -f -s http://localhost/health >/dev/null; then
        echo "✓ Nginx proxy working"
    else
        echo "⚠️  Nginx proxy not responding"
    fi
    
    # Show container logs (last 10 lines)
    echo "📋 Container logs:"
    docker logs --tail 10 juvenile-api
else
    echo "❌ Container failed to start"
    echo "📋 Container logs:"
    docker logs juvenile-api
    exit 1
fi
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo ""
    echo "📡 API Endpoints:"
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
    echo ""
    echo "💰 Free Tier: EC2 t2.micro gives you 750 hours/month for 12 months"
else
    echo "❌ DEPLOYMENT FAILED!"
    echo "Check the logs above for details."
    exit 1
fi
