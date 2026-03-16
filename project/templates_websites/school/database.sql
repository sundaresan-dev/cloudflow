-- School Management System Database
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    class VARCHAR(20) NOT NULL,
    roll_no INT NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'present',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(50) NOT NULL,
    marks INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Sample Students
INSERT INTO students (name, class, roll_no, email, phone) VALUES
('John Smith', '10-A', 1, 'john@academy.com', '9876543210'),
('Sarah Johnson', '10-B', 15, 'sarah@academy.com', '9876543211'),
('Michael Brown', '9-A', 28, 'michael@academy.com', '9876543212'),
('Emma Davis', '11-A', 42, 'emma@academy.com', '9876543213'),
('David Wilson', '9-B', 55, 'david@academy.com', '9876543214'),
('Lisa Anderson', '12-A', 68, 'lisa@academy.com', '9876543215');

-- Sample Classes
INSERT INTO classes (class_name, description) VALUES
('9-A', 'Class 9 Section A'),
('9-B', 'Class 9 Section B'),
('10-A', 'Class 10 Section A'),
('10-B', 'Class 10 Section B'),
('11-A', 'Class 11 Section A'),
('12-A', 'Class 12 Section A');
