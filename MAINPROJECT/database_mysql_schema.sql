-- MySQL schema for College Recruitment Portal
-- Run: mysql -u root -p < database_mysql_schema.sql

CREATE DATABASE
IF
  NOT EXISTS college_recruitment CHARACTER
  SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
  USE college_recruitment;

  -- Users table (students and companies)
  DROP TABLE
  IF
    EXISTS users;
    CREATE TABLE users (
      id INT AUTO_INCREMENT PRIMARY KEY
      , username VARCHAR(100) NOT NULL UNIQUE
      , email VARCHAR(255) NOT NULL UNIQUE
      , password VARCHAR(255) NOT NULL
      , user_type ENUM('student', 'company') NOT NULL
      , created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      , INDEX idx_user_type (user_type)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

    -- Companies table
    DROP TABLE
    IF
      EXISTS companies;
      CREATE TABLE companies (
        id INT AUTO_INCREMENT PRIMARY KEY
        , user_id INT NOT NULL UNIQUE
        , company_name VARCHAR(255) NOT NULL
        , email VARCHAR(255)
        , phone VARCHAR(50)
        , website VARCHAR(255)
        , industry VARCHAR(150)
        , description TEXT
        , logo VARCHAR(255)
        , verified TINYINT(1) NOT NULL DEFAULT 0
        , created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        , FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
      ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

      -- Students table
      DROP TABLE
      IF
        EXISTS students;
        CREATE TABLE students (
          id INT AUTO_INCREMENT PRIMARY KEY
          , user_id INT NOT NULL UNIQUE
          , name VARCHAR(255)
          , phone VARCHAR(50)
          , department VARCHAR(150)
          , year TINYINT
          , cgpa DECIMAL(4, 2) DEFAULT 0.00
          , skills TEXT
          , projects TEXT
          , resume_link VARCHAR(512)
          , bio TEXT
          , profile_picture VARCHAR(512)
          , created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
          , FOREIGN KEY (user_id) REFERENCES users(id)
          ON DELETE CASCADE
          , INDEX idx_cgpa (cgpa)
          , INDEX idx_department (department)
        ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

        -- Jobs table
        DROP TABLE
        IF
          EXISTS jobs;
          CREATE TABLE jobs (
            id INT AUTO_INCREMENT PRIMARY KEY
            , company_id INT NOT NULL
            , job_title VARCHAR(255) NOT NULL
            , role VARCHAR(150)
            , description LONGTEXT
            , skills_required TEXT
            , min_cgpa DECIMAL(4, 2) DEFAULT 0.00
            , department VARCHAR(150)
            , experience_level VARCHAR(50)
            , job_type VARCHAR(50)
            , salary_min DECIMAL(12, 2)
            , salary_max DECIMAL(12, 2)
            , location VARCHAR(255)
            , application_deadline DATETIME
            , created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            , FOREIGN KEY (company_id) REFERENCES companies(id)
            ON DELETE CASCADE
            , INDEX idx_company (company_id)
            , INDEX idx_role (role)
            , INDEX idx_created_at (created_at)
          ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

          -- Applications table
          DROP TABLE
          IF
            EXISTS applications;
            CREATE TABLE applications (
              id INT AUTO_INCREMENT PRIMARY KEY
              , student_id INT NOT NULL
              , job_id INT NOT NULL
              , status ENUM('pending', 'accepted', 'rejected') NOT NULL DEFAULT 'pending'
              , applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
              , FOREIGN KEY (student_id) REFERENCES students(id)
              ON DELETE CASCADE
              , FOREIGN KEY (job_id) REFERENCES jobs(id)
              ON DELETE CASCADE
              , INDEX idx_student (student_id)
              , INDEX idx_job (job_id)
            ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

            -- Shortlist table
            DROP TABLE
            IF
              EXISTS shortlist;
              CREATE TABLE shortlist (
                id INT AUTO_INCREMENT PRIMARY KEY
                , company_id INT NOT NULL
                , student_id INT NOT NULL
                , created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                , FOREIGN KEY (company_id) REFERENCES companies(id)
                ON DELETE CASCADE
                , FOREIGN KEY (student_id) REFERENCES students(id)
                ON DELETE CASCADE
                , UNIQUE KEY uniq_company_student (company_id, student_id)
              ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

              -- Useful indexes for text searching (MySQL fulltext supported on InnoDB since 5.6)
              -- Fulltext index for job description and skills to enable keyword searches
              ALTER TABLE jobs ADD FULLTEXT KEY ft_description_skills (description, skills_required);

              -- Fulltext index for student skills
              ALTER TABLE students ADD FULLTEXT KEY ft_student_skills (skills, projects);

              -- End of schema