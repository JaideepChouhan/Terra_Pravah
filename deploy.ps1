# ================================================================
# Terra Pravah - Quick Deployment Script (PowerShell)
# ================================================================
# This script helps you prepare for deployment on Windows
# Usage: powershell -ExecutionPolicy Bypass -File deploy.ps1

Write-Host ">> Terra Pravah - Deployment Preparation Script" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Check prerequisites
Write-Host "[*] Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check Node.js
try {
    $nodeVersion = (node --version) | Out-String
    Write-Host "[OK] $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = (python --version) | Out-String
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = (git --version) | Out-String
    Write-Host "[OK] $gitVersion" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Git not found. Please install Git" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
Write-Host ""

# Frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
Push-Location frontend
npm install --legacy-peer-deps
Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
Pop-Location

Write-Host ""
Write-Host "[*] Building frontend..." -ForegroundColor Cyan
npm run build --prefix frontend
Write-Host "[OK] Frontend built" -ForegroundColor Green

Write-Host ""
Write-Host "[OK] Deployment preparation complete!" -ForegroundColor Green
Write-Host ""

Write-Host "[NEXT STEPS]" -ForegroundColor Yellow
Write-Host "1. Review environment variables in .env.production.example"
Write-Host "2. Create accounts on Vercel (https://vercel.com) and Railway (https://railway.app)"
Write-Host "3. Push code to GitHub: git push origin main"
Write-Host "4. In Vercel: Import this repository and configure environment variables"
Write-Host "5. In Railway: Create a new project from GitHub and configure environment variables"
Write-Host "6. Follow DEPLOYMENT_GUIDE.md for detailed instructions"
Write-Host ""

Write-Host "[DOCUMENTATION FILES]" -ForegroundColor Yellow
Write-Host "   - DEPLOYMENT_GUIDE.md (Complete deployment guide)"
Write-Host "   - PRE_DEPLOYMENT_CHECKLIST.md (Verification checklist)"
Write-Host "   - .env.production.example (Environment variables reference)"
Write-Host ""

Write-Host "You are ready to deploy!" -ForegroundColor Green
