# AWS Deployment Guide

This guide will help you deploy your juvenile immigration data analysis application to AWS using Terraform.

## Prerequisites

### 1. Install Required Tools

**On macOS:**
```bash
# Install AWS CLI
brew install awscli

# Install Terraform
brew install terraform

# Install Python 3.11+ (if not already installed)
brew install python@3.11
```

**On Linux:**
```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### 2. Configure AWS Credentials

Create an AWS account (free tier) and configure your credentials:

```bash
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (recommend: `us-east-1`)
- Default output format: `json`

### 3. Verify Setup

```bash
# Check AWS connection
aws sts get-caller-identity

# Check Terraform
terraform version
```

## Deployment Steps

### 1. Setup Local Environment

```bash
# Make setup script executable and run it
chmod +x setup-local.sh
./setup-local.sh
```

### 2. Deploy to AWS

```bash
# Deploy everything to AWS
./deploy-aws.sh
```

This script will:
- Package your Python API for Lambda
- Create AWS infrastructure with Terraform
- Deploy your API to Lambda
- Build and deploy your frontend to S3
- Set up CloudFront for global distribution

### 3. Access Your Application

After deployment, you'll get:
- **API URL**: Your Lambda function endpoint
- **Frontend URL**: Your CloudFront distribution URL

## Architecture

Your AWS deployment includes:

1. **AWS Lambda**: Hosts your Python Flask API
   - Runtime: Python 3.11
   - Memory: 512MB (adjustable up to 10GB)
   - Timeout: 30 seconds (adjustable up to 15 minutes)

2. **API Gateway**: REST API endpoint for your Lambda function

3. **S3 Bucket**: Static website hosting for your Svelte frontend

4. **CloudFront**: CDN for global content delivery

5. **IAM Roles**: Secure permissions for Lambda execution

## Cost Estimation (AWS Free Tier)

- **Lambda**: 1M requests/month + 400GB-seconds compute - FREE
- **API Gateway**: 1M API calls/month - FREE  
- **S3**: 5GB storage + 20K GET requests - FREE
- **CloudFront**: 50GB data transfer + 2M requests - FREE

**After free tier**: ~$5-15/month for typical usage

## Monitoring

Access AWS CloudWatch for:
- Lambda function logs
- API Gateway metrics
- Error monitoring
- Performance analytics

## Updating Your Application

To update after making changes:

```bash
# Update API
./deploy-aws.sh

# Or update just frontend
cd frontend
npm run build
aws s3 sync build/ s3://$(cd ../terraform && terraform output -raw s3_bucket_name)/ --delete
```

## Cleanup

To destroy all AWS resources:

```bash
cd terraform
terraform destroy
```

## Troubleshooting

### Common Issues:

1. **AWS Credentials**: Ensure `aws configure` is properly set up
2. **Permissions**: Your AWS user needs Lambda, S3, CloudFront, and IAM permissions
3. **Package Size**: If Lambda package is too large, we can optimize dependencies
4. **CORS Issues**: API Gateway handles CORS automatically

### Getting Help:

- Check CloudWatch logs for Lambda errors
- Verify S3 bucket policies for frontend access
- Ensure API Gateway deployment is successful

## Security Notes

- All resources use least-privilege IAM policies
- S3 bucket is configured for static website hosting only
- Lambda functions run in AWS's secure environment
- CloudFront provides DDoS protection
