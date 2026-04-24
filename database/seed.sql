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

-- Sample Activity Log Entries (Feature 8: Recent Activity Feed)
INSERT INTO activity_log (case_id, user_id, action_type, action_description, timestamp, entity_type, entity_id)
VALUES
    (1, 1, 'case_created', 'Created new case: Corporate Data Breach Investigation', '2026-03-01 09:00:00', 'case', 1),
    (1, 1, 'evidence_upload', 'Uploaded 15 evidence files from server logs', '2026-03-01 10:30:00', 'evidence', NULL),
    (1, 2, 'evidence_analyzed', 'Analyzed suspicious network traffic logs', '2026-03-02 14:15:00', 'evidence', NULL),
    (1, 2, 'milestone_added', 'Added milestone: Initial Evidence Collection Complete', '2026-03-02 16:00:00', 'milestone', NULL),
    (2, 1, 'case_created', 'Created new case: Employee Misconduct Case', '2026-03-10 08:30:00', 'case', 2),
    (2, 1, 'evidence_upload', 'Uploaded email communications and activity logs', '2026-03-10 11:00:00', 'evidence', NULL),
    (1, 1, 'status_update', 'Updated case status to In Progress', '2026-03-05 09:45:00', 'case', 1),
    (1, 2, 'report_generated', 'Generated preliminary forensic report', '2026-03-08 15:30:00', 'report', NULL),
    (2, 2, 'evidence_analyzed', 'Reviewed employee email communications', '2026-03-12 10:20:00', 'evidence', NULL),
    (1, 1, 'evidence_flagged', 'Flagged 3 high-risk files for detailed analysis', '2026-03-03 13:45:00', 'evidence', NULL),
    (2, 1, 'milestone_added', 'Added milestone: Evidence Review Meeting Scheduled', '2026-03-13 14:00:00', 'milestone', NULL),
    (1, 2, 'evidence_upload', 'Uploaded additional firewall logs', '2026-03-06 11:30:00', 'evidence', NULL),
    (2, 2, 'status_update', 'Updated evidence status: 8 files analyzed', '2026-03-14 09:00:00', 'evidence', NULL),
    (1, 1, 'timeline_updated', 'Updated case timeline with new events', '2026-03-07 16:15:00', 'timeline', NULL),
    (2, 1, 'evidence_upload', 'Uploaded HR documentation and incident reports', '2026-03-11 13:20:00', 'evidence', NULL);

-- Note: In production, use proper password hashing (bcrypt, argon2, etc.)

