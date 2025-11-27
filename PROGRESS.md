## 20th November 2025 (Midnight)
- Successfully set up the users, authentication and categories app
- Successfully created superuser
- Created, set up and successfully migrated data models to Supabase
- User Information (using seeded data):
      1. POST request to `http://127.0.0.1:8000/api/auth/token/` using the seeded Admin data returns the `access_token` and the `refresh_token`
      2. I used this same data to try fetching the job categories, and it worked.
      3. Let's make more progress.


## 20th November 2025 (3:06 PM WAT)
- Successfully created and implemented users models, after several database fixes and migrations
- Updated Swagger UI
- Updated User Authentication
- Implement User Email Verifying using Google SMTP


## 21st Novemeber 2025 (2:56 AM)
- Successfully implemented the email sending service and background job
- User verification works

## 22nd November 2025 (12:27 AM)
- Implemented the email sending after a user sign up and then they are taken to the verify auth route, and then, the user gets verified, and can then login.
- Add password validators for the project.


## 27th November 2025 (05:17 AM)
- **Major Win**: Implemented and tested the correct user's access to endpoints, and user authorization implemented.
- Next Steps: Design `applications` app, Fix category filtering (it shows by id instead), case sensitive location filtering (fix this to use .lower), clean up the codebase and re-arrange spaghetti code, implement documentation, write tests.
- Final Steps before cleanup: Migration to a new DB server on production, Deployment, and Vibe-code of Frontend.