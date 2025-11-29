# Celery Email Not Working - Production Troubleshooting

## 🔍 **Diagnostic Steps**

### **Step 1: Check if Celery Worker is Running**

```bash
# In Render Shell
supervisorctl status

# Should show:
# celery_worker    RUNNING   pid XXX, uptime X:XX:XX
# django           RUNNING   pid YYY, uptime Y:YY:YY

# If NOT running:
supervisorctl start celery_worker
```

**If Celery is not in the list**, check if supervisor config includes it.

---

### **Step 2: Check Celery Worker Logs**

```bash
# View real-time logs
supervisorctl tail -f celery_worker

# Or view last 100 lines
supervisorctl tail celery_worker

# Look for:
# ✅ "Connected to rediss://..."
# ✅ "celery@worker ready"
# ❌ Connection errors
# ❌ Import errors
# ❌ Configuration errors
```

---

### **Step 3: Check Redis Connection**

```bash
# Test Celery can reach Redis
celery -A remosphere inspect ping

# Should return:
# -> celery@worker: OK
#     pong

# If fails: Redis connection issue
```

---

### **Step 4: Check if Tasks are Registered**

```bash
# List registered tasks
celery -A remosphere inspect registered

# Should include:
# - authentication.email_utils.send_verification_email
# - authentication.email_utils.send_welcome_email
# - authentication.email_utils.send_password_reset_email

# If missing: Import/configuration issue
```

---

### **Step 5: Check Task Queue**

```bash
# Check active tasks
celery -A remosphere inspect active

# Check scheduled tasks
celery -A remosphere inspect scheduled

# Check if tasks are stuck
celery -A remosphere inspect reserved
```

---

### **Step 6: Test Email Sending Manually**

```bash
# Django shell
python manage.py shell

# Test email directly
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@example.com'],
)

# If this fails: Email settings issue
# If this works: Celery configuration issue
```

---

### **Step 7: Queue a Test Task**

```python
# In Django shell
from authentication.email_utils import send_verification_email
from users.models import User

# Get a user
user = User.objects.first()

# Queue task manually
result = send_verification_email.delay(user.id, 'http://localhost:8000')

# Check task ID
print(f"Task ID: {result.id}")

# Check task status
from celery.result import AsyncResult
task = AsyncResult(result.id)
print(f"Status: {task.state}")
print(f"Result: {task.result}")

# States: PENDING, STARTED, SUCCESS, FAILURE, RETRY
```

---

## 🐛 **Common Issues & Fixes**

### **Issue 1: Celery Worker Not Running**

**Symptoms:**
- `supervisorctl status` shows celery_worker as STOPPED or FATAL
- No celery logs

**Diagnosis:**
```bash
# Check supervisor logs
cat /var/log/supervisor/supervisord.log
cat /var/log/supervisor/celery_worker-*.log
```

**Common Causes:**
1. Import errors in code
2. Redis connection failed
3. Missing environment variables

**Fix:**
```bash
# Restart celery
supervisorctl restart celery_worker

# If still failing, check error logs
supervisorctl tail celery_worker stderr
```

---

### **Issue 2: Redis Connection Failed**

**Symptoms:**
- "Connection refused" errors
- "Connection closed by server" errors
- Worker keeps restarting

**Check Environment Variables:**
```bash
# In Render Shell
echo $CELERY_BROKER_URL
echo $CELERY_RESULT_BACKEND

# Should be:
# rediss://red-xxx.render.com:6379/0  (with 's' for SSL)
```

**Verify Redis Service:**
1. Go to Render Dashboard
2. Check Redis service is **RUNNING**
3. Copy **Internal Connection String**
4. Ensure it's set in environment variables

**Test Connection:**
```bash
# From Render shell
redis-cli -u $CELERY_BROKER_URL ping
# Should return: PONG
```

---

### **Issue 3: Email Settings Incorrect**

**Symptoms:**
- Task succeeds but no email received
- SMTP errors in logs

**Check Email Configuration:**
```python
# Django shell
from django.conf import settings

print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
# Don't print EMAIL_HOST_PASSWORD for security
```

**Common Issues:**
- Wrong SendGrid API key
- `DEFAULT_FROM_EMAIL` not set
- `EMAIL_USE_TLS=False` (should be True for SendGrid)

**Test SendGrid API Key:**
```bash
# Test with curl
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [{"to": [{"email": "test@example.com"}]}],
    "from": {"email": "noreply@remosphere.app"},
    "subject": "Test",
    "content": [{"type": "text/plain", "value": "Test"}]
  }'

# Should return: 202 Accepted
```

---

### **Issue 4: Tasks Not Being Queued**

**Symptoms:**
- No tasks in queue
- `inspect active` returns empty

**Check Task Call:**
```python
# In your code, verify you're calling .delay()
send_verification_email.delay(user.id, domain)
# NOT: send_verification_email(user.id, domain)
```

**Check Logs:**
```bash
# Django logs should show:
# "Task authentication.email_utils.send_verification_email[task-id] received"
```

---

### **Issue 5: Import Errors**

**Symptoms:**
- Celery worker won't start
- "No module named..." errors

**Check Celery Can Import Task:**
```bash
# In Render shell
python -c "from authentication.email_utils import send_verification_email; print('OK')"

# Should print: OK
# If error: Check imports and dependencies
```

---

### **Issue 6: Environment Variables Missing**

**Required Variables in Render:**

```env
✅ CELERY_BROKER_URL=rediss://red-xxx:6379/0
✅ CELERY_RESULT_BACKEND=rediss://red-xxx:6379/1
✅ EMAIL_HOST=smtp.sendgrid.net
✅ EMAIL_HOST_USER=apikey
✅ EMAIL_HOST_PASSWORD=SG.xxxxx
✅ EMAIL_PORT=587
✅ EMAIL_USE_TLS=True
✅ DEFAULT_FROM_EMAIL=noreply@remosphere.app
✅ FRONTEND_URL=https://remosphere.vercel.app
```

**Check All Are Set:**
```bash
# List all environment variables
env | grep CELERY
env | grep EMAIL
env | grep FRONTEND
```

---

## 📊 **Monitoring Commands**

### **Real-Time Monitoring**

```bash
# Watch Celery logs
supervisorctl tail -f celery_worker

# Watch Django logs
supervisorctl tail -f django

# Watch all logs
tail -f /var/log/supervisor/*.log
```

### **Check Task Stats**

```bash
# Celery stats
celery -A remosphere inspect stats

# Shows:
# - Total tasks received
# - Total tasks completed
# - Active tasks
# - Registered tasks
```

---

## 🔧 **Quick Fixes**

### **Fix 1: Restart Everything**

```bash
# Restart all services
supervisorctl restart all

# Or individually:
supervisorctl restart celery_worker
supervisorctl restart django
```

### **Fix 2: Clear Redis Queue**

```bash
# WARNING: This clears ALL tasks
redis-cli -u $CELERY_BROKER_URL FLUSHDB

# Then restart worker
supervisorctl restart celery_worker
```

### **Fix 3: Verify Supervisor Config**

Check `/app/supervisord.conf`:

```ini
[program:celery_worker]
command=celery -A remosphere worker --loglevel=info --concurrency=2
directory=/app
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
```

---

## 📝 **Step-by-Step Debugging Checklist**

Run these commands in order:

```bash
# 1. Check services running
supervisorctl status
# ✅ Both django and celery_worker should be RUNNING

# 2. Check Redis connection
celery -A remosphere inspect ping
# ✅ Should return: pong

# 3. Check registered tasks
celery -A remosphere inspect registered
# ✅ Should list email tasks

# 4. Check for active tasks
celery -A remosphere inspect active
# ✅ Shows currently processing tasks

# 5. Check Celery logs
supervisorctl tail celery_worker
# ✅ Look for errors

# 6. Test email directly
python manage.py shell
>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail('Test', 'Body', settings.DEFAULT_FROM_EMAIL, ['you@example.com'])
# ✅ Should return: 1

# 7. Queue a test task
>>> from authentication.email_utils import send_verification_email
>>> from users.models import User
>>> user = User.objects.first()
>>> send_verification_email.delay(user.id, 'http://test.com')
# ✅ Should return: AsyncResult object

# 8. Check Celery processed it
# Exit shell, then:
supervisorctl tail celery_worker
# ✅ Should show task execution
```

---

## 🎯 **Expected Working Output**

### **Supervisor Status**
```
celery_worker    RUNNING   pid 123, uptime 1:23:45
django           RUNNING   pid 456, uptime 1:23:45
```

### **Celery Worker Logs**
```
[INFO] Connected to rediss://red-xxx.render.com:6379/0
[INFO] celery@worker v5.x.x ready
[INFO] Task authentication.email_utils.send_verification_email[abc-123] received
[INFO] Task authentication.email_utils.send_verification_email[abc-123] succeeded in 1.2s
```

### **Django Logs (on Registration)**
```
[INFO] User registered: user@example.com
[INFO] Queueing verification email task
[INFO] Task queued: abc-123
```

---

## 🆘 **Still Not Working?**

### **Get Full Diagnostic Report**

```bash
# Save this output and share it
echo "=== Supervisor Status ==="
supervisorctl status

echo -e "\n=== Celery Worker Logs ==="
supervisorctl tail celery_worker | tail -50

echo -e "\n=== Environment Variables ==="
env | grep -E '(CELERY|EMAIL|FRONTEND)' | sed 's/PASSWORD=.*/PASSWORD=***/'

echo -e "\n=== Celery Inspect ==="
celery -A remosphere inspect ping
celery -A remosphere inspect registered | head -20

echo -e "\n=== Redis Connection ==="
redis-cli -u $CELERY_BROKER_URL ping
```

---

## 💡 **Pro Tips**

1. **Always check Supervisor status first**
   ```bash
   supervisorctl status
   ```

2. **Monitor logs in real-time when testing**
   ```bash
   supervisorctl tail -f celery_worker
   # In another terminal, trigger a task
   ```

3. **Test email settings directly before testing Celery**
   - If direct email fails, Celery won't help
   - Fix email settings first

4. **Use Render logs dashboard**
   - Real-time log streaming
   - Filter by service
   - Search functionality

---

**Follow these steps systematically to identify the issue!** 🔍
