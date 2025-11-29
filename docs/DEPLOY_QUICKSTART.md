# Quick Reference: Celery + Django Deployment

## ✅ Files Created

1. **`supervisord.conf`** - Process manager config
2. **`start.sh`** - Main startup script (with Supervisor)
3. **`start-simple.sh`** - Alternative startup (no Supervisor)
4. **`Dockerfile`** - Updated to install Supervisor
5. **`CELERY_DEPLOYMENT.md`** - Full documentation

---

## 🚀 Deploy to Render

### Step 1: Commit & Push

```bash
cd /root/GitHub/ALX-PD-BE/RemoSphere/remosphere-backend

git add supervisord.conf start.sh start-simple.sh Dockerfile CELERY_DEPLOYMENT.md
git commit -m "feat: add supervisor to run Django + Celery together"
git push origin main
```

### Step 2: Verify Render Environment Variables

Make sure these are set in Render Dashboard → Environment:

```
CELERY_BROKER_URL=redis://your-redis-url:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-url:6379/1
SENDGRID_API_KEY=your-sendgrid-key
```

### Step 3: Watch Render Deploy

Render will auto-detect changes and rebuild. Wait for deployment.

### Step 4: Check Logs

Look for these lines in Render logs:

```
✅ Starting RemoSphere Backend Services
✅ Running database migrations...
✅ Collecting static files...
✅ Starting Django and Celery via Supervisor...
✅ supervisord started with pid XXX
✅ spawned: 'django' with pid XXX
✅ spawned: 'celery_worker' with pid YYY
```

---

## 🧪 Test Celery Works

### Test 1: Register a New User

1. Go to your frontend
2. Register a new user
3. Check Render logs for email task:

```
[INFO/MainProcess] Task authentication.email_utils.send_verification_email succeeded
```

### Test 2: Check Supervisor Status (Render Shell)

```bash
supervisorctl status

# Should show:
# celery_worker    RUNNING
# django           RUNNING
```

---

## 🔧 Troubleshooting

### Celery Not Running?

**Check 1: Redis Connection**
```bash
# In Render shell
python -c "import redis; r=redis.from_url('$CELERY_BROKER_URL'); print(r.ping())"
# Should print: True
```

**Check 2: Celery Can Connect**
```bash
celery -A remosphere inspect ping
# Should show: pong
```

**Check 3: Tasks Registered**
```bash
celery -A remosphere inspect registered
# Should list your tasks
```

### Container Keeps Crashing?

**Check logs for:**
- Migration errors
- Missing env vars
- Database connection issues
- Supervisor syntax errors

### Emails Not Sending?

**Verify:**
1. SENDGRID_API_KEY is set
2. DEFAULT_FROM_EMAIL is configured
3. Celery worker is running
4. No errors in Celery logs

---

## 📊 How It Works

```
┌─────────────────────────────────┐
│   Docker Container (Render)     │
│                                  │
│  ┌───────────────────────────┐  │
│  │     Supervisor (Root)      │  │
│  │                            │  │
│  │  ┌──────────────────────┐ │  │
│  │  │  Django (appuser)     │ │  │
│  │  │  Port 8000            │ │  │
│  │  └──────────────────────┘ │  │
│  │                            │  │
│  │  ┌──────────────────────┐ │  │
│  │  │  Celery (appuser)     │ │  │
│  │  │  Background Tasks     │ │  │
│  │  └──────────────────────┘ │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
           ↓
    ┌─────────────┐
    │ Redis       │
    │ (Render)    │
    └─────────────┘
```

---

## 🎯 Key Points

1. **Supervisor** runs as root to manage processes
2. **Django & Celery** run as `appuser` for security
3. **Logs** go to stdout/stderr (visible in Render)
4. **Auto-restart** enabled for both services
5. **Single container** = easier to manage on Render

---

## 🔍 Monitoring Commands

```bash
# View all processes
supervisorctl status

# Restart Celery only
supervisorctl restart celery_worker

# Restart Django only
supervisorctl restart django

# Restart all
supervisorctl restart all

# View logs
supervisorctl tail -f celery_worker
supervisorctl tail -f django
```

---

## 📝 Next Steps After Deployment

1. ✅ Verify both Django and Celery are running
2. ✅ Test user registration (email verification)
3. ✅ Monitor logs for errors
4. ✅ Set up Sentry for error tracking
5. 📅 Add Celery Beat for periodic tasks (if needed)
6. 📊 Add Flower for Celery monitoring (optional)

---

## 💡 Pro Tips

- **Health Checks**: Supervisor auto-restarts crashed processes
- **Scaling**: When traffic grows, split to separate services
- **Redis**: Use same Redis for cache + Celery broker
- **Logs**: Check Render logs regularly for Celery errors
- **Performance**: Adjust `--concurrency` based on workload

---

**Ready to deploy? Run the git commands above!** 🚀
