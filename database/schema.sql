-- Evidentia Database Schema
-- SQLite Database for Digital Evidence Management System

-- Cases table
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number TEXT UNIQUE NOT NULL,
    case_name TEXT NOT NULL,
    case_type TEXT NOT NULL,
    description TEXT,
    investigator TEXT,
    created_date TEXT NOT NULL,
    status TEXT DEFAULT 'Active',
    total_evidence_count INTEGER DEFAULT 0,
    analyzed_count INTEGER DEFAULT 0,
    pending_count INTEGER DEFAULT 0,
    flagged_count INTEGER DEFAULT 0
);

-- Evidence table
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT,
    file_size INTEGER,
    hash_value TEXT,
    created_date TEXT,
    modified_date TEXT,
    accessed_date TEXT,
    metadata TEXT,
    notes TEXT,
    analysis_status TEXT DEFAULT 'Pending',
    risk_level TEXT DEFAULT 'Low',
    analyzed_by TEXT,
    analyzed_date TEXT,
    FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE,
    CHECK (analysis_status IN ('Pending', 'Analyzed', 'Flagged')),
    CHECK (risk_level IN ('Low', 'Medium', 'High'))
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'Investigator',
    created_date TEXT NOT NULL
);

-- Case Milestones table (for Timeline Grid feature)
CREATE TABLE IF NOT EXISTS case_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    milestone_name TEXT NOT NULL,
    milestone_date TEXT NOT NULL,
    milestone_status TEXT DEFAULT 'Pending',
    description TEXT,
    created_by TEXT,
    FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE,
    CHECK (milestone_status IN ('Pending', 'In Progress', 'Completed'))
);

-- Activity Log table (for Recent Activity Feed feature)
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER,
    user_id INTEGER,
    action_type TEXT NOT NULL,
    action_description TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_evidence_case_id ON evidence(case_id);
CREATE INDEX IF NOT EXISTS idx_cases_case_number ON cases(case_number);
CREATE INDEX IF NOT EXISTS idx_evidence_file_type ON evidence(file_type);
CREATE INDEX IF NOT EXISTS idx_evidence_status ON evidence(analysis_status);
CREATE INDEX IF NOT EXISTS idx_evidence_risk_level ON evidence(risk_level);
CREATE INDEX IF NOT EXISTS idx_milestones_case_id ON case_milestones(case_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_case_id ON activity_log(case_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON activity_log(timestamp);
