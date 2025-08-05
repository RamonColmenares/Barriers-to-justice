#!/bin/bash

# Script to clean up the testing infrastructure
# This script destroys the testing environment to save costs

set -e

echo "🧹 Cleaning up TESTING environment..."
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "terraform-testing" ]; then
    echo -e "${RED}❌ Error: terraform-testing directory not found.${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will destroy the entire testing infrastructure!${NC}"
echo -e "${YELLOW}⚠️  All data and applications running on the testing instance will be lost.${NC}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${BLUE}ℹ️  Operation cancelled.${NC}"
    exit 0
fi

echo -e "${BLUE}🏗️  Destroying testing infrastructure...${NC}"

cd terraform-testing

# Get the S3 bucket name before destroying (for cleaning)
S3_BUCKET=$(terraform output -raw s3_bucket_name 2>/dev/null || echo "")

# Clean S3 bucket if it exists
if [ ! -z "$S3_BUCKET" ] && [ "$S3_BUCKET" != "null" ]; then
    echo -e "${BLUE}🗑️  Emptying S3 bucket: $S3_BUCKET${NC}"
    aws s3 rm s3://$S3_BUCKET --recursive 2>/dev/null || true
    echo -e "${GREEN}✅ S3 bucket emptied${NC}"
fi

# Get the instance IP before destroying (for logging)
INSTANCE_IP=$(terraform output -raw ec2_public_ip 2>/dev/null || echo "unknown")

# Destroy the infrastructure
terraform destroy -auto-approve

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Testing infrastructure destroyed successfully!${NC}"
    echo -e "${BLUE}ℹ️  Instance ${INSTANCE_IP} has been terminated.${NC}"
else
    echo -e "${RED}❌ Failed to destroy infrastructure. Please check Terraform state.${NC}"
    exit 1
fi

cd ..

# Clean up local Docker images
echo -e "${BLUE}🐳 Cleaning up local Docker images...${NC}"
docker rmi juvenile-api-testing:latest 2>/dev/null || true

echo ""
echo "======================================"
echo -e "${GREEN}🎉 CLEANUP COMPLETED SUCCESSFULLY!${NC}"
echo "======================================"
echo -e "${BLUE}💰 Testing infrastructure has been destroyed to save costs.${NC}"
echo -e "${YELLOW}ℹ️  You can redeploy anytime using ./deploy-testing.sh${NC}"
