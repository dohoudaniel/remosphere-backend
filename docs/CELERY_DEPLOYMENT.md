# Celery + Django Deployment Guide (Render)

## Problem
Celery tasks (like email sending) were not running in production because the Docker container only ran Django/Gunicorn, not the Celery worker.

## Solution
We now run **both Django and Celery** in the same container using **Supervisor** (a process manager).

---

## How It Works

### **Architecture**
```
Docker Container (Render)
├── Supervisor (Process Manager)
│   ├── Django/Gunicorn (Port 8000)
│   └── Celery Worker (Background tasks)
└── Redis (External - Render Redis)
```

### **Files Added**

1. **`supervisord.conf`** - Supervisor configuration
   - Manages both Django and Celery as separate processes
   - Auto-restarts if either crashes
   - Logs go to stdout/stderr (visible in Render logs)

2. **`start.sh`** - Startup script
   - Runs migrations
   - Collects static files
   - Starts Supervisor

3. **Updated `Dockerfile`**
   - Installs Supervisor
   - Copies config files
   - Uses `start.sh` as CMD

---

## Environment Variables (Render)

Make sure these are set in your Render service:

```env
# Redis URL from Render Redis service
CELERY_BROKER_URL=redis://<your-redis-url>:6379/0
CELERY_RESULT_BACKEND=redis://<your-redis-url>:6379/1

# Email settings
SENDGRID_API_KEY=<your-sendgrid-key>
DEFAULT_FROM_EMAIL=noreply@remosphere.app

# Django settings
DEBUG=False
SECRET_KEY=<your-secret-key>
DATABASE_URL=<your-postgres-url>
ALLOWED_HOSTS=your-app.onrender.com
```

---

## Deployment Steps

### **1. Push Changes to GitHub**

```bash
git add supervisord.conf start.sh Dockerfile
git commit -m "feat: add supervisor to run Django + Celery in one container"
git push origin main
```

### **2. Render Will Auto-Deploy**

Render detects the Dockerfile changes and rebuilds.

### **3. Check Logs**

In Render dashboard, check logs for:

```
Starting RemoSphere Backend Services
Running database migrations...
Collecting static files...
Starting Django and Celery via Supervisor...
[INFO] supervisord started
[INFO] spawned: 'django' with pid XXX
[INFO] spawned: 'celery_worker' with pid YYY
```

### **4. Verify Celery is Working**

Test email sending:
- Register a new user
- Check Render logs for:
  ```
  [celery_worker] Task authentication.email_utils.send_verification_email succeeded
  ```

---

## Alternative: Simple Script (Without Supervisor)

If you prefer not to use Supervisor, we also created `start-simple.sh`:

```bash
# In Dockerfile, change CMD to:
CMD ["/app/start-simple.sh"]
```

**Pros:**
- Simpler, no external dependencies
- Works well for small apps

**Cons:**
- No auto-restart if Celery crashes
- Manual process management

---

## Troubleshooting

### **Issue: Celery tasks still not running**

**Check:**
1. Redis URL is correct: `echo $CELERY_BROKER_URL`
2. Celery worker started: Look for `celery_worker` in logs
3. Task is registered: `celery -A remosphere inspect registered`

### **Issue: Supervisor not starting**

**Check:**
1. File permissions: `start.sh` must be executable
2. superviso

r installed: `supervisor --version`
3. Config syntax: `supervisord -c supervisord.conf -n` (test locally)

### **Issue: Container crashes on startup**

**Check:**
1. Migration errors
2. Missing environment variables
3. Database connection

**Debug:**
```bash
# Render shell
python manage.py check
celery -A remosphere inspect ping
```

---

## Local Testing

Test the Docker setup locally:

```bash
# Build image
docker build -t remosphere-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=<local-db> \
  -e CELERY_BROKER_URL=redis://localhost:6379/0 \
  remosphere-backend

# Check logs for both Django and Celery
docker logs -f <container-id>
```

---

## Production Checklist

- [ ] Supervisor config copied to container
- [ ] start.sh is executable (`chmod +x`)
- [ ] Redis URL configured
- [ ] Celery broker and result backend set
- [ ] SendGrid API key configured
- [ ] Logs showing both Django and Celery starting
- [ ] Test email verification works
- [ ] Monitor for Celery errors in logs

---

## Monitoring

### **Check Service Health**

```bash
# In Render shell
supervisorctl status

# Should show:
# celery_worker    RUNNING   pid XXX, uptime X:XX:XX
# django           RUNNING   pid YYY, uptime X:XX:XX
```

### **Restart Celery Only**

```bash
supervisorctl restart celery_worker
```

### **View Celery Logs**

```bash
tail -f /var/log/supervisor/celery_worker.log
```

---

## Performance Tips

1. **Concurrency**: Adjust `--concurrency=2` based on Render plan
2. **Workers**: Increase Gunicorn workers for more traffic
3. **Redis**: Use Redis for caching + Celery broker
4. **Monitoring**: Use Sentry for error tracking

---

## Next Steps

1. ✅ Deploy and verify Celery works
2. Consider: Celery Beat for scheduled tasks
3. Consider: Flower for Celery monitoring UI
4. Consider: Separate Celery worker service (if scaling)

---

**Questions?** Check Render logs or contact support.
