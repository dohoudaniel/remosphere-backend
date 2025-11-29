# Celery + Django Deployment Fix - Summary

## 🎯 Problem Solved

**Issue**: Celery tasks (email verification, etc.) were not running in production on Render because the Docker container only ran Django/Gunicorn, not the Celery worker.

**Solution**: Updated Docker setup to run **both Django and Celery** in the same container using **Supervisor** process manager.

---

## 📦 What Was Changed

### **New Files Created**

| File | Purpose |
|------|---------|
| `supervisord.conf` | Supervisor configuration to manage Django + Celery |
| `start.sh` | Startup script that runs migrations, collectstatic, and starts Supervisor |
| `start-simple.sh` | Alternative startup without Supervisor (simpler but less robust) |
| `.dockerignore` | Optimizes Docker build by excluding unnecessary files |
| `CELERY_DEPLOYMENT.md` | Full deployment documentation |
| `DEPLOY_QUICKSTART.md` | Quick reference for deployment |

### **Modified Files**

| File | Changes |
|------|---------|
| `Dockerfile` | - Added supervisor installation<br>- Copy supervisor config and scripts<br>- Changed CMD to use `start.sh` |

---

## 🏗️ Architecture

### **Before (Not Working)**
```
Docker Container
└── Django/Gunicorn only
```
❌ Celery tasks never executed

### **After (Working)**
```
Docker Container
├── Supervisor (Process Manager)
│   ├── Django/Gunicorn (Port 8000)
│   └── Celery Worker (Background)
└── → Redis (External Render service)
```
✅ Both processes run simultaneously

---

## 🚀 Deployment Instructions

### **1. Commit Changes**

```bash
cd /root/GitHub/ALX-PD-BE/RemoSphere/remosphere-backend

git add .
git commit -m "feat: add supervisor to run Django + Celery in single container"
git push origin main
```

### **2. Environment Variables**

Ensure these are set in Render Dashboard:

```env
# Required for Celery
CELERY_BROKER_URL=redis://<your-render-redis>:6379/0
CELERY_RESULT_BACKEND=redis://<your-render-redis>:6379/1

# Required for emails
SENDGRID_API_KEY=<your-key>
DEFAULT_FROM_EMAIL=noreply@remosphere.app
```

### **3. Deploy**

Render will automatically:
1. Detect Dockerfile changes
2. Build new image
3. Deploy container
4. Start both Django and Celery

### **4. Verify**

Check Render logs for:

```
✅ Starting RemoSphere Backend Services
✅ Running database migrations...
✅ Collecting static files...
✅ Starting Django and Celery via Supervisor...
✅ supervisord started
✅ spawned: 'django' with pid XXX
✅ spawned: 'celery_worker' with pid YYY
```

---

## 🧪 Testing

### **Test Email Verification**

1. Register a new user on frontend
2. Check Render logs for:
   ```
   [celery_worker] Task authentication.email_utils.send_verification_email succeeded
   ```
3. Verify email received

### **Check Process Status (Render Shell)**

```bash
supervisorctl status

# Output should show:
# celery_worker    RUNNING   pid XXX, uptime X:XX:XX
# django           RUNNING   pid YYY, uptime X:XX:XX
```

---

## 💡 How Supervisor Works

Supervisor is a process control system that:

1. **Starts** both Django and Celery when container boots
2. **Monitors** both processes continuously
3. **Restarts** automatically if either crashes
4. **Logs** all output to stdout/stderr (visible in Render)
5. **Manages** graceful shutdown

### **Configuration Highlights**

**supervisord.conf:**
- `nodaemon=true` - Runs in foreground (required for Docker)
- `autostart=true` - Starts processes on boot
- `autorestart=true` - Auto-recovers from crashes
- `redirect_stderr=true` - Combines logs
- `stopwaitsecs=600` - 10min graceful shutdown for Celery

---

## 🔧 Troubleshooting

### **Issue: Celery still not running**

**Diagnosis:**
```bash
# 1. Check Redis connection
python -c "import redis; r=redis.from_url('$CELERY_BROKER_URL'); print(r.ping())"

# 2. Check Celery can reach broker
celery -A remosphere inspect ping

# 3. List registered tasks
celery -A remosphere inspect registered
```

**Common Causes:**
- Incorrect Redis URL
- Redis service not running
- Firewall blocking Redis
- Missing CELERY_BROKER_URL env var

### **Issue: Supervisor not starting**

**Check:**
1. start.sh has execute permissions (`chmod +x`)
2. supervisord.conf syntax is valid
3. Supervisor is installed in Dockerfile

**Debug:**
```bash
# Test supervisor config
supervisord -c /app/supervisord.conf -n

# Check supervisor logs
cat /var/log/supervisor/supervisord.log
```

### **Issue: Container crashes on startup**

**Check logs for:**
- Database connection errors
- Missing environment variables
- Migration failures
- Permission issues

---

## 📊 Production Monitoring

### **Key Metrics to Watch**

| Metric | What to Monitor |
|--------|-----------------|
| Celery Queue | Task backlog size |
| Task Success Rate | Failed vs succeeded tasks |
| Task Duration | Average task execution time |
| Worker Health | Uptime, crashes |
| Memory Usage | Per process |

### **Useful Commands**

```bash
# View Celery stats
celery -A remosphere inspect stats

# Active tasks
celery -A remosphere inspect active

# Scheduled tasks
celery -A remosphere inspect scheduled

# Revoke a task
celery -A remosphere revoke <task-id>
```

---

## 🎯 Performance Tuning

### **Celery Worker Concurrency**

Current: `--concurrency=2`

Adjust based on:
- Render plan resources
- Task complexity
- I/O vs CPU bound tasks

```bash
# Light tasks (I/O bound): Higher concurrency
--concurrency=4

# Heavy tasks (CPU bound): Lower concurrency
--concurrency=1
```

### **Gunicorn Workers**

Current: `--workers 2 --threads 2`

Formula:
```
workers = (CPU cores * 2) + 1
threads = 2-4 for I/O bound
```

---

## 🔮 Future Enhancements

### **Option 1: Celery Beat (Scheduled Tasks)**

Add to `supervisord.conf`:

```ini
[program:celery_beat]
command=celery -A remosphere beat --loglevel=info
directory=/app
user=appuser
autostart=true
autorestart=true
```

Use cases:
- Daily cleanup tasks
- Scheduled emails
- Report generation

### **Option 2: Flower (Monitoring UI)**

Add to `supervisord.conf`:

```ini
[program:flower]
command=celery -A remosphere flower --port=5555
directory=/app
user=appuser
autostart=true
autorestart=true
```

Access at: `https://your-app.onrender.com:5555`

### **Option 3: Separate Services (Scaling)**

For high traffic:
1. Run Django in one Render service
2. Run Celery in separate service
3. Share same Redis instance

---

## ✅ Checklist

Before deploying:

- [ ] All files committed and pushed
- [ ] Redis URL configured in Render
- [ ] SendGrid API key set
- [ ] start.sh is executable
- [ ] supervisord.conf syntax valid
- [ ] .dockerignore excludes sensitive files

After deploying:

- [ ] Container started successfully
- [ ] Both Django and Celery running
- [ ] Test email verification works
- [ ] Monitor logs for errors
- [ ] Check Celery task queue

---

## 📚 Resources

- [Supervisor Documentation](http://supervisord.org/)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices)
- [Render Deployment Guide](https://render.com/docs)
- [Django + Celery Patterns](https://docs.celeryq.dev/en/stable/django/)

---

## 🎉 Success Criteria

You'll know it's working when:

1. ✅ Render logs show both processes started
2. ✅ `supervisorctl status` shows both RUNNING
3. ✅ Email verification works for new users
4. ✅ Celery logs show tasks succeeding
5. ✅ No Celery-related errors in logs

---

**Questions or issues?** Check `CELERY_DEPLOYMENT.md` for detailed troubleshooting.

**Ready to deploy?** Follow the deployment instructions above! 🚀
