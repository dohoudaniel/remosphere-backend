CREATE TABLE `users` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `role` ENUM ('admin', 'user') DEFAULT 'user',
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `dob` date,
  `username` varchar(100) UNIQUE COMMENT 'auto-generate (lower(firstname||lastname)) ensure uniqueness',
  `email` varchar(255) UNIQUE NOT NULL,
  `password` varchar(255) NOT NULL,
  `is_admin` tinyint(1) DEFAULT 0 COMMENT 'derived from role on app side or DB trigger',
  `created_at` timestamp DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` timestamp DEFAULT (CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP),
  `last_login` timestamp
);

CREATE TABLE `categories` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(150) UNIQUE NOT NULL,
  `created_at` timestamp DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `companies` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL,
  `website` varchar(255),
  `description` text,
  `created_at` timestamp DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `jobs` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `slug` varchar(255) UNIQUE,
  `description` text,
  `category_id` int COMMENT 'FK -> categories.id',
  `location_city` varchar(150),
  `location_state` varchar(150),
  `location_country` varchar(150),
  `is_remote` tinyint(1) DEFAULT 0,
  `type` ENUM ('full_time', 'part_time', 'contract', 'internship', 'temporary', 'freelance') DEFAULT 'full_time',
  `application_link` varchar(512) COMMENT 'external application link if using external apply',
  `salary_min` decimal(12,2),
  `salary_max` decimal(12,2),
  `company_name` varchar(255),
  `company_id` int COMMENT 'FK -> companies.id (optional)',
  `created_by` int COMMENT 'FK -> users.id (who posted the job)',
  `created_at` timestamp DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` timestamp DEFAULT (CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP),
  `is_active` tinyint(1) DEFAULT 1,
  `no_of_applications` int DEFAULT 0 COMMENT 'prefer view/materialized view or triggers to keep consistent'
);

CREATE TABLE `applications` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `job_id` int NOT NULL COMMENT 'FK -> jobs.id',
  `user_id` int NOT NULL COMMENT 'FK -> users.id',
  `resume_url` varchar(512),
  `portfolio_url` varchar(512),
  `cover_letter_url` varchar(512),
  `cover_letter` text,
  `status` ENUM ('pending', 'reviewed', 'shortlisted', 'rejected', 'offered', 'withdrawn') DEFAULT 'pending',
  `applied_at` timestamp DEFAULT (CURRENT_TIMESTAMP)
);

CREATE INDEX `jobs_index_0` ON `jobs` (`title`);

CREATE INDEX `jobs_index_1` ON `jobs` (`category_id`);

CREATE INDEX `jobs_index_2` ON `jobs` (`type`);

CREATE INDEX `jobs_index_3` ON `jobs` (`is_remote`);

CREATE INDEX `jobs_index_4` ON `jobs` (`created_at`);

CREATE INDEX `applications_index_5` ON `applications` (`job_id`);

CREATE INDEX `applications_index_6` ON `applications` (`user_id`);

CREATE INDEX `applications_index_7` ON `applications` (`status`);

ALTER TABLE `users` COMMENT = 'Stores user data on signup, focusing on ALX Nigeria Alumni';

ALTER TABLE `categories` COMMENT = 'Job categories / industries';

ALTER TABLE `companies` COMMENT = 'Optional company profiles to associate with jobs';

ALTER TABLE `jobs` COMMENT = 'Job postings';

ALTER TABLE `applications` COMMENT = 'Job applications by users';

ALTER TABLE `jobs` ADD FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`);

ALTER TABLE `jobs` ADD FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`);

ALTER TABLE `jobs` ADD FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

ALTER TABLE `applications` ADD FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`);

ALTER TABLE `applications` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
