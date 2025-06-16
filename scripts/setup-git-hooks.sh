#!/bin/bash

# Setup script for git hooks and Trigger.dev deployment

echo "🔧 Setting up git hooks for Trigger.dev deployment..."

# Configure git to use our custom hooks directory
git config core.hooksPath .githooks

# Make hooks executable
chmod +x .githooks/post-push

echo "✅ Git hooks configured!"
echo ""
echo "📋 Next steps:"
echo "1. Set your Trigger.dev access token:"
echo "   export TRIGGER_ACCESS_TOKEN=your_token_here"
echo ""
echo "2. Test your authentication:"
echo "   npm run trigger:whoami"
echo ""
echo "3. Deploy manually if needed:"
echo "   npm run trigger:deploy:dev   # For development"
echo "   npm run trigger:deploy:prod  # For production"
echo ""
echo "4. Automatic deployment on git push:"
echo "   git push origin develop  # Deploys to development"
echo "   git push origin main     # Deploys to production"
echo ""
echo "✅ Setup complete!" 