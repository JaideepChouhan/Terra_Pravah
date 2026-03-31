# AIR_TERRA_PRAVAH - QUICK RUN INSTRUCTIONS

## 🚀 START THE PROJECT IN 3 STEPS

### Step 1: Activate Virtual Environment
```bash
cd /home/jaideepchouhan/pythonProjects/AIR_Terra_Pravah
source .venv/bin/activate
```

### Step 2: Start Backend Server
```bash
python run.py --dev --port 5000
```

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════════╗
║     TERRA PRAVAH - AI-Powered Drainage Design Platform        ║
╚═══════════════════════════════════════════════════════════════╝

📦 Initializing Database...
✅ Database tables created successfully
✅ Database initialization complete

=================================================================
  🌍 Environment: DEVELOPMENT
  🔗 Server: http://localhost:5000
  🗄️  Database: sqlite:///database/terrapravah.db
  🔐 Debug Mode: Enabled
  📱 Frontend: Served from backend (frontend/dist/)
=================================================================

✅ APPLICATION READY

🌐 Open: http://localhost:5000
🏥 Health Check: http://localhost:5000/api/health

Press Ctrl+C to stop the server
```

### Step 3: Access the Application
- **Web App:** http://localhost:5000
- **API Health:** http://localhost:5000/api/health
- **API Docs:** http://localhost:5000/api/docs

---

## 🎨 OPTIONAL: RUN FRONTEND DEV SERVER

Open **another terminal** and run:

```bash
cd /home/jaideepchouhan/pythonProjects/AIR_Terra_Pravah/frontend
npm install  # Only needed first time
npm run dev
```

Then access the frontend at:
- **Frontend Dev:** http://localhost:5173 or http://localhost:3000

---

## 🐳 DOCKER DEPLOYMENT (Production)

To run the entire stack with Docker:

```bash
docker-compose up --build
```

Access at: http://localhost

---

## 📋 AVAILABLE COMMANDS

### Development Server
```bash
python run.py --dev                    # Run with debug enabled
python run.py --prod                   # Run in production mode
python run.py --init-db               # Initialize database
python run.py --host 0.0.0.0          # Listen on all interfaces
python run.py --port 8000             # Custom port
```

### Database Management
```bash
python run.py --init-db               # Create tables
python -c "from backend.utils.seed import seed_database; seed_database()"  # Seed sample data
```

### Testing
```bash
pytest                                # Run all tests
pytest -v                             # Verbose test output
pytest --cov=backend                 # Code coverage
```

---

## 🔧 TROUBLESHOOTING

### Port Already in Use
```bash
python run.py --port 8000            # Use different port
```

### Database Issues
```bash
rm database/terrapravah.db           # Delete old database
python run.py --init-db              # Reinitialize
```

### Virtual Environment Issues
```bash
source .venv/bin/activate            # Activate venv
pip install -r requirements.txt       # Reinstall dependencies
```

---

## ✅ WHAT'S WORKING

- ✅ Backend API (Flask)
- ✅ Database (SQLite/PostgreSQL)
- ✅ Authentication (JWT)
- ✅ REST Endpoints
- ✅ WebSocket Support
- ✅ CORS Configuration
- ✅ Rate Limiting
- ✅ Error Handling
- ✅ Logging
- ✅ Docker Ready

---

## 📚 DOCUMENTATION

- **Full Report:** [PROJECT_STATUS_FINAL.md](PROJECT_STATUS_FINAL.md)
- **Analysis Report:** [PROJECT_ANALYSIS_COMPLETE.md](PROJECT_ANALYSIS_COMPLETE.md)
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **Technical Docs:** [docs/](docs/) folder
- **Integration Guide:** [DTM_INTEGRATION_GUIDE.md](DTM_INTEGRATION_GUIDE.md)

---

## 🎯 PROJECT INFORMATION

**Name:** AIR Terra Pravah  
**Version:** 2.3 (Production Ready)  
**Type:** AI-Powered Drainage Network Design System  
**Tech Stack:** Python (Flask) + React + PostgreSQL/SQLite  
**Status:** ✅ FULLY OPERATIONAL

---

**Happy coding! 🚀**
