# Deployment Guide

## Overview

This project uses GitHub Actions for continuous integration and automatic deployment to Trigger.dev. Every push to the `main` branch triggers a full CI/CD pipeline that includes testing, security checks, and automatic deployment of Trigger.dev tasks.

## GitHub Actions Workflow

### Pipeline Structure

The CI/CD pipeline consists of several jobs that run in parallel and sequence:

1. **test** - Runs on multiple Python versions (3.11, 3.12, 3.13)
2. **test-llm** - Runs LLM tests (only on main branch pushes)
3. **security** - Security scanning with bandit and safety
4. **performance** - Performance benchmarks (only on main branch pushes)
5. **deploy-docs** - Documentation generation (only on main branch pushes)
6. **deploy-trigger** - Automatic Trigger.dev deployment (only on main branch pushes)

### Trigger.dev Deployment Jobs

The pipeline now includes two deployment jobs:

1. **`deploy-trigger-dev`** - Deploys to development environment on **any push**
2. **`deploy-trigger-prod`** - Deploys to production environment on **main branch pushes only**

Each job:

1. Sets up Node.js and Python environments
2. Installs all dependencies
3. Validates the Python API server is accessible
4. Deploys tasks to Trigger.dev using the official CLI

## Required GitHub Secrets

To enable automatic deployment, you need to configure the following secrets in your GitHub repository:

### Trigger.dev Secrets

-   `TRIGGER_ACCESS_TOKEN` - Your Trigger.dev access token (get from Trigger.dev dashboard)

### Database & API Secrets

-   `DATABASE_URL` - PostgreSQL connection string for production
-   `PYTHON_API_URL` - Public URL of your deployed Python API server (e.g., https://your-api.herokuapp.com)
-   `API_TOKEN` - Authentication token for the Python API server

### External Service Secrets

-   `DEEPSEEK_API_KEY` - DeepSeek API key for LLM functionality
-   `SLACK_BOT_TOKEN` - Slack bot token for notifications
-   `SLACK_USER_ID` - Your Slack user ID for direct messages

## Setting Up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its corresponding value

### Getting Your Trigger.dev Access Token

1. Log in to [Trigger.dev](https://trigger.dev)
2. Go to your project dashboard
3. Navigate to **Settings** → **API Keys**
4. Create a new access token or copy an existing one
5. Add it as `TRIGGER_ACCESS_TOKEN` in GitHub secrets

## Manual Deployment

You can also deploy manually using the npm scripts:

```bash
# Deploy to development environment
npm run trigger:deploy:dev

# Deploy to production environment
npm run trigger:deploy:prod

# Start local development mode
npm run trigger:dev

# List deployed tasks (development)
npm run trigger:list:dev

# List deployed tasks (production)
npm run trigger:list:prod

# View logs (development)
npm run trigger:logs:dev

# View logs (production)
npm run trigger:logs:prod
```

## Environment Variables

The deployment process uses the following environment variables:

### Required for Trigger.dev Tasks

-   `TRIGGER_ACCESS_TOKEN` - Trigger.dev authentication
-   `DATABASE_URL` - PostgreSQL connection
-   `PYTHON_API_URL` - Public URL of your deployed Python API server
-   `API_TOKEN` - API authentication token

### Optional for Enhanced Features

-   `DEEPSEEK_API_KEY` - LLM analysis capabilities
-   `SLACK_BOT_TOKEN` - Slack notifications
-   `SLACK_USER_ID` - Direct message target

## Deployment Architecture

```
GitHub Push → GitHub Actions → Tests Pass → Deploy to Development
     ↓                                              ↓
Main Branch? ────────────────────────────→ Deploy to Production
     ↓                                              ↓
Validate Python API Server (must be publicly accessible)
     ↓                                              ↓
Deploy Trigger.dev Tasks (dev/prod environments)
     ↓                                              ↓
Tasks can call Python API endpoints
```

### Deployment Flow

1. **Any Push**: Deploys to development environment after tests pass
2. **Main Branch Push**: Additionally deploys to production environment after security checks
3. **Environment Separation**: Development and production tasks are isolated
4. **Testing**: Development deployment is tested before production deployment

## Python API Server Deployment

**Important**: Your Python API server must be deployed to a publicly accessible URL before Trigger.dev deployment will work. Options include:

### Cloud Deployment Options

1. **Railway** (Recommended)

    ```bash
    # Install Railway CLI
    npm install -g @railway/cli

    # Deploy
    railway login
    railway init
    railway up
    ```

2. **Heroku**

    ```bash
    # Create Procfile
    echo "web: uvicorn src.api.main:app --host 0.0.0.0 --port \$PORT" > Procfile

    # Deploy
    heroku create your-stock-api
    git push heroku main
    ```

3. **Render**

    - Connect your GitHub repo
    - Set build command: `uv sync --all-extras`
    - Set start command: `uv run uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

4. **DigitalOcean App Platform**
    - Similar setup to Render
    - Good performance and pricing

### Environment Variables for API Deployment

Your deployed API server needs these environment variables:

```bash
API_TOKEN=your-secure-api-token
DATABASE_URL=your-postgresql-url
DEEPSEEK_API_KEY=your-deepseek-key
```

## Troubleshooting Deployment

### Common Issues

1. **Missing Secrets**: Ensure all required GitHub secrets are configured
2. **API Server Startup**: The Python API server must start successfully for deployment
3. **Environment Validation**: Tasks use fail-fast validation and will fail if required env vars are missing

### Debugging Steps

1. Check GitHub Actions logs for detailed error messages
2. Verify all secrets are properly configured
3. Test the Python API server locally: `make run-api`
4. Test Trigger.dev connection: `npm run trigger:list`

### Manual Deployment Fallback

If automatic deployment fails, you can deploy manually:

```bash
# Ensure API server is running
make run-api

# Deploy in another terminal
npm run trigger:deploy
```

## Monitoring Deployments

-   **GitHub Actions**: Monitor deployment status in the Actions tab
-   **Trigger.dev Dashboard**: View deployed tasks and their status
-   **Logs**: Use `npm run trigger:logs` to view task execution logs

## Security Considerations

-   All sensitive data is stored in GitHub secrets
-   API tokens are rotated regularly
-   Database connections use SSL
-   Tasks validate environment variables before execution

## Next Steps

After setting up deployment:

1. Configure all required GitHub secrets
2. Push to main branch to trigger first deployment
3. Monitor the deployment in GitHub Actions
4. Verify tasks are running in Trigger.dev dashboard
5. Test task execution and monitoring
