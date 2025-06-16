# 🚀 Deployment Guide

## Overview

This project uses **git-based deployment** to Trigger.dev. Deployments are triggered automatically when you push to specific branches.

## 🔧 Setup

### 1. Configure Git Hooks

```bash
# Run the setup script
npm run setup:hooks

# Or manually:
git config core.hooksPath .githooks
chmod +x .githooks/post-push
```

### 2. Set Environment Variables

```bash
# Set your Trigger.dev access token
export TRIGGER_ACCESS_TOKEN=tr_pat_your_token_here

# Optional: Add to your shell profile (.bashrc, .zshrc, etc.)
echo 'export TRIGGER_ACCESS_TOKEN=tr_pat_your_token_here' >> ~/.zshrc
```

### 3. Test Authentication

```bash
# Verify your token works
npm run trigger:whoami
```

## 🌟 Deployment Workflow

### Automatic Deployment (Git Hooks)

```bash
# Deploy to development
git push origin develop

# Deploy to production
git push origin main
```

**What happens:**

1. Code is pushed to GitHub
2. GitHub Actions runs tests
3. Git post-push hook triggers locally
4. Trigger.dev deployment starts based on branch

### Manual Deployment

```bash
# Deploy to development
npm run trigger:deploy:dev

# Deploy to production
npm run trigger:deploy:prod

# Deploy to current environment
npm run trigger:deploy
```

## 🌍 Environments

| Branch    | Environment | Trigger.dev Env |
| --------- | ----------- | --------------- |
| `develop` | Development | `development`   |
| `main`    | Production  | `production`    |
| Other     | None        | Manual only     |

## 📋 Available Scripts

```bash
# Development server
npm run trigger:dev

# Manual deployments
npm run trigger:deploy          # Current environment
npm run trigger:deploy:dev      # Development
npm run trigger:deploy:prod     # Production

# Utilities
npm run trigger:whoami          # Check authentication
npm run setup:hooks             # Configure git hooks
```

## 🔍 Troubleshooting

### Authentication Issues

```bash
# Check if token is set
echo $TRIGGER_ACCESS_TOKEN

# Test authentication
npm run trigger:whoami

# Re-login if needed
npx trigger.dev@latest login
```

### Hook Not Running

```bash
# Check git hooks configuration
git config core.hooksPath

# Should output: .githooks

# Make sure hook is executable
chmod +x .githooks/post-push

# Test hook manually
./.githooks/post-push
```

### Deployment Failures

```bash
# Check Trigger.dev status
npx trigger.dev@latest status

# View deployment logs
npx trigger.dev@latest logs

# Manual deployment with verbose output
npx trigger.dev@latest deploy --verbose
```

## 🚨 Important Notes

- **Git hooks run locally** - you need the `TRIGGER_ACCESS_TOKEN` set on your machine
- **GitHub Actions only run tests** - no deployment secrets needed in GitHub
- **Each developer** needs to set up their own Trigger.dev token
- **Hooks are optional** - you can always deploy manually

## 🔄 Migration from GitHub Actions

Previously, deployments ran in GitHub Actions. Now:

✅ **Benefits:**

- No secrets needed in GitHub
- Faster feedback (local deployment)
- More control over when deployments happen
- Easier debugging

❌ **Trade-offs:**

- Each developer needs Trigger.dev access
- Deployments require local environment setup
- No automatic deployment on PR merge (manual push needed)

## 🎯 Best Practices

1. **Test locally first**: `npm run trigger:dev`
2. **Deploy to develop**: Test in development environment
3. **Deploy to main**: Only after development testing
4. **Monitor deployments**: Check Trigger.dev dashboard
5. **Keep tokens secure**: Don't commit tokens to git

---

**Ready to deploy!** 🚀
