# 🚀 Terra Pravah - Complete Deployment Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [Backend Deployment (Railway)](#backend-deployment-railway)
5. [Database Setup](#database-setup)
6. [Environment Variables](#environment-variables)
7. [Post-Deployment Configuration](#post-deployment-configuration)
8. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Architecture Overview

Your Terra Pravah application uses a **3-tier deployment strategy**:

```
┌─────────────────────────────────────┐
│        VERCEL (Frontend)            │
│  - React + TypeScript + Vite        │
│  - Global CDN                       │
├─────────────────────────────────────┤
│        RAILWAY (Backend)            │
│  - Flask + SocketIO                 │
│  - Gunicorn + Gevent                │
├─────────────────────────────────────┤
│  MANAGED SERVICES                   │
│  - PostgreSQL (Railway)             │
│  - Redis (Redis Cloud)              │
│  - S3/GCS (Optional Cloud Storage)  │
└─────────────────────────────────────┘
```

### Why This Architecture?

| Component | Platform | Reason |
|-----------|----------|--------|
| **Frontend** | Vercel | Best for React, automatic deployments, edge caching |
| **Backend** | Railway | Supports Flask, SocketIO/WebSockets, easier scaling |
| **Database** | Railway PostgreSQL | Managed database, automatic backups |
| **Cache** | Redis Cloud | Managed Redis, free tier available |

---

## Prerequisites

Before you start, ensure you have:

- [ ] GitHub account with repository access
- [ ] Vercel account (free tier: vercel.com)
- [ ] Railway account (free credit: railway.app)
- [ ] Redis Cloud account (free tier: redis.com)
- [ ] Node.js 18+ installed locally
- [ ] Python 3.11+ installed locally
- [ ] Git configured locally

### Local Testing (Optional but Recommended)

```bash
# Test frontend build
cd frontend
npm install --legacy-peer-deps
npm run build

# Test backend
cd ../backend
pip install -r requirements.txt
python -m flask run
```

---

## Frontend Deployment (Vercel)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Deploy: Setup Vercel configuration"
git push origin main
```

### Step 2: Import Project to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New"** → **"Project"**
3. Select your **GitHub repository**
4. **Framework Preset**: Select "Vite"
5. Click **"Import"**

### Step 3: Configure Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables:

```
VITE_API_URL = https://api.yourdomain.com
VITE_APP_NAME = Terra Pravah
VITE_APP_VERSION = 2.0.0
VITE_ENVIRONMENT = production
VITE_ENABLE_ANALYTICS = true
VITE_LOG_LEVEL = info
```

> **Note**: Replace `api.yourdomain.com` with your Railway backend URL

### Step 4: Deploy

Click **"Deploy"** button. Vercel will automatically:
- ✅ Clone repository
- ✅ Execute build command: `cd frontend && npm run build`
- ✅ Optimize with Vite
- ✅ Deploy to global CDN
- ✅ Set up HTTPS/SSL certificate

**Expected deployment time**: 2-5 minutes

### Verify Deployment

```bash
# Test your frontend
curl https://your-project.vercel.app
# Should return HTML
```

---

## Backend Deployment (Railway)

### Step 1: Create Railway Account & Project

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub"**
4. Authorize Railway with GitHub
5. Select `Terra_Pravah` repository
6. Railway auto-detects Dockerfile ✅

### Step 2: Create PostgreSQL Service

In Railway Dashboard:

1. Click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway creates database automatically
4. Database URL is auto-populated: `${{ secrets.DATABASE_URL }}`

### Step 3: Create Redis Service

In Railway Dashboard:

1. Click **"+ New"**
2. Select **"Database"** → **"Redis"**
3. Railway creates Redis instance
4. Redis URL is auto-populated: `${{ secrets.REDIS_URL }}`

### Step 4: Configure Environment Variables

In Railway → Your Project → Variables:

Add all variables from `.env.production.example`:

```env
FLASK_ENV=production
SECRET_KEY=<generate-new-secure-key>
JWT_SECRET_KEY=<generate-new-secure-key>

# Database (auto-linked from PostgreSQL service)
DATABASE_URL=${{ secrets.DATABASE_URL }}

# Redis (auto-linked from Redis service)
REDIS_URL=${{ secrets.REDIS_URL }}

CORS_ORIGINS=https://your-project.vercel.app
FRONTEND_URL=https://your-project.vercel.app

# Add other variables...
ANTHROPIC_API_KEY=<your-key>
MAIL_PASSWORD=<your-sendgrid-key>
# etc...
```

### Step 5: Deploy

1. Click **"Deploy"** button
2. Watch logs in Railway Dashboard
3. Expected deployment time: 5-10 minutes

### Verify Deployment

```bash
# Get your Railway backend URL from dashboard
curl https://your-railway-app.up.railway.app/health

# Should return:
# {"status": "ok"}
```

---

## Database Setup

### PostgreSQL Initial Setup

After Railway deployment, run database migrations:

```bash
# Option 1: Via Railway CLI (recommended)
railway run flask db upgrade

# Option 2: Manual via SSH
# In Railway, open "Shell" tab and run:
flask db upgrade
```

### Create Default Admin User

```bash
# Via Railway Shell
FLASK_ENV=production python -m flask shell
>>> from backend.models.models import db, User
>>> admin = User(
...     email='admin@terrapravah.com',
...     username='admin',
...     is_admin=True
... )
>>> admin.set_password('change-me-after-login')
>>> db.session.add(admin)
>>> db.session.commit()
>>> exit()
```

### Verify Database Connection

```bash
# Test from Railway
railway run python -c "from backend.models.models import db, User; print(User.query.all())"
```

---

## Environment Variables

### Generate Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY  
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Critical Variables for Production

| Variable | Source | Example |
|----------|--------|---------|
| `DATABASE_URL` | Railway PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis Cloud | `redis://:password@host:6379` |
| `CORS_ORIGINS` | Vercel Frontend URL | `https://myapp.vercel.app` |
| `SECRET_KEY` | Generate new | 32-char random string |
| `JWT_SECRET_KEY` | Generate new | 32-char random string |
| `ANTHROPIC_API_KEY` | Claude Account | `sk-ant-...` |

### Conditional Variables

**If using SendGrid for email:**
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PASSWORD=<your-sendgrid-api-key>
```

**If using S3 for file storage:**
```env
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_BUCKET_NAME=terrapravah-storage
```

---

## Post-Deployment Configuration

### 1. Connect Frontend to Backend

Update frontend environment variable:

```env
# In Vercel Dashboard
VITE_API_URL = https://your-railway-backend.up.railway.app
```

### 2. Test API Connection

```bash
# From browser console or curl:
curl https://your-railway-backend.up.railway.app/api/health

# Should return: {"status": "ok"}
```

### 3. Setup Custom Domain (Optional)

**For Vercel:**
1. Go to Project Settings → Domains
2. Add your domain
3. Update DNS records (CNAME → vercel.app)

**For Railway:**
1. Go to Project Settings → Domain
2. Add custom domain
3. Update DNS records

### 4. Setup HTTPS/SSL

- ✅ Vercel: Automatic SSL certificate
- ✅ Railway: Automatic SSL certificate

### 5. Setup Monitoring

#### Sentry (Error Tracking)

1. Create account: sentry.io
2. Create project for Terra Pravah
3. Add to prod variables:
   ```env
   SENTRY_DSN=<your-sentry-dsn>
   SENTRY_ENV=production
   ```

#### Railway Monitoring

Railway provides built-in:
- ✅ Logs
- ✅ Metrics
- ✅ Status page
- ✅ Alerts

---

## Monitoring & Troubleshooting

### Frontend Issues

#### Build Fails
```bash
# Check logs in Vercel Dashboard
# Common issues:
# 1. TypeScript errors
npm run lint-fix
npm run build

# 2. Missing env vars - verify in Vercel Settings
# 3. Peer dependency conflicts
npm install --legacy-peer-deps
```

#### Slow Performance
```bash
# Verify API endpoint is correct:
curl -I https://your-api-url.com

# Check Vercel Analytics: 
# Vercel Dashboard → Analytics
```

### Backend Issues

#### Cold Start / Timeout
```bash
# Railway → Logs tab
# Look for slow imports or long startup

# Solution: Optimize Flask app initialization
# - Remove unnecessary imports from app.py
# - Use lazy loading for heavy libraries
```

#### Database Connection Error
```bash
# Railway → Shell
# Test connection:
python -c "from backend.models.models import db; db.engine.execute('SELECT 1')"

# Check DATABASE_URL variable in Railway
```

#### Redis Connection Error
```bash
# Railway → Variables
# Verify REDIS_URL is set and correct

# Test from Railway Shell:
redis-cli -u $REDIS_URL ping
# Should return: PONG
```

### Common Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `CORS error` | Frontend URL not in `CORS_ORIGINS` | Update backend env var |
| `404 Not Found API/...` | Frontend pointing to wrong backend URL | Check `VITE_API_URL` |
| `502 Bad Gateway` | Backend service down | Check Railway logs |
| `Database connection timeout` | PostgreSQL not responding | Restart PostgreSQL in Railway |
| `SSL certificate error` | Domain not linked | Configure custom domain in Vercel/Railway |

### Check Service Health

```bash
# Frontend
curl https://your-project.vercel.app

# Backend API
curl https://your-railway-api.up.railway.app/api/health

# Database (from Railway Shell)
psql $DATABASE_URL -c "SELECT 1"

# Redis (from Railway Shell)
redis-cli -u $REDIS_URL ping
```

### View Logs

**Vercel:**
- Dashboard → Deployments → Click deployment → Logs tab

**Railway:**
- Dashboard → Select project → Logs tab (real-time streaming)

---

## Scaling & Optimization

### Increase Backend Replicas

Railway Dashboard → Settings → Replicas: `1` → `2-4`

### Enable Caching

Update frontend `.env.production`:
```env
VITE_ENABLE_CACHE=true
```

### Optimize Database Queries

Monitoring → check slow queries in PostgreSQL logs

### Setup CDN for Large Files

If serving LiDAR/GeoTIFF files:
```env
STORAGE_BACKEND=s3
# Use S3 CloudFront CDN
```

---

## Summary Checklist

- [ ] Frontend deployed on Vercel
- [ ] Backend deployed on Railway with PostgreSQL & Redis
- [ ] Environment variables configured in both platforms
- [ ] Database migrations ran successfully
- [ ] CORS configured correctly
- [ ] Frontend can communicate with backend
- [ ] Admin user created
- [ ] SSL certificates active
- [ ] Monitoring setup (optional)
- [ ] Custom domain configured (optional)

---

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Flask Deployment**: https://flask.palletsprojects.com/deployment
- **SocketIO Production**: https://python-socketio.readthedocs.io/en/latest/server.html

---

## Next Steps

1. **Monitor** - Watch your deployments for the first 24-48 hours
2. **Test** - Thoroughly test all critical features
3. **Optimize** - Profile and optimize based on usage patterns
4. **Scale** - Increase resources as user base grows

**Success! 🎉 Your Terra Pravah application is now live!**
