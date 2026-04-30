"""
Database Module
SQLite database operations for storing evidence and case data
"""

import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class Database:
    """SQLite database handler for Evidentia."""
    
    def __init__(self, db_path: str = "database/evidentia.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'Student/Learner',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    case_type TEXT,
                    status TEXT DEFAULT 'Active',
                    priority TEXT DEFAULT 'Medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Evidence files table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_extension TEXT,
                    file_size INTEGER,
                    created_time TIMESTAMP,
                    modified_time TIMESTAMP,
                    status TEXT DEFAULT 'Pending',
                    risk_level TEXT DEFAULT 'Low',
                    notes TEXT,
                    metadata TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    role TEXT,
                    organization TEXT,
                    primary_use TEXT,
                    profile_completed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Activity log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Custom case types table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_case_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Milestones table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER NOT NULL,
                    milestone_name TEXT NOT NULL,
                    milestone_date TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            
            # Search history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER NOT NULL,
                    search_query TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            
            # Search presets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER NOT NULL,
                    preset_name TEXT NOT NULL,
                    filters_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
    
    # ──────────────────────────────────────────────
    # User operations
    # ──────────────────────────────────────────────
    
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash a password with the given salt using SHA-256."""
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    
    def create_user(self, username: str, password: str, full_name: str, email: str = "") -> int:
        """
        Create a new user account.
        
        Args:
            username: Unique username (min 4 chars)
            password: User password (min 6 chars)
            full_name: User's full name
            email: User's email (optional)
            
        Returns:
            New user's ID
            
        Raises:
            ValueError: If username already exists or validation fails
        """
        # Validate inputs
        if len(username) < 4:
            raise ValueError("Username must be at least 4 characters")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        if not full_name.strip():
            raise ValueError("Full name is required")
        
        # Check if username already exists
        if self.user_exists(username):
            raise ValueError("Username already taken")
        
        # Generate salt and hash password
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt, full_name, email) VALUES (?, ?, ?, ?, ?)",
                (username, password_hash, salt, full_name.strip(), email.strip())
            )
            return cursor.lastrowid
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user by username and password.
        
        Returns:
            User dict if credentials are valid, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            user = dict(row)
            # Verify password
            password_hash = self._hash_password(password, user['salt'])
            if password_hash == user['password_hash']:
                return user
            return None
    
    def user_exists(self, username: str) -> bool:
        """Check if a username is already taken."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM users WHERE username = ?",
                (username,)
            )
            return cursor.fetchone()['count'] > 0
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, full_name, email, role, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def save_user_preferences(self, user_id: int, role: str, organization: str = "", primary_use: str = ""):
        """Save user profile preferences."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_preferences (user_id, role, organization, primary_use, profile_completed)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    role = excluded.role,
                    organization = excluded.organization,
                    primary_use = excluded.primary_use,
                    profile_completed = 1
            ''', (user_id, role, organization, primary_use))
            
            # Also update the role in the users table
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    
    def is_profile_completed(self, user_id: int) -> bool:
        """Check if a user has completed their profile setup."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT profile_completed FROM user_preferences WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row is not None and row['profile_completed'] == 1
    
    # ──────────────────────────────────────────────
    # Case operations
    # ──────────────────────────────────────────────
    
    def create_case(self, name: str, description: str = "", case_type: str = "", priority: str = "Medium", user_id: int = None) -> int:
        """Create a new case and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cases (name, description, case_type, priority, user_id) VALUES (?, ?, ?, ?, ?)",
                (name, description, case_type, priority, user_id)
            )
            return cursor.lastrowid
    
    def get_case(self, case_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get a case by ID, optionally scoped to a specific user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id is None:
                cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
            else:
                cursor.execute(
                    "SELECT * FROM cases WHERE id = ? AND user_id = ?",
                    (case_id, user_id)
                )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_cases(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all cases, optionally scoped to a specific user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id is None:
                cursor.execute("SELECT * FROM cases ORDER BY created_at DESC")
            else:
                cursor.execute(
                    "SELECT * FROM cases WHERE user_id = ? ORDER BY created_at DESC",
                    (user_id,)
                )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_case_status(self, case_id: int, status: str, user_id: Optional[int] = None):
        """Update the status of a case, optionally scoped to a specific user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id is None:
                cursor.execute(
                    "UPDATE cases SET status = ?, updated_at = ? WHERE id = ?",
                    (status, datetime.now(), case_id)
                )
            else:
                cursor.execute(
                    "UPDATE cases SET status = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                    (status, datetime.now(), case_id, user_id)
                )
    
    def update_case_type(self, case_id: int, case_type: str, user_id: Optional[int] = None):
        """Update the type of a case, optionally scoped to a specific user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id is None:
                cursor.execute(
                    "UPDATE cases SET case_type = ?, updated_at = ? WHERE id = ?",
                    (case_type, datetime.now(), case_id)
                )
            else:
                cursor.execute(
                    "UPDATE cases SET case_type = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                    (case_type, datetime.now(), case_id, user_id)
                )
    
    # Evidence operations
    def add_evidence(self, case_id: int, file_data: Dict[str, Any]) -> int:
        """Add an evidence file to a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO evidence 
                (case_id, file_name, file_path, file_extension, file_size, 
                 created_time, modified_time, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_id,
                file_data.get('file_name'),
                file_data.get('file_path'),
                file_data.get('file_extension'),
                file_data.get('file_size'),
                file_data.get('created_time'),
                file_data.get('modified_time'),
                str(file_data),
            ))
            return cursor.lastrowid
    
    def get_evidence_for_case(self, case_id: int) -> List[Dict[str, Any]]:
        """Get all evidence files for a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM evidence WHERE case_id = ? ORDER BY modified_time",
                (case_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_evidence_status(self, evidence_id: int, status: str, user_id: Optional[int] = None, log_activity: bool = True):
        """
        Update the status of an evidence file.
        
        Args:
            evidence_id: Evidence ID
            status: New status value
            user_id: User ID for activity logging
            log_activity: Whether to log this change to activity feed
        """
        # Get evidence details for logging BEFORE the transaction
        evidence_row = None
        if log_activity:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT e.file_name, e.case_id, e.status as old_status FROM evidence e WHERE e.id = ?",
                    (evidence_id,)
                )
                evidence_row = cursor.fetchone()
        
        # Update the status
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE evidence SET status = ? WHERE id = ?",
                (status, evidence_id)
            )
        
        # Log the activity in a separate transaction
        if log_activity and evidence_row:
            file_name = evidence_row['file_name']
            case_id = evidence_row['case_id']
            old_status = evidence_row['old_status']
            
            if old_status != status:  # Only log if status actually changed
                self.log_activity(
                    case_id=case_id,
                    user_id=user_id,
                    action="Evidence Status Updated",
                    details=f"Changed status of '{file_name}' from {old_status} to {status}"
                )
    
    def update_evidence_risk(self, evidence_id: int, risk_level: str, user_id: Optional[int] = None, log_activity: bool = True):
        """
        Update the risk level of an evidence file.
        
        Args:
            evidence_id: Evidence ID
            risk_level: New risk level value
            user_id: User ID for activity logging
            log_activity: Whether to log this change to activity feed
        """
        # Get evidence details for logging BEFORE the transaction
        evidence_row = None
        if log_activity:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT e.file_name, e.case_id, e.risk_level as old_risk FROM evidence e WHERE e.id = ?",
                    (evidence_id,)
                )
                evidence_row = cursor.fetchone()
        
        # Update the risk level
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE evidence SET risk_level = ? WHERE id = ?",
                (risk_level, evidence_id)
            )
        
        # Log the activity in a separate transaction
        if log_activity and evidence_row:
            file_name = evidence_row['file_name']
            case_id = evidence_row['case_id']
            old_risk = evidence_row['old_risk']
            
            if old_risk != risk_level:  # Only log if risk actually changed
                self.log_activity(
                    case_id=case_id,
                    user_id=user_id,
                    action="Risk Level Updated",
                    details=f"Changed risk level of '{file_name}' from {old_risk} to {risk_level}"
                )
    
    def search_evidence(self, case_id: int, query: str) -> List[Dict[str, Any]]:
        """Search evidence files by name."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM evidence WHERE case_id = ? AND file_name LIKE ?",
                (case_id, f"%{query}%")
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ──────────────────────────────────────────────
    # Activity log operations
    # ──────────────────────────────────────────────
    
    def log_activity(self, case_id: int, action: str, details: str = "", user_id: int = None):
        """Log an activity for a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Use explicit local timestamp instead of CURRENT_TIMESTAMP
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO activity_log (case_id, user_id, action, details, timestamp) VALUES (?, ?, ?, ?, ?)",
                (case_id, user_id, action, details, timestamp)
            )
    
    def get_recent_activity(self, case_id: int = None, limit: int = 10, user_id: int = None) -> List[Dict[str, Any]]:
        """
        Get recent activity for a case or all cases for a user.
        
        Args:
            case_id: Optional case ID to filter by (None = all cases)
            limit: Maximum number of activities to return
            user_id: Optional user ID to filter by (None = all users)
            
        Returns:
            List of activity log entries with user and case information
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build comprehensive query with all context
            query = """
                SELECT 
                    al.id,
                    al.case_id,
                    al.user_id,
                    al.action,
                    al.details,
                    al.timestamp,
                    u.full_name as user_name,
                    u.username,
                    c.name as case_name,
                    c.status as case_status,
                    c.case_type
                FROM activity_log al
                LEFT JOIN users u ON al.user_id = u.id
                LEFT JOIN cases c ON al.case_id = c.id
                WHERE 1=1
            """
            params = []
            
            if case_id is not None:
                query += " AND al.case_id = ?"
                params.append(case_id)
            
            if user_id is not None:
                query += " AND al.user_id = ?"
                params.append(user_id)
            
            query += " ORDER BY al.timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_recent_activity(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent activity across ALL cases and ALL users (truly global).
        
        Args:
            limit: Maximum number of activities to return
            
        Returns:
            List of activity log entries with full context
        """
        return self.get_recent_activity(case_id=None, limit=limit, user_id=None)
    
    def get_activity_count(self, case_id: int = None, user_id: int = None) -> int:
        """
        Get total count of activities.
        
        Args:
            case_id: Optional case ID to filter by
            user_id: Optional user ID to filter by
            
        Returns:
            Total count of activities matching filters
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) as count FROM activity_log WHERE 1=1"
            params = []
            
            if case_id is not None:
                query += " AND case_id = ?"
                params.append(case_id)
            
            if user_id is not None:
                query += " AND user_id = ?"
                params.append(user_id)
            
            cursor.execute(query, params)
            return cursor.fetchone()['count']
    
    # ──────────────────────────────────────────────
    # Statistics
    # ──────────────────────────────────────────────
    
    def get_dashboard_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get overall statistics for the dashboard.
        
        Args:
            user_id: Optional user ID to scope stats to a specific user
            
        Returns:
            Dictionary with comprehensive statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build WHERE clause for user filtering
            user_filter = ""
            user_params = []
            if user_id is not None:
                user_filter = " WHERE user_id = ?"
                user_params = [user_id]
            
            # Total cases
            cursor.execute(f"SELECT COUNT(*) as total FROM cases{user_filter}", user_params)
            total_cases = cursor.fetchone()['total']
            
            # Case status breakdown
            cursor.execute(f"SELECT status, COUNT(*) as count FROM cases{user_filter} GROUP BY status", user_params)
            case_status = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Case type breakdown
            cursor.execute(f"SELECT case_type, COUNT(*) as count FROM cases{user_filter} GROUP BY case_type", user_params)
            case_types = {row['case_type']: row['count'] for row in cursor.fetchall()}
            
            # Total evidence files (across user's cases)
            if user_id is not None:
                cursor.execute("""
                    SELECT COUNT(*) as total 
                    FROM evidence e
                    JOIN cases c ON e.case_id = c.id
                    WHERE c.user_id = ?
                """, [user_id])
            else:
                cursor.execute("SELECT COUNT(*) as total FROM evidence")
            total_evidence = cursor.fetchone()['total']
            
            # Evidence status breakdown
            if user_id is not None:
                cursor.execute("""
                    SELECT e.status, COUNT(*) as count 
                    FROM evidence e
                    JOIN cases c ON e.case_id = c.id
                    WHERE c.user_id = ?
                    GROUP BY e.status
                """, [user_id])
            else:
                cursor.execute("SELECT status, COUNT(*) as count FROM evidence GROUP BY status")
            evidence_status = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Risk level breakdown
            if user_id is not None:
                cursor.execute("""
                    SELECT e.risk_level, COUNT(*) as count 
                    FROM evidence e
                    JOIN cases c ON e.case_id = c.id
                    WHERE c.user_id = ?
                    GROUP BY e.risk_level
                """, [user_id])
            else:
                cursor.execute("SELECT risk_level, COUNT(*) as count FROM evidence GROUP BY risk_level")
            risk_breakdown = {row['risk_level']: row['count'] for row in cursor.fetchall()}
            
            # Total users (only if not filtered by user)
            if user_id is None:
                cursor.execute("SELECT COUNT(*) as total FROM users")
                total_users = cursor.fetchone()['total']
            else:
                total_users = 1
            
            # Active cases (Open or In Progress)
            active_statuses = ['Open', 'In Progress', 'Active']
            placeholders = ','.join('?' * len(active_statuses))
            if user_id is not None:
                cursor.execute(
                    f"SELECT COUNT(*) as total FROM cases WHERE user_id = ? AND status IN ({placeholders})",
                    [user_id] + active_statuses
                )
            else:
                cursor.execute(
                    f"SELECT COUNT(*) as total FROM cases WHERE status IN ({placeholders})",
                    active_statuses
                )
            active_cases = cursor.fetchone()['total']
            
            # Closed cases
            closed_statuses = ['Closed', 'Completed']
            placeholders_closed = ','.join('?' * len(closed_statuses))
            if user_id is not None:
                cursor.execute(
                    f"SELECT COUNT(*) as total FROM cases WHERE user_id = ? AND status IN ({placeholders_closed})",
                    [user_id] + closed_statuses
                )
            else:
                cursor.execute(
                    f"SELECT COUNT(*) as total FROM cases WHERE status IN ({placeholders_closed})",
                    closed_statuses
                )
            closed_cases = cursor.fetchone()['total']
            
            # Calculate completion rate
            if total_cases > 0:
                completion_rate = round((closed_cases / total_cases) * 100, 1)
            else:
                completion_rate = 0.0
            
            return {
                'total_cases': total_cases,
                'active_cases': active_cases,
                'closed_cases': closed_cases,
                'completion_rate': completion_rate,
                'case_status': case_status,
                'case_types': case_types,
                'total_evidence': total_evidence,
                'evidence_status': evidence_status,
                'risk_breakdown': risk_breakdown,
                'total_users': total_users,
            }
    
    def get_case_stats(self, case_id: int) -> Dict[str, Any]:
        """Get statistics for a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total evidence count
            cursor.execute(
                "SELECT COUNT(*) as total FROM evidence WHERE case_id = ?",
                (case_id,)
            )
            total = cursor.fetchone()['total']
            
            # Status breakdown
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM evidence WHERE case_id = ? 
                GROUP BY status
            ''', (case_id,))
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Risk level breakdown
            cursor.execute('''
                SELECT risk_level, COUNT(*) as count 
                FROM evidence WHERE case_id = ? 
                GROUP BY risk_level
            ''', (case_id,))
            risk_counts = {row['risk_level']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total_evidence': total,
                'status_breakdown': status_counts,
                'risk_breakdown': risk_counts,
            }

    # ──────────────────────────────────────────────
    # Custom Case Types operations
    # ──────────────────────────────────────────────
    
    def get_custom_case_types(self) -> List[str]:
        """Get all custom case types."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT type_name FROM custom_case_types ORDER BY type_name")
            return [row['type_name'] for row in cursor.fetchall()]
    
    def add_custom_case_type(self, type_name: str) -> bool:
        """Add a new custom case type."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO custom_case_types (type_name) VALUES (?)",
                    (type_name,)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Type already exists
            return False
    
    def delete_custom_case_type(self, type_name: str) -> bool:
        """Delete a custom case type."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM custom_case_types WHERE type_name = ?",
                    (type_name,)
                )
                conn.commit()
                return True
        except Exception:
            return False
    
    # ──────────────────────────────────────────────
    # Milestone operations (US-04)
    # ──────────────────────────────────────────────
    
    def create_milestone(self, case_id: int, milestone_name: str, 
                        milestone_date: str, description: str = "") -> int:
        """
        Create a new milestone for a case.
        
        Args:
            case_id: Case ID
            milestone_name: Name of the milestone
            milestone_date: Date of milestone (ISO format)
            description: Optional description
            
        Returns:
            Milestone ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO milestones (case_id, milestone_name, milestone_date, description) VALUES (?, ?, ?, ?)",
                (case_id, milestone_name, milestone_date, description)
            )
            return cursor.lastrowid
    
    def get_milestones(self, case_id: int) -> List[Dict[str, Any]]:
        """Get all milestones for a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM milestones WHERE case_id = ? ORDER BY milestone_date",
                (case_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_milestone(self, milestone_id: int):
        """Delete a milestone."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM milestones WHERE id = ?", (milestone_id,))
    
    # ──────────────────────────────────────────────
    # Status tracking operations (US-05)
    # ──────────────────────────────────────────────
    
    def bulk_update_status(self, evidence_ids: List[int], status: str, user_id: Optional[int] = None, log_activity: bool = True):
        """
        Update status for multiple evidence files.
        
        Args:
            evidence_ids: List of evidence IDs
            status: New status value
            user_id: User ID for activity logging
            log_activity: Whether to log this change to activity feed
        """
        # Get evidence details for logging BEFORE the transaction
        evidence_rows = []
        if log_activity and evidence_ids:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' * len(evidence_ids))
                cursor.execute(
                    f"SELECT e.id, e.file_name, e.case_id, e.status as old_status FROM evidence e WHERE e.id IN ({placeholders})",
                    evidence_ids
                )
                evidence_rows = cursor.fetchall()
        
        # Update the statuses
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(evidence_ids))
            cursor.execute(
                f"UPDATE evidence SET status = ? WHERE id IN ({placeholders})",
                [status] + evidence_ids
            )
        
        # Log activities for each evidence file in separate transactions
        if log_activity and evidence_rows:
            for evidence_row in evidence_rows:
                file_name = evidence_row['file_name']
                case_id = evidence_row['case_id']
                old_status = evidence_row['old_status']
                
                if old_status != status:  # Only log if status actually changed
                    self.log_activity(
                        case_id=case_id,
                        user_id=user_id,
                        action="Evidence Status Updated",
                        details=f"Changed status of '{file_name}' from {old_status} to {status}"
                    )
    
    def update_evidence_notes(self, evidence_id: int, notes: str, user_id: Optional[int] = None, log_activity: bool = True):
        """
        Update notes for an evidence file.
        
        Args:
            evidence_id: Evidence ID
            notes: New notes content
            user_id: User ID for activity logging
            log_activity: Whether to log this change to activity feed
        """
        # Get evidence details for logging BEFORE the transaction
        evidence_row = None
        if log_activity:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT e.file_name, e.case_id FROM evidence e WHERE e.id = ?",
                    (evidence_id,)
                )
                evidence_row = cursor.fetchone()
        
        # Update the notes
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE evidence SET notes = ? WHERE id = ?",
                (notes, evidence_id)
            )
        
        # Log the activity in a separate transaction
        if log_activity and evidence_row:
            file_name = evidence_row['file_name']
            case_id = evidence_row['case_id']
            
            self.log_activity(
                case_id=case_id,
                user_id=user_id,
                action="Evidence Notes Updated",
                details=f"Updated notes for '{file_name}'"
            )
    
    def get_evidence_notes(self, evidence_id: int) -> Optional[str]:
        """Get notes for an evidence file."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT notes FROM evidence WHERE id = ?",
                (evidence_id,)
            )
            row = cursor.fetchone()
            return row['notes'] if row else None
    
    def get_status_statistics(self, case_id: int) -> Dict[str, int]:
        """
        Get status statistics for a case.
        
        Returns:
            Dictionary with counts for each status
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM evidence 
                WHERE case_id = ? 
                GROUP BY status
            ''', (case_id,))
            
            stats = {'Pending': 0, 'Analyzed': 0, 'Flagged': 0}
            for row in cursor.fetchall():
                stats[row['status']] = row['count']
            
            return stats
    
    def get_evidence_by_status(self, case_id: int, status: str) -> List[Dict[str, Any]]:
        """Get all evidence files with a specific status."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM evidence WHERE case_id = ? AND status = ? ORDER BY modified_time",
                (case_id, status)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ──────────────────────────────────────────────
    # Search operations (US-07)
    # ──────────────────────────────────────────────
    
    def add_search_history(self, case_id: int, search_query: str):
        """Add a search query to history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO search_history (case_id, search_query) VALUES (?, ?)",
                (case_id, search_query)
            )
    
    def get_search_history(self, case_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history for a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM search_history WHERE case_id = ? ORDER BY timestamp DESC LIMIT ?",
                (case_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def clear_search_history(self, case_id: int):
        """Clear search history for a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_history WHERE case_id = ?", (case_id,))
    
    def save_search_preset(self, case_id: int, preset_name: str, filters_json: str) -> int:
        """Save a search preset."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO search_presets (case_id, preset_name, filters_json) VALUES (?, ?, ?)",
                (case_id, preset_name, filters_json)
            )
            return cursor.lastrowid
    
    def get_search_presets(self, case_id: int) -> List[Dict[str, Any]]:
        """Get all search presets for a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM search_presets WHERE case_id = ? ORDER BY created_at DESC",
                (case_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_search_preset(self, preset_id: int):
        """Delete a search preset."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_presets WHERE id = ?", (preset_id,))
