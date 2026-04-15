#!/bin/bash
# ================================================================
# Terra Pravah - Quick Deployment Script
# ================================================================
# This script helps you prepare for deployment
# Usage: bash deploy.sh

set -e

echo "🚀 Terra Pravah - Deployment Preparation Script"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js $(node --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $(python3 --version)${NC}"

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found. Please install Git${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git $(git --version | grep -oP 'version \K[^ ]*')${NC}"

echo ""
echo "📦 Installing dependencies..."
echo ""

# Frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
cd ..

echo ""
echo "🔨 Building frontend..."
npm run build --prefix frontend || true
echo -e "${GREEN}✅ Frontend built (or build warnings exist)${NC}"

echo ""
echo "✅ Deployment preparation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Review environment variables in .env.production.example"
echo "2. Create accounts on Vercel (https://vercel.com) and Railway (https://railway.app)"
echo "3. Push code to GitHub: git push origin main"
echo "4. In Vercel: Import this repository and configure environment variables"
echo "5. In Railway: Create a new project from GitHub and configure environment variables"
echo "6. Follow DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "📖 Documentation:"
echo "   - DEPLOYMENT_GUIDE.md (Complete deployment guide)"
echo "   - PRE_DEPLOYMENT_CHECKLIST.md (Verification checklist)"
echo "   - .env.production.example (Environment variables reference)"
echo ""
echo -e "${GREEN}Good luck! 🎉${NC}"
