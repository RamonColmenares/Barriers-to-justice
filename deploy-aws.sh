#!/bin/bash

# AWS Lambda deployment script
set -e

echo "🚀 Deploying Juvenile Immigration Data Analysis App to AWS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

print_header "Checking Prerequisites"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first:${NC}"
    echo "macOS: brew install awscli"
    echo "Linux: See AWS_DEPLOYMENT.md for instructions"
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform not found. Please install it first:${NC}"
    echo "macOS: brew install terraform"
    echo "Linux: See AWS_DEPLOYMENT.md for instructions"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run:${NC}"
    echo "aws configure"
    exit 1
fi

# Get AWS account info
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-east-1")

echo -e "${GREEN}✅ AWS Account: ${AWS_ACCOUNT}${NC}"
echo -e "${GREEN}✅ AWS Region: ${AWS_REGION}${NC}"
echo -e "${GREEN}✅ Prerequisites check passed${NC}"

print_header "Creating Lambda Deployment Package"

# Clean previous builds
rm -rf build/
rm -f api.zip

# Create build directory
mkdir -p build

# Copy API files
echo "📂 Copying API files..."
cp -r api/ build/
cp lambda_handler.py build/
cp requirements-lambda.txt build/requirements.txt

# Install dependencies
echo "📦 Installing Python dependencies..."
cd build

# Use pip with specific options for Lambda - try multiple approaches
echo "🔧 Attempting platform-specific installation..."
pip install -r requirements.txt -t . --platform linux_x86_64 --only-binary=all --upgrade --no-deps || {
    echo "⚠️  Platform-specific install failed, trying generic install..."
    pip install -r requirements.txt -t . --upgrade
}

# Remove unnecessary files to reduce size
echo "🧹 Optimizing package size..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "test" -exec rm -rf {} + 2>/dev/null || true
find . -name "*test*.py" -delete 2>/dev/null || true

# Remove large unnecessary files from packages
echo "🗜️  Removing unnecessary package files..."
rm -rf pandas/tests/ 2>/dev/null || true
rm -rf numpy/tests/ 2>/dev/null || true
rm -rf scipy/tests/ 2>/dev/null || true
rm -rf plotly/tests/ 2>/dev/null || true
rm -rf plotly/datasets/ 2>/dev/null || true
rm -rf */tests/ 2>/dev/null || true
rm -rf */test/ 2>/dev/null || true

# Create ZIP file
echo "📦 Creating deployment package..."
zip -r ../api.zip . -x "*.DS_Store" "*.git*" > /dev/null

cd ..

# Get package size
SIZE=$(ls -lh api.zip | awk '{print $5}')
SIZE_BYTES=$(ls -l api.zip | awk '{print $5}')
SIZE_MB=$((SIZE_BYTES / 1024 / 1024))

echo -e "${GREEN}📦 Package created: api.zip (${SIZE})${NC}"

# Check if package is too large (Lambda limit is 250MB)
if [ $SIZE_MB -gt 200 ]; then
    echo -e "${YELLOW}⚠️  Warning: Package size is ${SIZE_MB}MB. Consider optimizing if deployment fails.${NC}"
fi

print_header "Deploying Infrastructure with Terraform"

# Deploy with Terraform
cd terraform

# Initialize Terraform if not already done
if [ ! -d ".terraform" ]; then
    echo "🔧 Initializing Terraform..."
    terraform init
fi

# Plan deployment
echo "📋 Planning Terraform deployment..."
terraform plan -out=tfplan

# Apply deployment
echo -e "${YELLOW}⚡ Applying Terraform configuration...${NC}"
terraform apply tfplan

# Get outputs
echo "📝 Getting deployment information..."
API_URL=$(terraform output -raw api_gateway_url 2>/dev/null || echo "Not available")
S3_BUCKET=$(terraform output -raw s3_bucket_name 2>/dev/null || echo "Not available")
CLOUDFRONT_URL=$(terraform output -raw cloudfront_url 2>/dev/null || echo "Not available")

print_header "Building and Deploying Frontend"

# Build and deploy frontend
cd ../frontend

# Check if node_modules exists, install if not
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "🏗️  Building frontend..."
npm run build

# Upload to S3
if [ "$S3_BUCKET" != "Not available" ]; then
    echo "🌐 Uploading frontend to S3..."
    aws s3 sync build/ s3://${S3_BUCKET}/ --delete
    echo -e "${GREEN}✅ Frontend deployed to S3${NC}"
else
    echo -e "${RED}❌ Could not deploy frontend - S3 bucket not available${NC}"
fi

print_header "Deployment Summary"

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${GREEN}📡 API Endpoint:${NC} ${API_URL}"
echo -e "${GREEN}🌍 Frontend URL:${NC} https://${CLOUDFRONT_URL}"
echo -e "${GREEN}🪣 S3 Bucket:${NC} ${S3_BUCKET}"
echo ""
echo -e "${BLUE}📊 Test your API:${NC}"
echo "curl ${API_URL}/health"
echo ""
echo -e "${BLUE}🔍 Monitor your application:${NC}"
echo "- AWS Lambda Console: https://console.aws.amazon.com/lambda/"
echo "- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/"
echo "- S3 Console: https://console.aws.amazon.com/s3/"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "1. Test your API endpoints"
echo "2. Monitor CloudWatch logs for any issues"
echo "3. Update your frontend to use the new API URL"
echo ""
echo -e "${GREEN}✅ Deployment completed!${NC}"
