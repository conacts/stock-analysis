# 🚀 Deployment Guide

This guide covers deploying the Stock Analysis API to Railway and other platforms.

## 🌐 Current Production Deployment

**Production URL**: `https://stock-analysis-production-31e9.up.railway.app`
**Platform**: Railway
**Status**: ✅ Active
**Health Check**: `/health` and `/healthz` endpoints

## 📋 Prerequisites

1. **Environment Variables**:

    - `API_TOKEN` - Authentication token for API access
    - `DEEPSEEK_API_KEY` - DeepSeek AI API key for LLM functionality
    - `DATABASE_URL` - PostgreSQL database connection string

2. **Dependencies**:
    - Python 3.12+
    - uv package manager
    - Docker (for containerized deployment)

## 🚂 Railway Deployment

### Initial Setup

1. **Connect Repository**:

    ```bash
    # Install Railway CLI
    npm install -g @railway/cli

    # Login to Railway
    railway login

    # Link to existing project
    railway link
    ```

2. **Environment Configuration**:

    ```bash
    # Set environment variables
    railway variables set API_TOKEN=your-api-token
    railway variables set DEEPSEEK_API_KEY=your-deepseek-key
    railway variables set DATABASE_URL=your-postgres-url
    ```

3. **Database Setup**:

    ```bash
    # Add PostgreSQL service
    railway add postgresql

    # Get database URL
    railway variables
    ```

### Deployment Process

1. **Automatic Deployment**:

    - Railway automatically deploys on push to `main` branch
    - Build uses `Dockerfile` in project root
    - Health checks run on `/health` endpoint

2. **Manual Deployment**:

    ```bash
    # Deploy current branch
    railway up

    # Deploy specific branch
    railway up --branch dev
    ```

3. **Monitor Deployment**:

    ```bash
    # View logs
    railway logs

    # Check service status
    railway status
    ```

### Railway Configuration

**railway.json**:

```json
{
    "$schema": "https://railway.app/railway.schema.json",
    "build": {
        "builder": "dockerfile"
    },
    "deploy": {
        "healthcheckPath": "/health",
        "healthcheckTimeout": 30,
        "restartPolicyType": "on_failure"
    }
}
```

## 🐳 Docker Deployment

### Build Image

```bash
# Build production image
docker build -t stock-analysis .

# Build with specific tag
docker build -t stock-analysis:v1.0.0 .
```

### Run Container

```bash
# Run with environment file
docker run --env-file .env.local -p 8000:8000 stock-analysis

# Run with individual environment variables
docker run \
  -e API_TOKEN=your-token \
  -e DEEPSEEK_API_KEY=your-key \
  -e DATABASE_URL=your-db-url \
  -p 8000:8000 \
  stock-analysis
```

### Docker Compose

**docker-compose.yml**:

```yaml
version: "3.8"

services:
    api:
        build: .
        ports:
            - "8000:8000"
        environment:
            - API_TOKEN=${API_TOKEN}
            - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
            - DATABASE_URL=${DATABASE_URL}
        depends_on:
            - db
        restart: unless-stopped

    db:
        image: postgres:15
        environment:
            - POSTGRES_DB=stockanalysis
            - POSTGRES_USER=postgres
            - POSTGRES_PASSWORD=password
        volumes:
            - postgres_data:/var/lib/postgresql/data
        ports:
            - "5432:5432"

volumes:
    postgres_data:
```

Run with:

```bash
docker-compose up -d
```

## ☁️ Other Cloud Platforms

### AWS ECS

1. **Create ECR Repository**:

    ```bash
    aws ecr create-repository --repository-name stock-analysis
    ```

2. **Push Image**:

    ```bash
    # Get login token
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

    # Tag and push
    docker tag stock-analysis:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/stock-analysis:latest
    docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/stock-analysis:latest
    ```

3. **Create ECS Service**:
    - Use AWS Console or CLI to create ECS cluster
    - Define task definition with environment variables
    - Create service with load balancer

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy stock-analysis \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars API_TOKEN=your-token,DEEPSEEK_API_KEY=your-key,DATABASE_URL=your-db-url
```

### Azure Container Instances

```bash
# Create resource group
az group create --name stock-analysis-rg --location eastus

# Deploy container
az container create \
  --resource-group stock-analysis-rg \
  --name stock-analysis \
  --image your-registry/stock-analysis:latest \
  --dns-name-label stock-analysis \
  --ports 8000 \
  --environment-variables API_TOKEN=your-token DEEPSEEK_API_KEY=your-key DATABASE_URL=your-db-url
```

## 🔧 Configuration

### Environment Variables

| Variable           | Required | Description                    | Example                               |
| ------------------ | -------- | ------------------------------ | ------------------------------------- |
| `API_TOKEN`        | Yes      | Authentication token           | `default-dev-token`                   |
| `DEEPSEEK_API_KEY` | Yes      | DeepSeek AI API key            | `sk-xxx`                              |
| `DATABASE_URL`     | Yes      | PostgreSQL connection          | `postgresql://user:pass@host:5432/db` |
| `PORT`             | No       | Server port (default: 8000)    | `8000`                                |
| `HOST`             | No       | Server host (default: 0.0.0.0) | `0.0.0.0`                             |

### Health Checks

The application provides two health check endpoints:

1. **`/health`** - Comprehensive health check with environment validation
2. **`/healthz`** - Minimal health check for load balancers

Configure your platform to use `/health` with a 30-second timeout.

### Database Migration

The application automatically creates tables on startup. For production:

1. **Backup existing data**:

    ```bash
    pg_dump $DATABASE_URL > backup.sql
    ```

2. **Run migrations**:
    ```bash
    # Application handles this automatically
    # Or run manually if needed
    uv run python -c "from src.database.db_manager import DatabaseManager; DatabaseManager().create_tables()"
    ```

## 📊 Monitoring

### Health Monitoring

```bash
# Check health
curl https://your-domain.com/health

# Check minimal health
curl https://your-domain.com/healthz
```

### Logs

```bash
# Railway logs
railway logs --tail

# Docker logs
docker logs container-name --tail 100 -f

# Application logs are structured JSON
```

### Metrics

The application exposes metrics through:

-   Health check endpoints
-   Portfolio health check endpoint
-   Trading system status

## 🔒 Security

### API Authentication

All endpoints (except health checks) require Bearer token authentication:

```bash
Authorization: Bearer your-api-token
```

### Environment Security

1. **Never commit secrets** to version control
2. **Use platform secret management**:

    - Railway: Environment variables
    - AWS: Parameter Store / Secrets Manager
    - GCP: Secret Manager
    - Azure: Key Vault

3. **Rotate keys regularly**
4. **Use least privilege access**

### Network Security

1. **HTTPS only** in production
2. **Firewall rules** to restrict access
3. **Rate limiting** (implement as needed)
4. **CORS configuration** for web clients

## 🚨 Troubleshooting

### Common Issues

1. **Health Check Failures**:

    ```bash
    # Check environment variables
    railway variables

    # Check logs
    railway logs --tail

    # Test locally
    docker run --env-file .env.local -p 8000:8000 stock-analysis
    ```

2. **Database Connection Issues**:

    ```bash
    # Test database connection
    psql $DATABASE_URL -c "SELECT 1;"

    # Check database logs
    railway logs --service postgresql
    ```

3. **Memory Issues**:

    - Railway: Upgrade to higher memory plan
    - Docker: Increase memory limits
    - Optimize application memory usage

4. **Build Failures**:

    ```bash
    # Test build locally
    docker build -t test .

    # Check Dockerfile syntax
    docker build --no-cache -t test .
    ```

### Performance Optimization

1. **Docker Image Size**:

    - Current size: ~851MB (optimized from 6.2GB)
    - Uses multi-stage builds
    - Python slim base image

2. **Database Performance**:

    - Connection pooling
    - Query optimization
    - Index creation

3. **API Response Times**:
    - Async endpoints where possible
    - Caching for expensive operations
    - Background task processing

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer** configuration
2. **Database connection pooling**
3. **Stateless application design**
4. **Session management** (if needed)

### Vertical Scaling

1. **Memory allocation** based on usage
2. **CPU allocation** for AI processing
3. **Storage** for logs and temporary files

---

**Last Updated**: 2025-06-14
**Deployment Status**: ✅ Production Ready
**Platform**: Railway (Primary)
