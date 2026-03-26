-- Sample/Test Data for Evidentia Database
-- Run this after schema.sql to populate with test data

-- Sample Cases
INSERT INTO cases (case_number, case_name, case_type, description, investigator, created_date, status)
VALUES 
    ('CASE-2026-001', 'Corporate Data Breach Investigation', 'Cybercrime', 'Investigation of unauthorized access to corporate servers', 'John Doe', '2026-03-01', 'Active'),
    ('CASE-2026-002', 'Employee Misconduct Case', 'Internal Investigation', 'Review of employee activity logs and communications', 'Jane Smith', '2026-03-10', 'Active');

-- Sample Users
INSERT INTO users (username, password_hash, full_name, role, created_date)
VALUES 
    ('admin', 'placeholder_hash', 'Administrator', 'Admin', '2026-01-01'),
    ('investigator1', 'placeholder_hash', 'John Doe', 'Investigator', '2026-01-15');

-- Note: In production, use proper password hashing (bcrypt, argon2, etc.)
