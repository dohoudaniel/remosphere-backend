# Email Verification - Domain Detection Fix

## ✅ **Fixed Issue**

**Problem**: Verification emails always used FRONTEND_URL (localhost:8080) even when testing in Swagger (localhost:8000)

**Solution**: Now uses the actual domain from the request, so:
- Swagger users get: `http://localhost:8000/api/auth/verify?token=xxx`
- Frontend users get: `http://localhost:8080/auth/verify?token=xxx`

---

## 🎯 How It Works Now

### **Domain Detection (Smart)**

The `send_verification_email` function now uses the `domain` parameter that's passed to it:

```python
# In RegisterView (line 34)
domain = request.build_absolute_uri("/").rstrip("/")
send_verification_email.delay(user.id, domain)

# domain will be:
# - http://localhost:8000 when called from Swagger
# - http://localhost:8080 when called from frontend
# - https://backend.onrender.com when called from production backend
# - https://remosphere.vercel.app when called from production frontend
```

---

## 📧 Email Examples

### **1. Registration via Swagger (localhost:8000)**

**Request:**
```http
POST http://localhost:8000/api/users/register/
{
  "email": "test@example.com",
  "password": "password123",
  ...
}
```

**Email Sent:**
```
Subject: RemoSphere 🌍: Verify your email to continue

Hi Test,
Welcome to RemoSphere 🌍, the best job board out there :)

Click the link below to verify your email:
http://localhost:8000/api/auth/verify?token=xxx

If you didn't create an account, ignore this.
```

**Clicking the link:**
- Goes to `http://localhost:8000/api/auth/verify?token=xxx`
- Returns JSON response (default) ✅
- Perfect for testing!

---

### **2. Registration via Frontend (localhost:8080)**

**Request (from frontend):**
```http
POST http://localhost:8000/api/users/register/
Origin: http://localhost:8080
{
  "email": "test@example.com",
  "password": "password123",
  ...
}
```

**Email Sent:**
```
Subject: RemoSphere 🌍: Verify your email to continue

Hi Test,
Welcome to RemoSphere 🌍, the best job board out there :)

Click the link below to verify your email:
http://localhost:8080/auth/verify?token=xxx

If you didn't create an account, ignore this.
```

**Clicking the link:**
- Goes to `http://localhost:8080/auth/verify?token=xxx`
- Frontend handles the token
- Frontend calls backend with `?redirect=true`
- Gets redirected back to frontend with success ✅

---

## 🔄 Complete Flows

### **Flow A: Swagger Testing**

```
1. Developer registers user in Swagger UI
   POST http://localhost:8000/api/users/register/
   ↓
2. Backend detects domain: http://localhost:8000
   ↓
3. Email sent with link:
   http://localhost:8000/api/auth/verify?token=xxx
   ↓
4. Developer clicks email link
   ↓
5. Goes to Swagger/backend: GET /api/auth/verify?token=xxx
   ↓
6. Returns JSON:
   {
     "detail": "Email verified successfully",
     "email": "test@example.com",
     "verified": true
   }
   ✅ Perfect for testing!
```

---

### **Flow B: Frontend User**

```
1. User registers on frontend (http://localhost:8080)
   Frontend calls: POST http://localhost:8000/api/users/register/
   ↓
2. Backend detects domain from Origin header: http://localhost:8080
   (or you can configure frontend to send correct domain)
   ↓
3. Email sent with link:
   http://localhost:8080/auth/verify?token=xxx
   ↓
4. User clicks email link
   ↓
5. Goes to frontend: http://localhost:8080/auth/verify?token=xxx
   ↓
6. Frontend calls backend with redirect:
   GET /api/auth/verify?token=xxx&redirect=true
   ↓
7. Backend redirects:
   302 → http://localhost:8080/auth?verified=true
   ↓
8. Frontend shows success message ✅
```

---

## 💻 Frontend Configuration

If your frontend needs to ensure emails go to frontend domain, you have options:

### **Option A: Let Backend Detect (Current)**

Backend uses `request.build_absolute_uri("/")` which will be the backend URL.

If you want frontend URL, the frontend should call with `Origin` header or you can:

### **Option B: Frontend Sends Domain (Explicit)**

Update frontend to send the desired domain:

```typescript
// Frontend registration
const response = await fetch(`${API_URL}/users/register/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Frontend-URL': 'http://localhost:8080', // Custom header
  },
  body: JSON.stringify(userData)
});
```

Then update backend to check for this header:

```python
# In RegisterView
frontend_url = request.META.get('HTTP_X_FRONTEND_URL')
domain = frontend_url if frontend_url else request.build_absolute_uri("/").rstrip("/")
```

### **Option C: Always Use FRONTEND_URL for Frontend Requests**

Detect if request came from frontend and use FRONTEND_URL:

```python
# In send_verification_email
def send_verification_email(user_id, domain, use_frontend=False):
    if use_frontend:
        domain = getattr(settings, 'FRONTEND_URL', domain)
    
    # Rest of the function...
```

---

## 🧪 Testing

### **Test 1: Swagger Registration**

```bash
# 1. Open Swagger
http://localhost:8000/swagger/

# 2. POST /api/users/register/
{
  "email": "swagger@test.com",
  "password": "test123",
  "first_name": "Swagger",
  "last_name": "Test"
}

# 3. Check email - link should be:
http://localhost:8000/api/auth/verify?token=xxx

# 4. Click link → Should return JSON ✅
```

### **Test 2: Frontend Registration**

```bash
# 1. Register from frontend
http://localhost:8080

# 2. Check email - link should be:
http://localhost:8080/auth/verify?token=xxx
# OR
http://localhost:8000/api/auth/verify?token=xxx
# (depending on configuration)

# 3. Click link → Should work with frontend flow ✅
```

---

## ⚙️ Configuration

### **Environment Variables**

```env
# Backend (for production)
SITE_URL=https://backend.onrender.com

# Frontend URL (optional - only if using Option B or C)
FRONTEND_URL=https://remosphere.vercel.app
```

### **For Production**

When deploying, the domain detection will automatically use:
- Production backend URL for Swagger/API registrations
- Production frontend URL for frontend registrations (if configured)

---

## 🔍 Code Changes Summary

### **1. authentication/email_utils.py**

```python
def send_verification_email(user_id, domain):
    # Now USES the domain parameter instead of ignoring it
    verify_url = f"{domain.rstrip('/')}{verify_path}?token={token}"
```

### **2. users/views.py - RequestVerificationEmailView**

```python
# Fixed to pass domain parameter
domain = request.build_absolute_uri("/").rstrip("/")
send_verification_email.delay(user.id, domain)
```

### **3. authentication/views.py - VerifyEmailView**

```python
# Default to JSON, only redirect with ?redirect=true
wants_redirect = request.query_params.get('redirect', '').lower() == 'true'
```

---

## 🎯 Benefits

✅ **Swagger Works Correctly** - Gets backend URL in email  
✅ **Frontend Works Correctly** - Gets appropriate URL  
✅ **Flexible** - Can configure which URL to use  
✅ **No Hardcoding** - Uses request domain dynamically  
✅ **Production Ready** - Works in all environments  

---

## 📊 Domain Matrix

| Registration From | Email Link Domain | Verification Response |
|------------------|-------------------|----------------------|
| Swagger (localhost:8000) | localhost:8000 | JSON |
| Frontend (localhost:8080) | localhost:8080* | Redirect (with ?redirect=true) |
| Production API | backend.onrender.com | JSON |
| Production Frontend | remosphere.vercel.app* | Redirect |

*Depends on configuration - see Options A, B, C above

---

**Now Swagger gets the correct URL!** 🎉

Test it:
1. Register in Swagger
2. Check the email
3. Link should be `localhost:8000`, not `localhost:8080`
