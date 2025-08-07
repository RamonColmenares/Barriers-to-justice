#!/bin/bash

echo "=== JUVENILE IMMIGRATION API - EC2 DEPLOYMENT ==="
echo "Python 3.13.4 | Docker | EC2 t3.small (2GB RAM)"
echo ""

# Parse command line arguments
CONTACT_EMAIL=""
CUSTOM_DOMAIN=""
API_SUBDOMAIN="api"
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
        --domain|-d)
            CUSTOM_DOMAIN="$2"
            shift 2
            ;;
        --api-subdomain)
            API_SUBDOMAIN="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--email EMAIL] [-e EMAIL] [--domain DOMAIN] [-d DOMAIN] [--api-subdomain SUBDOMAIN]"
            echo ""
            echo "Options:"
            echo "  --email, -e EMAIL         Contact email for SES and Let's Encrypt certificates"
            echo "  --domain, -d DOMAIN       Custom domain for the application (e.g., barrierstojustice.me)"
            echo "  --api-subdomain SUBDOMAIN API subdomain (default: api, creates api.yourdomain.com)"
            echo "  --help, -h                Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --email contact@yourdomain.com"
            echo "  $0 -e contact@yourdomain.com --domain barrierstojustice.me"
            echo "  $0 --domain barrierstojustice.me --api-subdomain backend"
            echo ""
            echo "SES Domain Configuration:"
            echo "  When --domain is provided, Terraform will automatically:"
            echo "  • Create SES domain identity for your domain"
            echo "  • Configure DKIM authentication (3 CNAME records)"
            echo "  • Add SPF record (v=spf1 include:amazonses.com ~all)"
            echo "  • Add DMARC record for enhanced deliverability"
            echo "  • Use contact@yourdomain.com as sender email"
            echo ""
            echo "Prerequisites for domain setup:"
            echo "  • Domain must be hosted in Route 53 (delegated nameservers)"
            echo "  • AWS credentials must have Route 53 and SES permissions"
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

# Use verified SES email as default if no email provided
if [ -z "$CONTACT_EMAIL" ]; then
    echo "📧 No contact email provided. Checking for verified SES emails..."
    
    # Try to get verified emails from SES
    VERIFIED_EMAILS=$(aws ses list-identities --region us-east-1 --output text --query 'Identities' 2>/dev/null || echo "")
    
    if echo "$VERIFIED_EMAILS" | grep -q "ramon.colmenaresblanco@gmail.com"; then
        CONTACT_EMAIL="ramon.colmenaresblanco@gmail.com"
        echo "✓ Using verified SES email: $CONTACT_EMAIL"
    else
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

# Prepare Terraform variables (safe array)
TF_ARGS=(-var "contact_email=$CONTACT_EMAIL")
if [ -n "$CUSTOM_DOMAIN" ]; then
  TF_ARGS+=(-var "custom_domain=$CUSTOM_DOMAIN" -var "api_subdomain=$API_SUBDOMAIN")
fi

echo "📋 Terraform plan with variables: ${TF_ARGS[*]}"
terraform plan "${TF_ARGS[@]}"

echo "🏗️  Applying Terraform configuration..."
terraform apply -auto-approve "${TF_ARGS[@]}"

# Get outputs
EC2_IP=$(terraform output -raw ec2_public_ip 2>/dev/null)
S3_BUCKET=$(terraform output -raw s3_bucket_name 2>/dev/null)
CLOUDFRONT_URL=$(terraform output -raw cloudfront_url 2>/dev/null)
SES_DOMAIN_IDENTITY=$(terraform output -raw ses_domain_identity 2>/dev/null)

if [ -z "$EC2_IP" ]; then
    echo "❌ Failed to get EC2 IP from Terraform"
    exit 1
fi

# Compute sslip.io hostname for the current public IP
HOSTNAME_SSLIP="$(echo "$EC2_IP" | tr '.' '-')".sslip.io

# Determine hosts based on custom domain (if provided)
if [ -n "$CUSTOM_DOMAIN" ]; then
    API_HOST="${API_SUBDOMAIN}.${CUSTOM_DOMAIN}"
    FRONTEND_ORIGIN="https://${CUSTOM_DOMAIN}"
else
    API_HOST="$HOSTNAME_SSLIP"
    FRONTEND_ORIGIN="https://${HOSTNAME_SSLIP}"
fi

echo "✓ Infrastructure deployed"
echo "  EC2 Instance IP: $EC2_IP"
echo "  S3 Bucket: $S3_BUCKET"
echo "  Hostname: $HOSTNAME_SSLIP"
if [ -n "$CUSTOM_DOMAIN" ]; then
    echo "  Domain: $CUSTOM_DOMAIN"
    echo "  API Subdomain: $API_SUBDOMAIN (API Host: $API_HOST)"
fi

echo "  API Host: $API_HOST"
echo "  Frontend Origin: $FRONTEND_ORIGIN"

# Decide sender email for API (SES): prefer contact@<domain> if SES domain identity is configured
SENDER_EMAIL="$CONTACT_EMAIL"
if [ -n "$SES_DOMAIN_IDENTITY" ] && [ "$SES_DOMAIN_IDENTITY" != "" ]; then
    SENDER_EMAIL="contact@$SES_DOMAIN_IDENTITY"
    echo "✅ Using SES domain identity sender email: $SENDER_EMAIL"
elif [ -n "$CUSTOM_DOMAIN" ]; then
    # Fallback check via AWS CLI for backwards compatibility
    if aws sesv2 get-email-identity --region us-east-1 --email-identity "$CUSTOM_DOMAIN" >/dev/null 2>&1; then
        SENDER_EMAIL="contact@$CUSTOM_DOMAIN"
        echo "✅ Using existing SES domain identity: $SENDER_EMAIL"
    else
        echo "ℹ️  SES domain identity for $CUSTOM_DOMAIN not found; using contact email: $CONTACT_EMAIL"
    fi
else
    echo "ℹ️  No custom domain provided; using contact email: $CONTACT_EMAIL"
fi

# === Domain automation (Route 53, ACM, CloudFront) ===

# Tools we need locally
if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq is required (for JSON edits). Install with: brew install jq (macOS) or sudo apt-get install jq (Linux)"
  exit 1
fi

if [ -n "$CUSTOM_DOMAIN" ]; then
  printf "\n=== DOMAIN SETUP FOR $CUSTOM_DOMAIN ===\n"
  HZ_ID=$(aws route53 list-hosted-zones-by-name --dns-name "$CUSTOM_DOMAIN" \
    --query 'HostedZones[0].Id' --output text 2>/dev/null | sed 's|/hostedzone/||')
  if [ -z "$HZ_ID" ] || [ "$HZ_ID" = "None" ]; then
    echo "❌ Could not find Route 53 hosted zone for $CUSTOM_DOMAIN. Make sure DNS is delegated to Route 53."
    exit 1
  fi

  echo "📝 Creating/Updating A record: ${API_HOST} → ${EC2_IP}"
  cat > /tmp/route53-upsert-api.json <<EOF_API_RR
  {
    "Comment": "api A record",
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "${API_HOST}",
        "Type": "A",
        "TTL": 60,
        "ResourceRecords": [{ "Value": "${EC2_IP}" }]
      }
    }]
  }
EOF_API_RR
  aws route53 change-resource-record-sets --hosted-zone-id "$HZ_ID" \
    --change-batch file:///tmp/route53-upsert-api.json >/dev/null && \
    echo "✓ Route 53 A record set for ${API_HOST}"

  if [ -n "$CLOUDFRONT_URL" ] && [ "$CLOUDFRONT_URL" != "null" ]; then
    printf "\n=== ACM (us-east-1) & CloudFront Aliases for $CUSTOM_DOMAIN ===\n"

    # 4a) Find or request ACM cert in us-east-1 for apex + www
    CERT_ARN=$(aws acm list-certificates --region us-east-1 \
      --query "CertificateSummaryList[?DomainName=='$CUSTOM_DOMAIN'].CertificateArn | [0]" --output text 2>/dev/null)

    if [ -z "$CERT_ARN" ] || [ "$CERT_ARN" = "None" ]; then
      echo "📜 Requesting new ACM certificate for $CUSTOM_DOMAIN and www.$CUSTOM_DOMAIN (DNS validation)"
      CERT_ARN=$(aws acm request-certificate --region us-east-1 \
        --domain-name "$CUSTOM_DOMAIN" \
        --subject-alternative-names "www.$CUSTOM_DOMAIN" \
        --validation-method DNS \
        --query CertificateArn --output text)

      # Poll hasta que ACM devuelva los ResourceRecord
      echo "🔧 Creating DNS validation CNAMEs in Route 53..."
      ATTEMPTS=20
      SLEEP=5
      while :; do
        aws acm describe-certificate --region us-east-1 --certificate-arn "$CERT_ARN" \
          --query 'Certificate.DomainValidationOptions[].ResourceRecord' --output json \
          > /tmp/acm-dvo.json || true
        if jq -e 'length > 0 and .[0].Name and .[0].Value' /tmp/acm-dvo.json >/dev/null 2>&1; then
          break
        fi
        if [ $ATTEMPTS -le 0 ]; then
          echo "⚠️  ACM no entregó ResourceRecords todavía; continuaré sin crearlos automáticamente."
          break
        fi
        echo "   ... esperando ResourceRecords de ACM ($ATTEMPTS intentos restantes)"
        ATTEMPTS=$((ATTEMPTS-1))
        sleep $SLEEP
      done

      # Crear CNAMEs (tolerante si vienen vacíos)
      jq -r '.[]? | select(.Name and .Type and .Value) | [.Name, .Type, .Value] | @tsv' /tmp/acm-dvo.json \
      | while IFS=$'\t' read -r RR_NAME RR_TYPE RR_VALUE; do
        cat > /tmp/route53-acm-cname.json <<EOF_ACM_RR
{
  "Comment": "ACM DNS validation record",
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "${RR_NAME}",
      "Type": "${RR_TYPE}",
      "TTL": 300,
      "ResourceRecords": [{ "Value": "\"${RR_VALUE}\"" }]
    }
  }]
}
EOF_ACM_RR
        aws route53 change-resource-record-sets --hosted-zone-id "$HZ_ID" \
          --change-batch file:///tmp/route53-acm-cname.json >/dev/null || true
      done

      echo "⏳ Waiting for ACM certificate to be ISSUED..."
      aws acm wait certificate-validated --region us-east-1 --certificate-arn "$CERT_ARN" || {
        echo "⚠️  ACM validation not complete yet; CloudFront will pick it up once Issued."
      }
    else
      echo "✓ Reusing existing ACM certificate: $CERT_ARN"
    fi

    # 4b) Update CloudFront distribution to attach aliases and cert
    DISTRIBUTION_ID=$(aws cloudfront list-distributions \
      --query "DistributionList.Items[?DomainName=='$CLOUDFRONT_URL'].Id | [0]" \
      --output text)

    if [ -n "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
      echo "🔄 Updating CloudFront distribution $DISTRIBUTION_ID with aliases and ACM cert..."
      CF_ETAG=$(aws cloudfront get-distribution-config --id "$DISTRIBUTION_ID" --query ETag --output text)
      aws cloudfront get-distribution-config --id "$DISTRIBUTION_ID" --query DistributionConfig --output json \
        > /tmp/cf-config.json

      # Set Aliases and ViewerCertificate
      jq --arg apex "$CUSTOM_DOMAIN" --arg www "www.$CUSTOM_DOMAIN" --arg cert "$CERT_ARN" '.Aliases = {Quantity: 2, Items: [$apex, $www]} | .ViewerCertificate = {ACMCertificateArn:$cert, SSLSupportMethod:"sni-only", MinimumProtocolVersion:"TLSv1.2_2021", Certificate:$cert, CertificateSource:"acm"}' /tmp/cf-config.json > /tmp/cf-config-updated.json

      aws cloudfront update-distribution --id "$DISTRIBUTION_ID" \
        --if-match "$CF_ETAG" \
        --distribution-config file:///tmp/cf-config-updated.json >/dev/null && \
        echo "✓ CloudFront distribution updated"

      # 4c) Create Route 53 A (Alias) for apex and www → CloudFront
      # CloudFront hosted zone ID is a global constant
      CF_ZONE_ID="Z2FDTNDATAQYW2"
      echo "📝 Creating/Updating Route 53 Alias records for apex and www..."
      cat > /tmp/route53-alias-apex.json <<EOF_ALIAS_APEX
      {
        "Comment": "Apex alias to CloudFront",
        "Changes": [{
          "Action": "UPSERT",
          "ResourceRecordSet": {
            "Name": "$CUSTOM_DOMAIN",
            "Type": "A",
            "AliasTarget": {
              "HostedZoneId": "$CF_ZONE_ID",
              "DNSName": "$CLOUDFRONT_URL",
              "EvaluateTargetHealth": false
            }
          }
        }]
      }
EOF_ALIAS_APEX
      aws route53 change-resource-record-sets --hosted-zone-id "$HZ_ID" \
        --change-batch file:///tmp/route53-alias-apex.json >/dev/null && \
        echo "✓ Apex alias set"

      cat > /tmp/route53-alias-www.json <<EOF_ALIAS_WWW
      {
        "Comment": "WWW alias to CloudFront",
        "Changes": [{
          "Action": "UPSERT",
          "ResourceRecordSet": {
            "Name": "www.$CUSTOM_DOMAIN",
            "Type": "A",
            "AliasTarget": {
              "HostedZoneId": "$CF_ZONE_ID",
              "DNSName": "$CLOUDFRONT_URL",
              "EvaluateTargetHealth": false
            }
          }
        }]
      }
EOF_ALIAS_WWW
      aws route53 change-resource-record-sets --hosted-zone-id "$HZ_ID" \
        --change-batch file:///tmp/route53-alias-www.json >/dev/null && \
        echo "✓ WWW alias set"
    else
      echo "⚠️  Could not find CloudFront distribution for $CLOUDFRONT_URL; skipping alias setup"
    fi
  fi

  echo "✓ Domain setup stage completed"
fi

# Build and deploy frontend
echo "🎨 Building and deploying frontend..."
cd ../frontend
echo "PUBLIC_API_URL=https://${API_HOST}/api" > .env.production

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

# Copy AWS credentials to EC2 for email service
echo "🔑 Copying AWS credentials for email service..."
scp -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 \
    -r ~/.aws ubuntu@$EC2_IP:~/ 2>/dev/null || {
    echo "❌ Failed to copy AWS credentials"
    exit 1
}

echo "✓ Files and credentials copied to EC2"

# Deploy application on EC2
echo "🐳 Building and running Docker container..."
ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=30 ubuntu@$EC2_IP "export CONTACT_EMAIL='$CONTACT_EMAIL'; export SENDER_EMAIL='$SENDER_EMAIL'; export EC2_IP='$EC2_IP'; export HOSTNAME_SSLIP='$HOSTNAME_SSLIP'; export CLOUDFRONT_URL='$CLOUDFRONT_URL'; export CUSTOM_DOMAIN='$CUSTOM_DOMAIN'; export API_HOST='$API_HOST'; bash -s" << 'EOF'
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
sudo apt-get install -y htop iotop sysstat bc

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

# Determine sender email (prefer domain identity if provided from local step)
VERIFIED_EMAIL="${SENDER_EMAIL:-$CONTACT_EMAIL}"
echo "✉️  Using sender email: $VERIFIED_EMAIL"

sudo docker run -d \
  --name juvenile-api \
  -p 5000:5000 \
  --memory="1500m" --memory-swap="1500m" --cpus="1.0" \
  --oom-kill-disable=false \
  --restart unless-stopped \
  -e CONTACT_EMAIL="$VERIFIED_EMAIL" \
  -e ENABLE_BACKEND_CORS="0" \
  -e HOSTNAME_SSLIP="$HOSTNAME_SSLIP" \
  -e CLOUDFRONT_URL="$CLOUDFRONT_URL" \
  -e AWS_DEFAULT_REGION="us-east-1" \
  -v /home/ubuntu/.aws:/root/.aws:ro \
  --shm-size=128m \
  --ulimit nofile=65536:65536 \
  juvenile-immigration-api

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
            sudo sh -c 'echo 1 > /proc/sys/vm/drop_caches' 2>/dev/null || true
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
            sudo sh -c 'echo 1 > /proc/sys/vm/drop_caches' 2>/dev/null || true
            sudo sh -c 'echo 2 > /proc/sys/vm/drop_caches' 2>/dev/null || true
            sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' 2>/dev/null || true
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
map \$http_origin \$cors_origin {
    default "";
    "https://${API_HOST}" \$http_origin;
    "https://${CUSTOM_DOMAIN}" \$http_origin;
    "https://www.${CUSTOM_DOMAIN}" \$http_origin;
    "https://${CLOUDFRONT_URL}" \$http_origin;
    "http://localhost" \$http_origin;
    ~^http://localhost(:[0-9]+)?\$ \$http_origin;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _ ${API_HOST};

    # Timeouts and buffers
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
    proxy_buffering off;
    proxy_buffer_size 64k;
    proxy_buffers 8 64k;
    proxy_busy_buffers_size 128k;


    # API routes with CORS headers on success and error
    location /api/ {
        # Handle CORS preflight for /api/
        if (\$request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin \$cors_origin always;
            add_header Vary Origin always;
            add_header Access-Control-Allow-Credentials true always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers \$http_access_control_request_headers always;
            add_header Access-Control-Max-Age 86400 always;
            return 204;
        }
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        add_header Access-Control-Allow-Origin \$cors_origin always;
        add_header Vary Origin always;
        add_header Access-Control-Allow-Credentials true always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    }

    # Health check
    location /health {
        # Handle CORS preflight for /health
        if (\$request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin \$cors_origin always;
            add_header Vary Origin always;
            add_header Access-Control-Allow-Credentials true always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers \$http_access_control_request_headers always;
            add_header Access-Control-Max-Age 86400 always;
            return 204;
        }
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        add_header Access-Control-Allow-Origin \$cors_origin always;
        add_header Vary Origin always;
        add_header Access-Control-Allow-Credentials true always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    }

    # Default catch-all
    location / {
        # Handle CORS preflight for /
        if (\$request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin \$cors_origin always;
            add_header Vary Origin always;
            add_header Access-Control-Allow-Credentials true always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers \$http_access_control_request_headers always;
            add_header Access-Control-Max-Age 86400 always;
            return 204;
        }
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        add_header Access-Control-Allow-Origin \$cors_origin always;
        add_header Vary Origin always;
        add_header Access-Control-Allow-Credentials true always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    }

    # Return JSON with CORS when upstream errors occur
    error_page 502 504 = @err_json;
    location @err_json {
        default_type application/json;
        add_header Access-Control-Allow-Origin \$cors_origin always;
        add_header Vary Origin always;
        add_header Access-Control-Allow-Credentials true always;
        return 502 '{"error":"bad_gateway"}';
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
if curl -fsS "http://$API_HOST/health" >/dev/null; then
    echo "✓ HTTP (80) proxy reachable"
else
    echo "⚠️  HTTP (80) proxy not reachable at http://$API_HOST/health"
    echo "Checking nginx status..."
    sudo systemctl status nginx --no-pager
    exit 1
fi

# Obtain/renew a Let's Encrypt certificate for the sslip.io hostname
echo "🔐 Obtaining SSL certificate..."
CERTBOT_SUCCESS=false
if [ -n "$CONTACT_EMAIL" ]; then
    if sudo certbot --nginx --agree-tos -m "$CONTACT_EMAIL" --no-eff-email --redirect -d "$API_HOST" --non-interactive; then
        CERTBOT_SUCCESS=true
        echo "✓ SSL certificate obtained successfully"
    else
        echo "❌ Failed to obtain SSL certificate with email"
    fi
else
    if sudo certbot --nginx --agree-tos --register-unsafely-without-email --redirect -d "$API_HOST" --non-interactive; then
        CERTBOT_SUCCESS=true
        echo "✓ SSL certificate obtained successfully"
    else
        echo "❌ Failed to obtain SSL certificate without email"
    fi
fi

if [ "$CERTBOT_SUCCESS" = false ]; then
    echo "⚠️  SSL certificate setup failed, but continuing with HTTP only"
    echo "You can manually run: sudo certbot --nginx -d $API_HOST"
fi

echo "✓ Nginx is serving: ${API_HOST}"

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
    echo "🔎 Verifying HTTP/HTTPS on $API_HOST ..."
    
    # First, verify HTTP (port 80) works through Nginx
    if curl -fsS "http://$API_HOST/health" >/dev/null; then
        echo "✓ HTTP health check OK"
    else
        echo "⚠️  HTTP health check failed at http://$API_HOST/health"
    fi

    # Then, test HTTPS if the certificate file exists on the server
    if ssh -i ~/.ssh/juvenile-immigration-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=10 ubuntu@$EC2_IP "sudo test -f /etc/letsencrypt/live/$API_HOST/fullchain.pem"; then
        echo "🔒 Testing HTTPS connectivity..."
        ATTEMPTS=20
        SLEEP=3
        while ! curl -fsS "https://$API_HOST/health" >/dev/null && [ $ATTEMPTS -gt 0 ]; do
            echo "   ... waiting for HTTPS to be ready (attempts left: $ATTEMPTS)"
            sleep $SLEEP
            ATTEMPTS=$((ATTEMPTS-1))
        done

        if curl -fsS "https://$API_HOST/health" >/dev/null; then
            echo "✓ HTTPS health check OK"
            CERTBOT_OK=true
        else
            echo "⚠️  HTTPS health check failed at https://$API_HOST/health"
            echo "You may need to wait a few more minutes for the certificate to propagate"
            CERTBOT_OK=false
        fi

        # Test a key API endpoint as well
        if curl -fsS "https://$API_HOST/api/findings/outcome-percentages" -o /dev/null; then
            echo "✓ Findings endpoint OK"
        else
            echo "⚠️  Findings endpoint check failed at https://$API_HOST/api/findings/outcome-percentages"
        fi
        
        # Test contact form endpoint
        echo "🔍 Testing contact form endpoint..."
        if curl -fsS -X POST "https://$API_HOST/api/contact" \
            -H "Content-Type: application/json" \
            -d '{"firstName":"Deploy","lastName":"Test","email":"test@example.com","message":"Deployment test message"}' \
            -o /dev/null; then
            echo "✓ Contact form endpoint OK"
        else
            echo "⚠️  Contact form endpoint check failed"
        fi
    else
        echo "⚠️  HTTPS not available yet (certificate file not found on server)"
        CERTBOT_OK=false
        echo "📡 Using HTTP endpoints only:"
        echo "   Health Check: http://$API_HOST/health"
        echo "   Overview:     http://$API_HOST/api/overview"
    fi

    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo ""
    
    # Show SES configuration status
    if [ -n "$SES_DOMAIN_IDENTITY" ] && [ "$SES_DOMAIN_IDENTITY" != "" ]; then
        echo "📧 SES Configuration:"
        echo "   ✅ Domain Identity: $SES_DOMAIN_IDENTITY"
        echo "   ✅ DKIM: Configured automatically via Route 53"
        echo "   ✅ SPF Record: Added to DNS"
        echo "   ✅ DMARC Record: Added to DNS"
        echo "   📨 Sender Email: $SENDER_EMAIL"
        echo ""
        echo "   💡 Your domain is ready for email delivery!"
        echo "   💡 Check SES console to request production access if needed"
        echo ""
    elif [ -n "$CUSTOM_DOMAIN" ]; then
        echo "📧 SES Configuration:"
        echo "   ⚠️  Domain identity not automatically configured"
        echo "   📨 Sender Email: $SENDER_EMAIL (fallback to contact email)"
        echo ""
        echo "   💡 To enable domain email (contact@$CUSTOM_DOMAIN):"
        echo "   💡 Check AWS SES console for domain verification status"
        echo ""
    else
        echo "📧 SES Configuration:"
        echo "   📨 Sender Email: $SENDER_EMAIL"
        echo "   💡 Using contact email for outbound messages"
        echo ""
    fi
    
    if [ "$CERTBOT_OK" = true ]; then
        echo "📡 API Endpoints (HTTPS with valid cert):"
        echo "   Health Check: https://$API_HOST/health"
        echo "   Overview:     https://$API_HOST/api/overview"
        echo "   Basic Stats:  https://$API_HOST/api/data/basic-stats"
        echo "   Findings:     https://$API_HOST/api/findings/*"
        echo "   Contact Form: https://$API_HOST/api/contact"
        echo ""
    fi
    
    echo "📡 API Endpoints (HTTP):"
    echo "   Health Check: http://$API_HOST/health"
    echo "   Overview:     http://$API_HOST/api/overview"
    echo "   Basic Stats:  http://$API_HOST/api/data/basic-stats"
    echo "   Findings:     http://$API_HOST/api/findings/*"
    echo "   Contact Form: http://$API_HOST/api/contact"
    echo ""
    echo "📡 API Endpoints (by IP, for debugging):"
    echo "   Health Check: http://$EC2_IP/health"
    echo "   Overview:     http://$EC2_IP/api/overview"
    echo "   Basic Stats:  http://$EC2_IP/api/data/basic-stats"
    echo "   Findings:     http://$EC2_IP/api/findings/*"
    echo "   Contact Form: http://$EC2_IP/api/contact"
    echo ""
    
    if [ "$S3_BUCKET" != "null" ] && [ -n "$S3_BUCKET" ]; then
        echo "🌐 Frontend URLs:"
        echo "   S3 Website:   http://$S3_BUCKET.s3-website-us-east-1.amazonaws.com"
        if [ "$CLOUDFRONT_URL" != "null" ] && [ -n "$CLOUDFRONT_URL" ]; then
            echo "   CloudFront:   https://$CLOUDFRONT_URL"
        fi
        if [ -n "$CUSTOM_DOMAIN" ]; then
            echo "   Custom Domain: https://$CUSTOM_DOMAIN"
        fi
        echo ""
    fi
    
    echo "🔧 Management:"
    echo "   SSH Access:   ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP"
    echo "   Docker Logs:  ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo docker logs juvenile-api'"
    echo "   Restart API:  ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo docker restart juvenile-api'"
    echo "   System Stats: ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'free -h && df -h'"
    echo "   Diagnostics:  ./diagnose-ec2.sh --ip $EC2_IP"
    if [ "$CERTBOT_OK" = false ]; then
        echo "   Setup SSL:    ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo certbot --nginx -d $API_HOST'"
    fi
    echo ""
    echo "📊 Resource Usage Tips:"
    echo "   - Container limited to 1500MB RAM (75% of total)"
    echo "   - 2GB swap configured for stability"
    echo "   - API monitoring runs every 2 minutes"
    echo "   - Auto-restart on container failure"
    echo "   - Nginx timeouts reduced to 120s"
    echo "   - AWS SES email service configured"
    echo "   - AWS credentials mounted as read-only volume"
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
