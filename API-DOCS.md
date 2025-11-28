# RemoSphere API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
RemoSphere uses JWT (JSON Web Tokens) for authentication with cookie-based sessions.

### Authentication Methods
1. **JWT Bearer Token**: Include in `Authorization` header as `Bearer <token>`
2. **HttpOnly Cookies**: Automatically set after login (`access_token` and `refresh_token`)

---

## Table of Contents
1. [User Management](#user-management)
2. [Authentication](#authentication-endpoints)
3. [Jobs](#jobs)
4. [Categories](#categories)
5. [Companies](#companies)
6. [Applications](#applications)
7. [Documentation Endpoints](#documentation-endpoints)

---

## User Management

### Register User
Creates a new user account and sends a verification email.

**Endpoint:** `POST /api/users/register/`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123!"
}
```

**Response:** `201 Created`
```json
{
  "detail": "User successfully signed up. Please check your email for verification."
}
```

**Validation:**
- Password must meet strength requirements (at least 8 characters, mixed case, numbers, special characters)
- Email must be unique
- All fields are required

---

### Login
Authenticates a user and returns JWT tokens.

**Endpoint:** `POST /api/users/login/`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_admin": false,
    "email_verified": true,
    "date_joined": "2025-11-28T05:00:00Z",
    "last_login": "2025-11-28T06:00:00Z"
  }
}
```

**Cookies Set:**
- `access_token` (HttpOnly, 60 min lifetime)
- `refresh_token` (HttpOnly, 24 hours lifetime)

**Error Responses:**
- `400`: Invalid email or password
- `403`: Email not verified

---

### Logout
Invalidates the refresh token and clears authentication cookies.

**Endpoint:** `POST /api/users/logout/`

**Authentication:** Required (JWT or Cookie)

**Response:** `200 OK`
```json
{
  "detail": "Logged out successfully"
}
```

---

## Authentication Endpoints

### Request Email Verification
Request a new email verification link.

**Endpoint:** `POST /api/auth/request-verification/`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Verification email sent"
}
```

---

### Verify Email
Verify email address using the token sent via email.

**Endpoint:** `POST /api/auth/verify-email/`

**Authentication:** Not required

**Request Body:**
```json
{
  "token": "verification_token_here"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Email verified successfully"
}
```

---

### Forgot Password
Request a password reset email.

**Endpoint:** `POST /api/auth/forgot-password/`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Password reset email sent"
}
```

---

### Reset Password
Reset password using the token sent via email.

**Endpoint:** `POST /api/auth/reset-password/`

**Authentication:** Not required

**Request Body:**
```json
{
  "token": "reset_token_here",
  "password": "NewSecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Password reset successfully"
}
```

---

## Jobs

### List Jobs
Retrieve a list of all active job postings with filtering, searching, and ordering.

**Endpoint:** `GET /api/jobs/`

**Authentication:** Required (authenticated users only)

**Query Parameters:**
- `search` (string): Search in title, description, category name, company name, location, job type
- `category__name` (string): Filter by exact category name
- `company_name` (string): Filter by exact company name
- `location` (string): Filter by exact location
- `job_type` (string): Filter by job type (`full_time`, `part_time`, `contract`, `internship`, `remote`, `other`)
- `is_active` (boolean): Filter by active status
- `ordering` (string): Sort by field (prefix with `-` for descending): `created_at`, `updated_at`, `title`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Senior Software Engineer",
    "description": "We are looking for an experienced software engineer...",
    "category": 1,
    "category_name": "Engineering",
    "location": "Remote",
    "job_type": "full_time",
    "salary_range": "$100,000 - $150,000",
    "company_name": "Tech Corp",
    "company": 1,
    "created_by": "admin@example.com",
    "created_at": "2025-11-28T05:00:00Z",
    "updated_at": "2025-11-28T05:00:00Z",
    "is_active": true,
    "slug": "https://example.com/jobs/senior-software-engineer",
    "expiry_at": null,
    "applications_count": 5
  }
]
```

**Permissions:**
- Authenticated users can view active jobs
- Admins can view all jobs (including inactive)

---

### Retrieve Job
Get details of a specific job.

**Endpoint:** `GET /api/jobs/{id}/`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Senior Software Engineer",
  "description": "We are looking for an experienced software engineer...",
  "category": 1,
  "category_name": "Engineering",
  "location": "Remote",
  "job_type": "full_time",
  "salary_range": "$100,000 - $150,000",
  "company_name": "Tech Corp",
  "company": 1,
  "created_by": "admin@example.com",
  "created_at": "2025-11-28T05:00:00Z",
  "updated_at": "2025-11-28T05:00:00Z",
  "is_active": true,
  "slug": "https://example.com/jobs/senior-software-engineer",
  "expiry_at": null,
  "applications_count": 5
}
```

---

### Create Job
Create a new job posting (Admin only).

**Endpoint:** `POST /api/jobs/`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "title": "Senior Software Engineer",
  "description": "We are looking for an experienced software engineer...",
  "category": 1,
  "location": "Remote",
  "job_type": "full_time",
  "salary_range": "$100,000 - $150,000",
  "company_name": "Tech Corp",
  "company": 1,
  "is_active": true,
  "expiry_at": "2025-12-31T23:59:59Z"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "title": "Senior Software Engineer",
  "description": "We are looking for an experienced software engineer...",
  "category": 1,
  "category_name": "Engineering",
  "location": "Remote",
  "job_type": "full_time",
  "salary_range": "$100,000 - $150,000",
  "company_name": "Tech Corp",
  "company": 1,
  "created_by": "admin@example.com",
  "created_at": "2025-11-28T06:00:00Z",
  "updated_at": "2025-11-28T06:00:00Z",
  "is_active": true,
  "slug": "",
  "expiry_at": "2025-12-31T23:59:59Z",
  "applications_count": 0
}
```

**Job Type Choices:**
- `full_time`: Full time
- `part_time`: Part time
- `contract`: Contract
- `internship`: Internship
- `remote`: Remote
- `other`: Other

---

### Update Job
Update an existing job posting (Admin only).

**Endpoint:** `PUT /api/jobs/{id}/` or `PATCH /api/jobs/{id}/`

**Authentication:** Required (Admin only)

**Request Body:** (Same as Create Job, all fields optional for PATCH)

**Response:** `200 OK`

---

### Delete Job
Delete a job posting (Admin only).

**Endpoint:** `DELETE /api/jobs/{id}/`

**Authentication:** Required (Admin only)

**Response:** `204 No Content`

---

## Categories

### List Categories
Retrieve all job categories.

**Endpoint:** `GET /api/categories/`

**Authentication:** Required

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Engineering",
    "description": "Software, hardware, and systems engineering roles",
    "created_at": "2025-11-28T05:00:00Z"
  },
  {
    "id": 2,
    "name": "Design",
    "description": "UI/UX, graphic design, and product design roles",
    "created_at": "2025-11-28T05:00:00Z"
  }
]
```

**Permissions:**
- Authenticated users can view categories
- Only admins can create, update, or delete categories

---

### Retrieve Category
Get details of a specific category.

**Endpoint:** `GET /api/categories/{id}/`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Engineering",
  "description": "Software, hardware, and systems engineering roles",
  "created_at": "2025-11-28T05:00:00Z"
}
```

---

### Create Category
Create a new job category (Admin only).

**Endpoint:** `POST /api/categories/`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "Marketing",
  "description": "Marketing and growth roles"
}
```

**Response:** `201 Created`

---

### Update Category
Update an existing category (Admin only).

**Endpoint:** `PUT /api/categories/{id}/` or `PATCH /api/categories/{id}/`

**Authentication:** Required (Admin only)

**Response:** `200 OK`

---

### Delete Category
Delete a category (Admin only).

**Endpoint:** `DELETE /api/categories/{id}/`

**Authentication:** Required (Admin only)

**Response:** `204 No Content`

---

## Companies

### List Companies
Retrieve all companies.

**Endpoint:** `GET /api/companies/`

**Authentication:** Required

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Tech Corp",
    "description": "Leading technology company",
    "website": "https://techcorp.com",
    "created_at": "2025-11-28T05:00:00Z"
  }
]
```

**Permissions:**
- Authenticated users can view companies
- Only admins can create, update, or delete companies

---

### Retrieve Company
Get details of a specific company.

**Endpoint:** `GET /api/companies/{id}/`

**Authentication:** Required

**Response:** `200 OK`

---

### Create Company
Create a new company (Admin only).

**Endpoint:** `POST /api/companies/`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "New Tech Inc",
  "description": "Innovative tech startup",
  "website": "https://newtech.com"
}
```

**Response:** `201 Created`

---

### Update Company
Update an existing company (Admin only).

**Endpoint:** `PUT /api/companies/{id}/` or `PATCH /api/companies/{id}/`

**Authentication:** Required (Admin only)

**Response:** `200 OK`

---

### Delete Company
Delete a company (Admin only).

**Endpoint:** `DELETE /api/companies/{id}/`

**Authentication:** Required (Admin only)

**Response:** `204 No Content`

---

## Applications

### List Applications
Retrieve job applications.
- Regular users see only their own applications
- Admins see all applications

**Endpoint:** `GET /api/applications/`

**Authentication:** Required

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "job": 1,
    "job_title": "Senior Software Engineer",
    "user": 2,
    "user_email": "user@example.com",
    "resume_url": "https://example.com/resume.pdf",
    "status": "pending",
    "applied_at": "2025-11-28T06:00:00Z"
  }
]
```

**Status Values:**
- `applied`: Application submitted
- `shortlisted`: Candidate shortlisted
- `rejected`: Application rejected
- `withdrawn`: Candidate withdrew
- `pending`: Application pending review

---

### Retrieve Application
Get details of a specific application.

**Endpoint:** `GET /api/applications/{id}/`

**Authentication:** Required (owner or admin)

**Response:** `200 OK`

---

### Create Application (Apply for Job)
Submit an application for a job.

**Endpoint:** `POST /api/applications/`

**Authentication:** Required

**Request Body:**
```json
{
  "job": 1,
  "resume_url": "https://example.com/resume.pdf"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "job": 1,
  "job_title": "Senior Software Engineer",
  "user": 2,
  "user_email": "user@example.com",
  "resume_url": "https://example.com/resume.pdf",
  "status": "pending",
  "applied_at": "2025-11-28T06:00:00Z"
}
```

**Constraints:**
- Users can only apply once per job (unique constraint on job + user)
- Must be authenticated

---

### Withdraw/Delete Application
Withdraw an application (users) or delete it (admins).

**Endpoint:** `DELETE /api/applications/{id}/`

**Authentication:** Required (owner or admin)

**Behavior:**
- **Regular users**: Sets status to `withdrawn` (doesn't actually delete)
- **Admins**: Permanently deletes the application

**Response:** `200 OK` (for withdrawal) or `204 No Content` (for deletion)
```json
{
  "detail": "Application withdrawn."
}
```

**Permissions:**
- Users can withdraw their own applications
- Admins can delete any application

---

## Documentation Endpoints

### Swagger UI
Interactive API documentation.

**Endpoints:**
- `GET /swagger/`
- `GET /api/docs/`
- `GET /docs/`

**Authentication:** Not required

---

### ReDoc
Alternative API documentation format.

**Endpoint:** `GET /redoc/`

**Authentication:** Not required

---

### OpenAPI JSON Schema
Raw OpenAPI specification.

**Endpoint:** `GET /swagger.json`

**Authentication:** Not required

---

## Common Response Codes

### Success Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Resource deleted successfully

### Error Codes
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Authentication Flow

### Registration → Verification → Login
1. **Register**: `POST /api/users/register/`
2. **Verify Email**: User receives email → clicks link or uses token → `POST /api/auth/verify-email/`
3. **Login**: `POST /api/users/login/` → Receive JWT tokens

### Password Reset
1. **Request Reset**: `POST /api/auth/forgot-password/`
2. **Reset Password**: User receives email → uses token → `POST /api/auth/reset-password/`

---

## Rate Limiting
Password reset requests are rate-limited:
- 5 requests per hour per user
- 20 requests per hour per IP address

---

## Notes
- All timestamps are in UTC ISO 8601 format
- All endpoints return JSON responses
- CSRF protection is enabled for cookie-based authentication
- CORS is configured to allow credentials from trusted origins
- Tokens expire: Access token (60 minutes), Refresh token (24 hours)
