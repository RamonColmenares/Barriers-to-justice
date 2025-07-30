#!/bin/bash

# Quick deployment steps for AWS
echo "🚀 Quick AWS Deployment Steps"
echo "================================"
echo ""

echo "1️⃣  Install prerequisites:"
echo "   macOS: brew install awscli terraform"
echo "   Linux: See AWS_DEPLOYMENT.md"
echo ""

echo "2️⃣  Configure AWS:"
echo "   aws configure"
echo "   (Enter your AWS Access Key, Secret, Region: us-east-1)"
echo ""

echo "3️⃣  Setup local environment:"
echo "   ./setup-local.sh"
echo ""

echo "4️⃣  Deploy to AWS:"
echo "   ./deploy-aws.sh"
echo ""

echo "✅ That's it! Your app will be live on AWS."
echo ""
echo "📖 For detailed instructions, see: AWS_DEPLOYMENT.md"
