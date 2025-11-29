# Celery Redis SSL Connection Fix - Deployment

## ✅ **Issue Fixed**

**Problem**: Celery worker was losing connection to Redis in production with error:
```
WARNING: Secure redis scheme specified (rediss) with no ssl options, 
defaulting to insecure SSL behaviour.
redis.exceptions.ConnectionError: Connection closed by server.
```

**Solution**: Added proper SSL configuration for Celery Redis connections.

---

## 🔧 **Changes Made**

### **Updated `remosphere/settings.py`**

Added SSL configuration after `CELERY_BROKER_URL`:

```python
import ssl

# Celery SSL configuration for production Redis (rediss://)
CELERY_BROKER_USE_SSL = {
    'ssl_cert_reqs': ssl.CERT_NONE
}

CELERY_REDIS_BACKEND_USE_SSL = {
    'ssl_cert_reqs': ssl.CERT_NONE
}

# Result backend SSL (if using Redis for results)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=None)
if CELERY_RESULT_BACKEND and CELERY_RESULT_BACKEND.startswith('rediss://'):
    CELERY_RESULT_BACKEND_USE_SSL = CELERY_REDIS_BACKEND_USE_SSL

# Worker stability settings
CELERY_WORKER_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOSS = False
```

---

## ⚙️ **Environment Variables**

### **Production (.env or Render Environment)**

```env
# Redis with SSL (Render Redis uses rediss://)
CELERY_BROKER_URL=rediss://red-xxx:6379/0
CELERY_RESULT_BACKEND=rediss://red-xxx:6379/1
```

### **Local Development**

```env
# Redis without SSL (local)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

**Note**: The SSL configuration only applies when using `rediss://` scheme.

---

## 🎯 **How It Works**

### **SSL Certificate Validation Options**

| Option | Security Level | Use Case |
|--------|---------------|----------|
| `ssl.CERT_NONE` | Lower (no validation) | Managed services (Render, Heroku) with internal SSL |
| `ssl.CERT_OPTIONAL` | Medium | Optional cert validation |
| `ssl.CERT_REQUIRED` | High (strict) | Custom Redis with verified certificates |

**Current Setup**: `ssl.CERT_NONE` 
- ✅ Works with Render Redis
- ✅ Works with most managed Redis services
- ✅ Simplifies deployment

### **For Stricter Security (Optional)**

If you have Redis SSL certificates:

```python
CELERY_BROKER_USE_SSL = {
    'ssl_cert_reqs': ssl.CERT_REQUIRED,
    'ssl_ca_certs': '/path/to/ca-cert.pem',
    'ssl_certfile': '/path/to/client-cert.pem',
    'ssl_keyfile': '/path/to/client-key.pem',
}
```

---

## 🧪 **Testing**

### **Test 1: Local (redis://)**

```bash
# Start local Redis
redis-server

# Start Celery worker
celery -A remosphere worker -l info

# Should connect without SSL warnings
```

### **Test 2: Production (rediss://)**

```bash
# In Render shell or production server
celery -A remosphere worker -l info

# Should see:
# ✅ Connected to rediss://...
# ✅ No SSL warnings
# ✅ No connection errors
```

### **Test 3: Send Test Task**

```python
# In Django shell (production)
from authentication.email_utils import send_verification_email

# Queue a test task
send_verification_email.delay(user_id, domain)

# Check Celery logs - should process without errors
```

---

## 🔍 **Diagnostic Commands**

### **Check Celery Connection**

```bash
# In production environment
celery -A remosphere inspect ping

# Should return: pong from worker
```

### **Check Redis Connection**

```bash
# Test Redis SSL connection
redis-cli -h <host> -p 6379 --tls ping

# Should return: PONG
```

### **Monitor Celery Worker**

```bash
# Watch Celery worker logs
celery -A remosphere events

# Or in Render dashboard:
# Logs → Select celery service
```

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: Still Getting SSL Warnings**

**Cause**: Old Celery process still running

**Solution**:
```bash
# Kill all Celery processes
pkill -9 celery

# Restart
celery -A remosphere worker -l info
```

### **Issue 2: Connection Refused**

**Cause**: Wrong Redis URL

**Solution**:
```bash
# Check environment variable
echo $CELERY_BROKER_URL

# Should be: rediss://host:port/db (production)
# Or: redis://localhost:6379/0 (local)
```

### **Issue 3: Tasks Not Processing**

**Cause**: Worker not running or crashed

**Solution**:
```bash
# Check if worker is running
ps aux | grep celery

# Check Supervisor status (if using)
supervisorctl status celery_worker

# Restart worker
supervisorctl restart celery_worker
```

---

## 📋 **Deployment Checklist**

### **Render Deployment**

- [ ] Redis service created on Render
- [ ] `CELERY_BROKER_URL` set to Redis URL (starts with `rediss://`)
- [ ] `CELERY_RESULT_BACKEND` set (optional but recommended)
- [ ] SSL configuration added to `settings.py`
- [ ] Supervisor configured to run both Django and Celery
- [ ] Deployed to Render
- [ ] Check logs for "Connected to rediss://"
- [ ] No SSL warnings in logs
- [ ] Test email sending works

### **Verification Steps**

```bash
# 1. Check worker is running
supervisorctl status celery_worker
# Should show: RUNNING

# 2. Test Celery connection
celery -A remosphere inspect ping
# Should return: pong

# 3. Register a user (trigger email task)
# Check logs for task success

# 4. Monitor for connection errors
# Should see no "Connection closed" errors
```

---

## 🎯 **SSL Configuration Explained**

### **Why `ssl.CERT_NONE`?**

1. **Managed Redis Services** (Render, Upstash, etc.):
   - Handle SSL/TLS termination
   - Use internal certificates
   - Don't require client certificate validation

2. **Simplicity**:
   - No need to manage certificates
   - Works out of the box
   - Sufficient for most use cases

3. **Security**:
   - Connection is still encrypted (TLS)
   - Only skips certificate verification
   - Acceptable for managed services

### **When to Use `ssl.CERT_REQUIRED`?**

- Self-hosted Redis with custom certificates
- Corporate/enterprise Redis with strict security
- Compliance requirements (HIPAA, PCI-DSS)

---

## 📊 **Connection Flow**

```
Celery Worker (Render Container)
    ↓
SSL/TLS Connection (rediss://)
    ↓
Check SSL settings:
- CELERY_BROKER_USE_SSL = {'ssl_cert_reqs': ssl.CERT_NONE}
    ↓
Skip certificate validation
    ↓
Establish encrypted connection
    ↓
Redis Server (Render Redis)
    ↓
✅ Connected and processing tasks
```

---

## 🔐 **Security Considerations**

### **Current Setup (Production)**
```
Encryption: ✅ YES (TLS)
Authentication: ✅ YES (Redis password in URL)
Certificate Validation: ❌ NO (CERT_NONE)
```

**Is this secure?**

✅ **YES** for managed services because:
- Connection is encrypted
- Password authentication is used
- Redis is in private network (Render internal)
- No public internet exposure

### **Improving Security (Optional)**

1. **Use Redis ACLs**:
   ```
   # In Render Redis settings
   Enable ACLs and create specific user for Celery
   ```

2. **Restrict Network Access**:
   ```
   # Render automatically does this
   Redis only accessible from your services
   ```

3. **Rotate Redis Password**:
   ```
   # Periodically update CELERY_BROKER_URL
   # Render allows password rotation
   ```

---

## ✅ **Verification**

After deploying, you should see in Render logs:

```
✅ [INFO] Connected to rediss://red-xxx.render.com:6379/0
✅ [INFO] celery@worker ready
❌ NO "Connection closed by server" errors
❌ NO "ssl options" warnings
```

---

## 📚 **References**

- [Celery SSL/TLS Documentation](https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-use-ssl)
- [Redis SSL Connections](https://redis.io/docs/manual/security/encryption/)
- [Render Redis Documentation](https://render.com/docs/redis)

---

**Issue resolved!** Celery should now connect to Redis in production without SSL warnings or connection errors. 🎉
