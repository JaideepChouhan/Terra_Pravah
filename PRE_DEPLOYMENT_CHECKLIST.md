# Terra Pravah - Pre-Deployment Checklist

## ✅ Code & Configuration

- [ ] All code committed to GitHub
- [ ] `.gitignore` configured (no `.env` files in repo)
- [ ] `vercel.json` created and configured
- [ ] `railway.json` created and configured
- [ ] `Dockerfile` updated for production (gunicorn + gevent)
- [ ] Frontend `.env.production` configured
- [ ] Backend `config.py` has `ProductionConfig` class
- [ ] `.env.production.example` created with all variables
- [ ] Frontend `frontend/src/config/api.ts` created
- [ ] Frontend `frontend/.npmrc` created for legacy deps
- [ ] `DEPLOYMENT_GUIDE.md` reviewed and bookmarked

---

## 🔐 Security & Secrets

- [ ] Generate new `SECRET_KEY` (32 chars)
- [ ] Generate new `JWT_SECRET_KEY` (32 chars)
- [ ] Create Anthropic API key (if needed)
- [ ] Create SendGrid API key (if using email)
- [ ] Create Stripe keys (if using billing)
- [ ] **NEVER** commit `.env` files to GitHub
- [ ] All secrets stored in Vercel/Railway dashboards

---

## 🎨 Frontend (Vercel) Setup

- [ ] Create Vercel account (free tier, https://vercel.com)
- [ ] Connect GitHub repository to Vercel
- [ ] Framework detected as "Vite"
- [ ] Build command: `cd frontend && npm run build`
- [ ] Output directory: `frontend/dist`
- [ ] Add environment variables in Vercel:
  - [ ] `VITE_API_URL` (e.g., `https://api.terrapravah.up.railway.app`)
  - [ ] `VITE_APP_NAME=Terra Pravah`
  - [ ] `VITE_APP_VERSION=2.0.0`
  - [ ] `VITE_ENVIRONMENT=production`
- [ ] Initial deployment successful
- [ ] Test frontend loads at https://your-project.vercel.app
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Analytics enabled (optional)

---

## 🐍 Backend (Railway) Setup

- [ ] Create Railway account (free $5 credit, https://railway.app)
- [ ] Connect GitHub repository to Railway
- [ ] Dockerfile auto-detected ✓
- [ ] PostgreSQL service created and linked
- [ ] Redis service created and linked
- [ ] Add environment variables in Railway:
  - [ ] `FLASK_ENV=production`
  - [ ] `SECRET_KEY=<new-generated-key>`
  - [ ] `JWT_SECRET_KEY=<new-generated-key>`
  - [ ] `DATABASE_URL=${{ secrets.DATABASE_URL }}` (auto-linked)
  - [ ] `REDIS_URL=${{ secrets.REDIS_URL }}` (auto-linked)
  - [ ] `CORS_ORIGINS=https://your-project.vercel.app`
  - [ ] `FRONTEND_URL=https://your-project.vercel.app`
  - [ ] `ANTHROPIC_API_KEY=<your-key>` (if needed)
  - [ ] `MAIL_PASSWORD=<sendgrid-key>` (if using email)
  - [ ] Other required variables from `.env.production.example`
- [ ] Initial deployment successful
- [ ] Test backend health at https://your-railway-api.up.railway.app/health
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active

---

## 🗄️ Database Setup

- [ ] PostgreSQL service running on Railway
- [ ] Database created: `terrapravah`
- [ ] Run migrations:
  ```bash
  railway run flask db upgrade
  ```
- [ ] Create default admin user:
  ```bash
  railway run python -c "from backend.models.models import db, User; \
  u = User(email='admin@example.com', username='admin'); \
  u.set_password('temp-password'); \
  db.session.add(u); \
  db.session.commit(); \
  print('Admin user created')"
  ```
- [ ] Test database connection from Railway Shell
- [ ] Verify migrations ran without errors

---

## 📊 Redis Setup

- [ ] Redis service running on Railway (or Redis Cloud)
- [ ] Connection string in `REDIS_URL`
- [ ] Test connection:
  ```bash
  railway run redis-cli -u $REDIS_URL ping
  # Should return: PONG
  ```
- [ ] Session storage working
- [ ] WebSocket message queue configured

---

## 🔗 Integration & Testing

**Frontend-Backend Connection:**
- [ ] CORS properly configured in backend
- [ ] `VITE_API_URL` points to correct backend
- [ ] Test from browser console:
  ```javascript
  fetch('https://your-api.com/api/health')
    .then(r => r.json())
    .then(d => console.log(d))
  ```

**Critical Feature Testing:**
- [ ] User registration works
- [ ] User login works
- [ ] JWT tokens issued correctly
- [ ] File uploads work
- [ ] LiDAR processing works (if applicable)
- [ ] WebSocket connections work (if applicable)
- [ ] Email notifications work (if enabled)
- [ ] File downloads work

---

## 🚨 Error Monitoring

- [ ] Sentry project created (optional, https://sentry.io)
- [ ] `SENTRY_DSN` added to production variables
- [ ] Check Vercel & Railway dashboards for errors
- [ ] Review logs regularly for first week

---

## 📈 Performance & Scaling

- [ ] Vercel Analytics enabled
- [ ] Frontend build time < 3 minutes
- [ ] Backend container startup < 30 seconds
- [ ] Database queries optimized
- [ ] Static assets cached properly
- [ ] Rate limiting configured

---

## 🔒 Security & Compliance

- [ ] HTTPS/SSL enabled on all domains
- [ ] CORS restricted to your domain only
- [ ] JWT tokens have proper expiration (1 hour)
- [ ] Session cookies are secure + httponly + samesite
- [ ] Database credentials never in code
- [ ] API keys never in version control
- [ ] Sensitive data logged appropriately (no passwords/tokens)

---

## 📞 Monitoring & Alerts (Optional)

- [ ] Railway alerts configured for:
  - [ ] High CPU usage
  - [ ] Restart/crash events
  - [ ] Database connection issues
- [ ] Status page setup (Vercel Status)
- [ ] Error tracking dashboard reviewed
- [ ] Uptime monitoring configured

---

## 🎉 Final Verification

### Test Complete User Flow

1. **Frontend Access:**
   ```bash
   curl -I https://your-project.vercel.app
   # Should return: 200 OK
   ```

2. **Backend API:**
   ```bash
   curl https://your-api.up.railway.app/api/health
   # Should return: {"status": "ok"}
   ```

3. **Database:**
   ```bash
   railway run psql $DATABASE_URL -c "SELECT 1;"
   # Should work without errors
   ```

4. **Redis:**
   ```bash
   railway run redis-cli -u $REDIS_URL ping
   # Should return: PONG
   ```

---

## ✨ Success Indicators

- ✅ Frontend loads and is accessible
- ✅ Backend API responds to requests
- ✅ Database is populated and queries work
- ✅ Frontend can communicate with backend (no CORS errors)
- ✅ User authentication flow works
- ✅ File uploads/processing work
- ✅ No 5xx errors in logs
- ✅ Response times < 2 seconds (normal queries)

---

## 📚 Documentation Links

- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Flask Documentation](https://flask.palletsprojects.com)
- [SocketIO Production](https://python-socketio.readthedocs.io/en/latest/server.html)

---

## 🎯 Post-Launch Monitoring

1. **First 24 Hours:**
   - Monitor logs closely
   - Test user registration/login flow
   - Verify file uploads work
   - Check error tracking dashboard

2. **First Week:**
   - Monitor performance metrics
   - Check database query performance
   - Review error patterns
   - Optimize slow endpoints

3. **Ongoing:**
   - Daily log review
   - Weekly performance check
   - Monthly security audit
   - Quarterly scaling assessment

---

**Status: Ready for Deployment! 🚀**

> Date Completed: _______________
> Deployed By: _______________
> Notes: _________________________________________________________________
