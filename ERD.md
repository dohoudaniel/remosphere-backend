# Database Entity Relationship Diagram (Markdown Format)

Each table shows: **Column | Type | Null? | Default / Constraint | Description / Notes | Index / Foreign Key (FK) or Primary Key (PK)**.

---

### Enums (Postgres)

| Name                      | Values                                                                       | Notes                 |
| ------------------------- | ---------------------------------------------------------------------------- | --------------------- |
| `role_enum`               | `admin`, `user`                                                              | User role             |
| `job_type_enum`           | `full_time`, `part_time`, `contract`, `internship`, `temporary`, `freelance` | Job type values       |
| `application_status_enum` | `pending`, `reviewed`, `shortlisted`, `rejected`, `offered`, `withdrawn`     | Application lifecycle |

---

### `users`

|          Column | Type          |      Null?     | Default / Constraint                                      | Description / Notes                                | Index / FK                    |                                                                 |              |
| --------------: | ------------- | :------------: | --------------------------------------------------------- | -------------------------------------------------- | ----------------------------- | --------------------------------------------------------------- | ------------ |
|            `id` | `uuid`        |    NOT NULL    | `DEFAULT gen_random_uuid()`                               | Primary key (UUID)                                 | PK                            |                                                                 |              |
|    `first_name` | `text`        |    NOT NULL    |                                                           | Given name                                         |                               |                                                                 |              |
|     `last_name` | `text`        |    NOT NULL    |                                                           | Family name                                        |                               |                                                                 |              |
|           `dob` | `date`        |      NULL      |                                                           | Date of birth (optional)                           |                               |                                                                 |              |
|      `username` | `text`        |    NOT NULL    | `UNIQUE` — generated (see notes)                          | Auto-generate e.g. `lower(first_name               |                               | last_name)` but ensure uniqueness by appending digits if needed | UNIQUE INDEX |
|          `role` | `role_enum`   |    NOT NULL    | `DEFAULT 'user'`                                          | `'admin'` or `'user'`                              |                               |                                                                 |              |
|      `is_admin` | `boolean`     |    NOT NULL    | `GENERATED ALWAYS AS (role = 'admin') STORED`             | Derived; do not set manually                       |                               |                                                                 |              |
|         `email` | `text`        |    NOT NULL    | `UNIQUE`                                                  | Primary contact / login                            | UNIQUE INDEX                  |                                                                 |              |
| `password_hash` | `text`        | NULL / depends | If using Supabase Auth, prefer to omit (use `auth.users`) | Store hashed password only if handling auth in-app |                               |                                                                 |              |
|   `date_joined` | `timestamptz` |    NOT NULL    | `DEFAULT now()`                                           | Account creation timestamp                         | INDEX if listing recent users |                                                                 |              |
|    `last_login` | `timestamptz` |      NULL      |                                                           | Last sign-in time                                  |                               |                                                                 |              |

**Notes:** Prefer Supabase Auth + a `profiles` table referencing `auth.uid` instead of duplicating password fields.

---

### `categories`

|       Column | Type          |   Null?  | Default / Constraint | Description / Notes                 | Index / FK   |
| -----------: | ------------- | :------: | -------------------- | ----------------------------------- | ------------ |
|         `id` | `serial`      | NOT NULL | PRIMARY KEY          | Numeric category id                 | PK           |
|       `name` | `text`        | NOT NULL | `UNIQUE`             | Category name (e.g., "Engineering") | UNIQUE INDEX |
| `created_at` | `timestamptz` | NOT NULL | `DEFAULT now()`      | Creation timestamp                  |              |

---

### `companies` (optional)

|        Column | Type          |   Null?  | Default / Constraint        | Description / Notes  | Index / FK   |
| ------------: | ------------- | :------: | --------------------------- | -------------------- | ------------ |
|          `id` | `uuid`        | NOT NULL | `DEFAULT gen_random_uuid()` | Company PK           | PK           |
|        `name` | `text`        | NOT NULL | `UNIQUE`                    | Company display name | UNIQUE INDEX |
|     `website` | `text`        |   NULL   |                             | Company URL          |              |
| `description` | `text`        |   NULL   |                             | Company summary      |              |
|  `created_at` | `timestamptz` | NOT NULL | `DEFAULT now()`             | Timestamp            |              |

---

### `jobs`

|               Column | Type            |         Null?        | Default / Constraint                                            | Description / Notes                                        | Index / FK                      |   |                                    |                         |                       |
| -------------------: | --------------- | :------------------: | --------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------- | - | ---------------------------------- | ----------------------- | --------------------- |
|                 `id` | `uuid`          |       NOT NULL       | `DEFAULT gen_random_uuid()`                                     | Job PK                                                     | PK                              |   |                                    |                         |                       |
|              `title` | `text`          |       NOT NULL       |                                                                 | Job title                                                  | b-tree index if used in filters |   |                                    |                         |                       |
|               `slug` | `text`          |         NULL         | `UNIQUE`                                                        | URL-friendly slug                                          | UNIQUE INDEX                    |   |                                    |                         |                       |
|        `description` | `text`          |         NULL         |                                                                 | Full job description                                       | Used by full-text search        |   |                                    |                         |                       |
|        `category_id` | `integer`       |         NULL         | `REFERENCES categories(id) ON DELETE SET NULL`                  | Category FK                                                | INDEX (b-tree)                  |   |                                    |                         |                       |
|      `location_city` | `text`          |         NULL         |                                                                 | City part of location                                      |                                 |   |                                    |                         |                       |
|     `location_state` | `text`          |         NULL         |                                                                 | State / region                                             |                                 |   |                                    |                         |                       |
|   `location_country` | `text`          |         NULL         |                                                                 | Country                                                    |                                 |   |                                    |                         |                       |
|          `is_remote` | `boolean`       |       NOT NULL       | `DEFAULT false`                                                 | Remote flag                                                | INDEX                           |   |                                    |                         |                       |
|               `type` | `job_type_enum` |       NOT NULL       | `DEFAULT 'full_time'`                                           | Job type enum                                              | INDEX                           |   |                                    |                         |                       |
|   `application_link` | `text`          |         NULL         |                                                                 | External apply link                                        |                                 |   |                                    |                         |                       |
|         `salary_min` | `numeric(12,2)` |         NULL         |                                                                 | Minimum salary (numeric)                                   |                                 |   |                                    |                         |                       |
|         `salary_max` | `numeric(12,2)` |         NULL         |                                                                 | Maximum salary (numeric)                                   |                                 |   |                                    |                         |                       |
|       `company_name` | `text`          |         NULL         |                                                                 | Denormalized company name                                  | INDEX if searched by company    |   |                                    |                         |                       |
|         `company_id` | `uuid`          |         NULL         | `REFERENCES companies(id) ON DELETE SET NULL`                   | Optional company FK                                        | INDEX                           |   |                                    |                         |                       |
|         `created_by` | `uuid`          |         NULL         | `REFERENCES users(id) ON DELETE SET NULL`                       | Admin/user who posted                                      | INDEX                           |   |                                    |                         |                       |
|         `created_at` | `timestamptz`   |       NOT NULL       | `DEFAULT now()`                                                 | Creation timestamp                                         | INDEX (for ordering)            |   |                                    |                         |                       |
|         `updated_at` | `timestamptz`   |       NOT NULL       | `DEFAULT now()`                                                 | Last update timestamp (update on save)                     |                                 |   |                                    |                         |                       |
|          `is_active` | `boolean`       |       NOT NULL       | `DEFAULT true`                                                  | Job visibility toggle                                      | INDEX                           |   |                                    |                         |                       |
| `no_of_applications` | `integer`       |       NOT NULL       | `DEFAULT 0` (recommended: use view instead)                     | Stored count — **prefer derived view / materialized view** |                                 |   |                                    |                         |                       |
|      `search_vector` | `tsvector`      | NOT NULL (generated) | `GENERATED ALWAYS AS (to_tsvector('english', coalesce(title,'') |                                                            | ' '                             |   | coalesce(description,''))) STORED` | Full-text search vector | GIN INDEX recommended |

**Recommended indexes for `jobs`:**

* `GIN (search_vector)` — full-text search
* B-tree on `category_id`, `type`, `is_remote`, `created_at DESC`, `company_name`
* Composite index e.g. `(category_id, type, created_at)` if query patterns require it

---

### `applications`

|             Column | Type                      |   Null?  | Default / Constraint                     | Description / Notes                 | Index / FK                   |
| -----------------: | ------------------------- | :------: | ---------------------------------------- | ----------------------------------- | ---------------------------- |
|               `id` | `uuid`                    | NOT NULL | `DEFAULT gen_random_uuid()`              | Application PK                      | PK                           |
|           `job_id` | `uuid`                    | NOT NULL | `REFERENCES jobs(id) ON DELETE CASCADE`  | FK to job                           | INDEX                        |
|          `user_id` | `uuid`                    | NOT NULL | `REFERENCES users(id) ON DELETE CASCADE` | Applicant FK                        | INDEX                        |
|       `resume_url` | `text`                    |   NULL   |                                          | Link to file in Supabase Storage    |                              |
|    `portfolio_url` | `text`                    |   NULL   |                                          | External portfolio link             |                              |
| `cover_letter_url` | `text`                    |   NULL   |                                          | Stored cover letter URL             |                              |
|     `cover_letter` | `text`                    |   NULL   |                                          | Inline cover letter text (optional) |                              |
|           `status` | `application_status_enum` | NOT NULL | `DEFAULT 'pending'`                      | Application state                   | INDEX on status if filtering |
|       `applied_at` | `timestamptz`             | NOT NULL | `DEFAULT now()`                          | When application occurred           | INDEX (for recent apps)      |
|  UNIQUE constraint |                           |          | `UNIQUE (job_id, user_id)`               | Prevent duplicate applications      |                              |

**Notes:** `ON DELETE CASCADE` removes applications if job or user is deleted. Use RLS so users can only read/write their own applications.

---

### Relationships (summary)

| From Table     | Column        | To Table     | To Column | On Delete  |
| -------------- | ------------- | ------------ | --------- | ---------- |
| `jobs`         | `category_id` | `categories` | `id`      | `SET NULL` |
| `jobs`         | `company_id`  | `companies`  | `id`      | `SET NULL` |
| `jobs`         | `created_by`  | `users`      | `id`      | `SET NULL` |
| `applications` | `job_id`      | `jobs`       | `id`      | `CASCADE`  |
| `applications` | `user_id`     | `users`      | `id`      | `CASCADE`  |

---

### Other implementation notes (short — as a compact table)

| Topic                | Recommendation                                                                                                                                              |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `no_of_applications` | **Preferred:** `VIEW job_application_counts` or `MATERIALIZED VIEW`. **Alternate:** triggers to increment/decrement column on insert/delete (more complex). |
| Resumes / Files      | Use **Supabase Storage** for files; store signed URLs in `resume_url` / `cover_letter_url`.                                                                 |
| Auth                 | Prefer **Supabase Auth** + `profiles` table referencing `auth.uid` rather than storing passwords manually.                                                  |
| RLS                  | Enable Row Level Security policies so users can access only their own `applications` rows (admins bypass/allowed by policy).                                |
| Full-text search     | Use `search_vector` + `GIN` index and rank results with `ts_rank`.                                                                                          |
| Pagination           | Use **cursor pagination** for large job lists (better scalability than offset/limit).                                                                       |
| Django mapping       | Use `UUIDField(default=uuid.uuid4, primary_key=True)` and `TextChoices` for enums; annotate `application_count` from view or `Count('applications')`.       |

