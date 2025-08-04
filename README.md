# Barriers to Justice - Immigration Research Web Application

MIT Emerging Talent research project analyzing barriers to justice in the U.S. immigration system for juveniles.

## 🚀 Production Deployment (AWS)

### Prerequisites
- AWS CLI configured with credentials
- Terraform installed
- Node.js and npm (for frontend)

### Deploy to AWS
```bash
# Deploy with your contact email for email service
./deploy.sh --email your-email@domain.com

# Or use the short flag
./deploy.sh -e your-email@domain.com
```

This deploys:
- **Backend**: Python 3.13.4 Flask API in Docker on EC2 t2.micro (Free Tier)
- **Frontend**: SvelteKit static site on S3 with CloudFront CDN
- **Email Service**: AWS SES for contact form functionality
- **Infrastructure**: Terraform-managed AWS resources

**Note**: You'll need to verify your email address in AWS SES after deployment to enable contact form emails.

## 🏠 Local Development

### Setup (first time only)
```bash
# Install Python dependencies
cd api && pip install -r requirements.txt

# Install frontend dependencies  
## 🏗️ Architecture

### Production (AWS)
- **Backend**: Python 3.13.4 Flask API in Docker containers on EC2 t2.micro
- **Frontend**: SvelteKit static site hosted on S3 with CloudFront CDN  
- **Database**: CSV files with caching for performance
- **Infrastructure**: Terraform-managed AWS resources (Free Tier eligible)

### API Endpoints
- `GET /health` - Health check
- `GET /api/overview` - Data overview and statistics
- `GET /api/data/basic-stats` - Basic statistical analysis
- `GET /api/findings/time-series` - Time series analysis
- `GET /api/findings/chi-square` - Chi-square analysis results
- `GET /api/findings/outcome-percentages` - Outcome percentage charts
- `GET /api/findings/countries` - Country-based analysis
- `POST /api/contact` - Contact form submission (sends email via AWS SES)

## 📁 Project Structure

```
├── deploy.sh              # AWS deployment script
├── Dockerfile             # Python 3.13.4 container
├── docker-entrypoint.py   # Flask app entry point
├── terraform-ec2/         # AWS infrastructure (Terraform)
│   └── main.tf
├── api/                   # Backend (Flask API)
│   ├── api_routes.py      # API endpoint handlers
│   ├── data_loader.py     # Data loading and caching
│   ├── chart_generator.py # Plotly chart generation
│   ├── data_processor.py  # Data analysis logic
│   └── requirements.txt   # Python dependencies
└── frontend/              # Frontend (SvelteKit)
    ├── src/               # Source code
    └── package.json       # Node dependencies
```

## 🛠️ Management

### Check deployment status
```bash
ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@EC2_IP
docker logs juvenile-api
```

### Restart API
```bash
ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@EC2_IP  
docker restart juvenile-api
```

### Destroy infrastructure
```bash
cd terraform-ec2
terraform destroy -auto-approve
```

## 💰 Cost Optimization
- EC2 t2.micro: Free for 12 months (750 hours/month)
- S3 hosting: Pay per use (minimal for static sites)
- CloudFront CDN: 50GB/month free tier
- Total estimated cost: $0/month for first year

## 🔒 Security
- SSH key auto-generated and secured
- CORS configured for frontend access
- Security groups allow only necessary ports
- Private keys excluded from git
├── setup-local.sh        # Setup script
└── run-local.sh          # Development server script
```

## 🔍 API Endpoints

- `GET /api/health` - Health check
- `GET /api/overview` - Immigration data overview

## 👥 Team

MIT Emerging Talent students researching barriers to justice in immigration.

## 📊 Data

This application analyzes juvenile immigration case data to identify patterns and barriers in legal representation and case outcomes.

## 🔧 Technology Stack

- **Frontend:** SvelteKit, TailwindCSS
- **Backend:** Flask, Python
- **Data:** Pandas, NumPy, Plotly
- **Deployment:** Vercel
