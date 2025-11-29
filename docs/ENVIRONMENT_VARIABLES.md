# Environment Variables Setup Guide

## 📋 **Required Environment Variables**

### **New Variables Added in This Session**

| Variable | Required | Purpose | Example |
|----------|----------|---------|---------|
| `FRONTEND_URL` | ✅ Yes | Frontend URL for email verification redirects | `http://localhost:8080` (local)<br>`https://remosphere.vercel.app` (prod) |
| `CELERY_BROKER_URL` | ✅ Yes | Redis URL for Celery task queue | `redis://localhost:6379/0` (local)<br>`rediss://red-xxx:6379/0` (prod) |
| `CELERY_RESULT_BACKEND` | ⚠️ Recommended | Redis URL for task results storage | `redis://localhost:6379/1` (local)<br>`rediss://red-xxx:6379/1` (prod) |

---

## 🔧 **Local Development Setup**

### **1. Create/Update `.env` file**

```bash
cd /root/GitHub/ALX-PD-BE/RemoSphere/remosphere-backend
cp .env.example .env
```

### **2. Configure Local Environment**

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SITE_URL=http://localhost:8000

# Frontend URL (for email verification)
FRONTEND_URL=http://localhost:8080

# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# JWT
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=your-jwt-secret

# Celery (Local Redis - no SSL)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Email (SendGrid or Brevo)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@remosphere.app

# Brevo (if using instead of SendGrid)
BREVO_API_KEY=your-brevo-api-key
```

### **3. Start Local Redis**

```bash
# Install Redis (if not installed)
sudo apt install redis-server  # Ubuntu/Debian
# or
brew install redis  # macOS

# Start Redis
redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

---

## 🚀 **Production Setup (Render)**

### **Required Services on Render**

1. ✅ **PostgreSQL** - Database
2. ✅ **Redis** - Celery broker (provides `rediss://` URL)
3. ✅ **Web Service** - Django + Celery (Docker)

### **Environment Variables in Render**

Go to your Render service → **Environment** tab and add:

```env
# Django
SECRET_KEY=<generate-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
SITE_URL=https://your-app.onrender.com

# Frontend URL (Vercel deployment)
FRONTEND_URL=https://remosphere.vercel.app

# Database (auto-populated by Render PostgreSQL)
DATABASE_URL=<render-provides-this>

# JWT
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=<generate-strong-jwt-secret>

# Celery (Render Redis - with SSL)
CELERY_BROKER_URL=<copy-from-render-redis-internal-url>
CELERY_RESULT_BACKEND=<same-redis-url-but-db-1>

# Example Render Redis URLs:
# CELERY_BROKER_URL=rediss://red-abc123:6379/0
# CELERY_RESULT_BACKEND=rediss://red-abc123:6379/1

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<your-sendgrid-api-key>
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@remosphere.app

# Brevo (optional)
BREVO_API_KEY=<your-brevo-api-key>

# Password Reset
PASSWORD_RESET_TOKEN_LIFETIME_MINUTES=30
PASSWORD_RESET_RATE_LIMIT_PER_HOUR=5
PASSWORD_RESET_RATE_LIMIT_IP_PER_HOUR=20
PASSWORD_RESET_SIGNING_KEY=<strong-signing-key>
PASSWORD_RESET_ALGORITHM=HS256
```

---

## 🔑 **How to Get Render Redis URL**

### **Option 1: From Render Dashboard**

1. Go to Render Dashboard
2. Click on your Redis instance
3. Copy **Internal Connection String**
4. It will look like: `rediss://red-xxx:6379`

### **Option 2: Create Redis Instance**

If you haven't created Redis yet:

1. In Render Dashboard → **New** → **Redis**
2. Choose a name: `remosphere-redis`
3. Select plan: **Free** (sufficient for development)
4. Click **Create Redis**
5. Once created, copy the **Internal Connection String**

### **Using Redis URL**

```env
# Broker (database 0)
CELERY_BROKER_URL=rediss://red-xxx:6379/0

# Result backend (database 1)
CELERY_RESULT_BACKEND=rediss://red-xxx:6379/1
```

**Note**: `/0` and `/1` are database numbers in Redis (0-15 available)

---

## ⚠️ **Important Notes**

### **1. Redis Scheme Differences**

| Environment | Scheme | SSL | Example |
|-------------|--------|-----|---------|
| **Local** | `redis://` | No | `redis://localhost:6379/0` |
| **Production** | `rediss://` | Yes | `rediss://red-xxx:6379/0` |

**Don't mix them up!** The SSL configuration in `settings.py` auto-detects `rediss://` and applies SSL.

### **2. Frontend URL**

Must match your actual frontend deployment:

- Local: `http://localhost:8080`
- Production: `https://remosphere.vercel.app`

If wrong, email verification links will go to wrong domain!

### **3. Database vs Database URL**

Render provides `DATABASE_URL` which overrides individual DB settings:

```env
# If using DATABASE_URL (Render auto-provides this)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Individual settings not needed when using DATABASE_URL
# DB_NAME, DB_USER, etc. are ignored
```

---

## ✅ **Verification Checklist**

### **Local Development**

- [ ] `.env` file created with all variables
- [ ] Redis installed and running (`redis-cli ping` returns PONG)
- [ ] `FRONTEND_URL=http://localhost:8080`
- [ ] `CELERY_BROKER_URL=redis://localhost:6379/0` (no 's')
- [ ] Email credentials configured
- [ ] Test: `python manage.py runserver` works
- [ ] Test: `celery -A remosphere worker -l info` works

### **Production (Render)**

- [ ] PostgreSQL service created
- [ ] Redis service created
- [ ] All environment variables set in Render dashboard
- [ ] `FRONTEND_URL=https://remosphere.vercel.app`
- [ ] `CELERY_BROKER_URL=rediss://...` (with 's')
- [ ] Deployed successfully
- [ ] Check logs: "Connected to rediss://..."
- [ ] Test: Register user → Email received
- [ ] Test: Verification link works

---

## 🧪 **Testing Environment Variables**

### **Test 1: Check Variables are Loaded**

```python
# In Django shell
python manage.py shell

from django.conf import settings

# Check variables
print(settings.FRONTEND_URL)  # Should print your frontend URL
print(settings.CELERY_BROKER_URL)  # Should print Redis URL
print(settings.DEBUG)  # False in production, True locally
```

### **Test 2: Test Redis Connection**

```bash
# Local
redis-cli ping

# Production (from Render shell)
redis-cli -h <redis-host> -p 6379 --tls ping
```

### **Test 3: Test Celery**

```bash
# Start Celery worker
celery -A remosphere worker -l info

# Should see:
# - Connected to redis://... (local) or rediss://... (prod)
# - No errors
# - Ready to process tasks
```

---

## 🔐 **Security Best Practices**

### **DO:**
- ✅ Use strong, random `SECRET_KEY` and `JWT_SECRET_KEY`
- ✅ Set `DEBUG=False` in production
- ✅ Use `rediss://` (SSL) for production Redis
- ✅ Keep `.env` in `.gitignore`
- ✅ Use environment variables manager (Render, Vercel)

### **DON'T:**
- ❌ Commit `.env` to Git
- ❌ Use same secrets for local and production
- ❌ Share secrets in plain text
- ❌ Use `DEBUG=True` in production
- ❌ Use `redis://` (no SSL) in production

---

## 📝 **Quick Reference**

### **Essential Commands**

```bash
# Copy example env
cp .env.example .env

# Edit env file
nano .env  # or vim, code, etc.

# Check Redis
redis-cli ping

# Start Celery
celery -A remosphere worker -l info

# Django shell
python manage.py shell

# Check environment
python manage.py check
```

---

## 🆘 **Troubleshooting**

### **Issue: Email verification links go to wrong domain**

**Fix**: Check `FRONTEND_URL` matches your frontend deployment

```bash
# Local should be:
FRONTEND_URL=http://localhost:8080

# Production should be:
FRONTEND_URL=https://remosphere.vercel.app
```

### **Issue: Celery can't connect to Redis**

**Fix**: Verify `CELERY_BROKER_URL` is correct

```bash
# Local (no SSL)
CELERY_BROKER_URL=redis://localhost:6379/0

# Production (with SSL)  
CELERY_BROKER_URL=rediss://red-xxx:6379/0
```

### **Issue: SSL warnings in production**

**Fix**: Already fixed in `settings.py` with SSL configuration. Just make sure URL uses `rediss://` (with 's')

---

**All environment variables are now documented and configured!** 🎉

For more details, see:
- `.env.example` - Template with all variables
- `CELERY_REDIS_SSL_FIX.md` - SSL configuration details
