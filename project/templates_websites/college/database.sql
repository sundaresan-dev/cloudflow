-- University Management System Database
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    head VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    duration INT NOT NULL,
    credits INT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    enrollment_number VARCHAR(20) UNIQUE NOT NULL,
    course_id INT NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    grade VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Sample Departments
INSERT INTO departments (name, head) VALUES
('Engineering', 'Dr. John Smith'),
('Science', 'Dr. Sarah Johnson'),
('Arts', 'Dr. James Brown'),
('Commerce', 'Dr. Emily Davis'),
('Law', 'Dr. Michael Wilson');

-- Sample Courses
INSERT INTO courses (name, department_id, duration, credits, description) VALUES
('Computer Science', 1, 4, 120, 'Master modern programming, AI, and software development'),
('Civil Engineering', 1, 4, 120, 'Design and build sustainable infrastructure'),
('Physics', 2, 4, 120, 'Study the laws of motion and energy'),
('Chemistry', 2, 4, 120, 'Learn the science of substances and reactions'),
('Literature', 3, 3, 90, 'Explore world literature and language'),
('Business Administration', 4, 4, 120, 'Develop business leadership and management'),
('Law', 5, 5, 150, 'Prepare for legal practice');
