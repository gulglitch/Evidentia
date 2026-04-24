-- Fake SQL database backup for testing
-- Extension .sql is in MEDIUM_RISK_EXTENSIONS
-- Risk Score: 2 (extension) + 1 (recent modification) = 3 = MEDIUM RISK

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password_hash TEXT
);

INSERT INTO users VALUES (1, 'admin', 'fake_hash_123');
