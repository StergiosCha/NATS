#!/bin/bash

# Railway Deployment Script for NATS
# This script helps deploy NATS to Railway with proper configuration

echo "🚀 NATS Railway Deployment Script"
echo "================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project
echo "📦 Creating Railway project..."
railway project create nats-text-analysis

# Set environment variables
echo "⚙️ Setting environment variables..."
railway variables set PORT=5000
railway variables set FLASK_ENV=production
railway variables set PYTHONUNBUFFERED=1

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your NATS application is now live on Railway!"
echo "📊 Check the Railway dashboard for your app URL and logs."










