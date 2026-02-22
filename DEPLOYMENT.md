# MindCare AI - Production Deployment Guide

## Overview

This guide covers deploying MindCare AI to production using AWS services.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  AWS Cloud                      │
│                                                 │
│  ┌──────────────┐       ┌─────────────────┐   │
│  │   Route 53   │──────>│  CloudFront CDN │   │
│  │  (DNS)       │       │  + S3 (Frontend)│   │
│  └──────────────┘       └─────────────────┘   │
│                                  │              │
│                                  ▼              │
│  ┌──────────────────────────────────────────┐ │
│  │        Application Load Balancer          │ │
│  └──────────────────────────────────────────┘ │
│                     │                          │
│                     ▼                          │
│  ┌──────────────────────────────────────────┐ │
│  │         AWS App Runner                    │ │
│  │       (FastAPI Backend)                   │ │
│  └──────────────────────────────────────────┘ │
│                     │                          │
│         ┌───────────┴───────────┐             │
│         ▼                       ▼             │
│  ┌─────────────┐         ┌──────────────┐    │
│  │  Amazon RDS │         │  Amazon S3   │    │
│  │ (PostgreSQL)│         │ (Documents)  │    │
│  └─────────────┘         └──────────────┘    │
└─────────────────────────────────────────────────┘
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Docker installed locally
- Domain name (optional but recommended)

## Step 1: Database Setup (Amazon RDS)

### Create RDS PostgreSQL Instance

```bash
# Via AWS CLI
aws rds create-db-instance \
    --db-instance-identifier mindcare-db \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --engine-version 14.7 \
    --master-username mindcare_admin \
    --master-user-password YOUR_SECURE_PASSWORD \
    --allocated-storage 100 \
    --storage-type gp3 \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name mindcare-subnet-group \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "mon:04:00-mon:05:00" \
    --storage-encrypted \
    --enable-cloudwatch-logs-exports '["postgresql"]' \
    --deletion-protection
```

### Initialize Database Schema

```bash
# Connect to RDS instance
psql -h mindcare-db.xxxxxxxxx.us-west-2.rds.amazonaws.com \
     -U mindcare_admin \
     -d postgres

# Create database and schema
CREATE DATABASE mindcare_production;
\c mindcare_production
\i database/schema.sql
```

## Step 2: S3 Bucket for Document Storage

```bash
# Create S3 bucket
aws s3 mb s3://mindcare-documents-prod --region us-west-2

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket mindcare-documents-prod \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

# Block public access
aws s3api put-public-access-block \
    --bucket mindcare-documents-prod \
    --public-access-block-configuration \
        BlockPublicAcls=true,\
        IgnorePublicAcls=true,\
        BlockPublicPolicy=true,\
        RestrictPublicBuckets=true

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket mindcare-documents-prod \
    --versioning-configuration Status=Enabled
```

## Step 3: Backend Deployment (AWS App Runner)

### Build and Push Docker Image

```bash
# Authenticate to ECR
aws ecr get-login-password --region us-west-2 | \
    docker login --username AWS --password-stdin \
    ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com

# Create ECR repository
aws ecr create-repository \
    --repository-name mindcare-backend \
    --region us-west-2

# Build and tag image
cd backend
docker build -t mindcare-backend:latest .
docker tag mindcare-backend:latest \
    ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/mindcare-backend:latest

# Push to ECR
docker push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/mindcare-backend:latest
```

### Create App Runner Service

```bash
# Create apprunner.yaml configuration
cat > apprunner.yaml << EOF
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000
  network:
    port: 8000
    env: APP_PORT
  env:
    - name: DATABASE_URL
      value: "postgresql://mindcare_admin:PASSWORD@mindcare-db.xxx.rds.amazonaws.com:5432/mindcare_production"
    - name: ANTHROPIC_API_KEY
      value: "your-api-key"
    - name: ENVIRONMENT
      value: "production"
    - name: SECRET_KEY
      value: "your-production-secret-key"
EOF

# Create service via Console or CLI
aws apprunner create-service \
    --service-name mindcare-backend \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/mindcare-backend:latest",
            "ImageRepositoryType": "ECR"
        },
        "AutoDeploymentsEnabled": true
    }' \
    --instance-configuration '{
        "Cpu": "1 vCPU",
        "Memory": "2 GB"
    }' \
    --health-check-configuration '{
        "Protocol": "HTTP",
        "Path": "/health",
        "Interval": 10,
        "Timeout": 5,
        "HealthyThreshold": 1,
        "UnhealthyThreshold": 5
    }'
```

## Step 4: Frontend Deployment (S3 + CloudFront)

### Build Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
VITE_API_URL=https://your-backend-url.amazonaws.com npm run build
```

### Deploy to S3

```bash
# Create S3 bucket for frontend
aws s3 mb s3://mindcare-frontend-prod --region us-west-2

# Upload build files
aws s3 sync dist/ s3://mindcare-frontend-prod/ \
    --delete \
    --cache-control "public, max-age=31536000"

# Configure bucket for static website hosting
aws s3 website s3://mindcare-frontend-prod/ \
    --index-document index.html \
    --error-document index.html
```

### Create CloudFront Distribution

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
    --origin-domain-name mindcare-frontend-prod.s3.amazonaws.com \
    --default-root-object index.html \
    --comment "MindCare AI Frontend"
```

## Step 5: Configure Domain and SSL

### Request SSL Certificate (ACM)

```bash
# Request certificate in us-east-1 for CloudFront
aws acm request-certificate \
    --domain-name mindcare-ai.com \
    --subject-alternative-names "*.mindcare-ai.com" \
    --validation-method DNS \
    --region us-east-1
```

### Configure Route 53

```bash
# Create hosted zone (if not exists)
aws route53 create-hosted-zone \
    --name mindcare-ai.com \
    --caller-reference $(date +%s)

# Add DNS records for CloudFront
# (Use AWS Console or create-record-set)
```

## Step 6: Security Configuration

### Enable WAF (Web Application Firewall)

```bash
# Create Web ACL
aws wafv2 create-web-acl \
    --name mindcare-waf \
    --scope CLOUDFRONT \
    --default-action Block={} \
    --rules file://waf-rules.json \
    --region us-east-1

# Associate with CloudFront
aws cloudfront update-distribution \
    --id DISTRIBUTION_ID \
    --web-acl-id WAF_ACL_ID
```

### Configure Secrets Manager

```bash
# Store sensitive credentials
aws secretsmanager create-secret \
    --name mindcare/production/api-keys \
    --secret-string '{
        "anthropic_api_key": "your-key",
        "database_password": "your-password",
        "secret_key": "your-secret"
    }' \
    --region us-west-2
```

## Step 7: Monitoring and Logging

### CloudWatch Setup

```bash
# Create log group
aws logs create-log-group \
    --log-group-name /aws/apprunner/mindcare-backend

# Create dashboard
aws cloudwatch put-dashboard \
    --dashboard-name MindCare-Metrics \
    --dashboard-body file://cloudwatch-dashboard.json
```

### Set Up Alarms

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
    --alarm-name mindcare-high-error-rate \
    --alarm-description "Alert on high 5xx errors" \
    --metric-name 5xxError \
    --namespace AWS/AppRunner \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions arn:aws:sns:us-west-2:ACCOUNT_ID:alerts
```

## Step 8: Backup and Disaster Recovery

### Automated RDS Snapshots

```bash
# Configure automated backups (already set in RDS creation)
# Create manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier mindcare-db \
    --db-snapshot-identifier mindcare-db-snapshot-$(date +%Y%m%d)
```

### S3 Cross-Region Replication

```bash
# Enable replication
aws s3api put-bucket-replication \
    --bucket mindcare-documents-prod \
    --replication-configuration file://replication-config.json
```

## Step 9: HIPAA Compliance Checklist

- [ ] Sign BAA (Business Associate Agreement) with AWS
- [ ] Enable encryption at rest for all data stores
- [ ] Enable encryption in transit (TLS/HTTPS)
- [ ] Configure VPC with private subnets
- [ ] Enable CloudTrail for audit logging
- [ ] Implement MFA for all admin access
- [ ] Regular security assessments and penetration testing
- [ ] Data retention and deletion policies
- [ ] Incident response plan
- [ ] Staff training on HIPAA requirements

## Step 10: CI/CD Pipeline (Optional)

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      
      - name: Build and push Docker image
        run: |
          docker build -t mindcare-backend ./backend
          docker tag mindcare-backend:latest $ECR_REGISTRY/mindcare-backend:latest
          docker push $ECR_REGISTRY/mindcare-backend:latest
```

## Cost Estimation (Monthly)

- RDS PostgreSQL (db.t3.medium): ~$70
- App Runner (1 vCPU, 2GB): ~$50
- S3 + CloudFront: ~$10-20
- Data Transfer: ~$20-50
- CloudWatch + Logs: ~$10
- **Total: ~$160-200/month**

## Scaling Considerations

- **Horizontal Scaling**: App Runner auto-scaling
- **Database**: Read replicas for read-heavy workloads
- **Caching**: Add ElastiCache (Redis) for session management
- **CDN**: Leverage CloudFront for global distribution

## Maintenance

### Regular Tasks
- Weekly: Review CloudWatch metrics and logs
- Monthly: Database performance tuning
- Quarterly: Security audit and dependency updates
- Annually: Disaster recovery testing

---

**For support with deployment, contact devops@mindcareai.com**
