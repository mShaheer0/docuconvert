#!/bin/bash
# Quick setup script for Digital Ocean Droplet
# Run as: bash setup.sh

set -e

echo "🚀 Setting up docuconvert on Digital Ocean Droplet..."

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
apt install -y docker.io docker-compose git curl

# Start Docker
systemctl start docker
systemctl enable docker

# Clone repo
echo "📥 Cloning repository..."
cd /
rm -rf /app 2>/dev/null || true
git clone https://github.com/mShaheer0/docuconvert.git app
cd /app

# Build and start
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting application..."
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for app to be ready..."
sleep 10

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is running!"
    echo ""
    echo "📊 Droplet Info:"
    echo "   URL: http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Configure GitHub Secrets (DO_SSH_KEY, DO_DROPLET_IP, DO_SSH_USER)"
    echo "   2. Push code to main branch to trigger auto-deployment"
    echo "   3. Check deployment status in GitHub Actions"
    echo ""
    echo "💡 View logs: docker-compose logs -f app"
    echo "🔄 Restart: docker-compose restart"
else
    echo "❌ App failed health check. Check logs:"
    docker-compose logs app
    exit 1
fi
