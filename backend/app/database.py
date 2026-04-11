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
    
    def update_evidence_status(self, evidence_id: int, status: str):
        """Update the status of an evidence file."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE evidence SET status = ? WHERE id = ?",
                (status, evidence_id)
            )
    
    def update_evidence_risk(self, evidence_id: int, risk_level: str):
        """Update the risk level of an evidence file."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE evidence SET risk_level = ? WHERE id = ?",
                (risk_level, evidence_id)
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
            cursor.execute(
                "INSERT INTO activity_log (case_id, user_id, action, details) VALUES (?, ?, ?, ?)",
                (case_id, user_id, action, details)
            )
    
    def get_recent_activity(self, case_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity for a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM activity_log WHERE case_id = ? ORDER BY timestamp DESC LIMIT ?",
                (case_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ──────────────────────────────────────────────
    # Statistics
    # ──────────────────────────────────────────────
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get overall statistics for the dashboard."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total cases
            cursor.execute("SELECT COUNT(*) as total FROM cases")
            total_cases = cursor.fetchone()['total']
            
            # Case status breakdown
            cursor.execute("SELECT status, COUNT(*) as count FROM cases GROUP BY status")
            case_status = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Case type breakdown
            cursor.execute("SELECT case_type, COUNT(*) as count FROM cases GROUP BY case_type")
            case_types = {row['case_type']: row['count'] for row in cursor.fetchall()}
            
            # Total evidence files
            cursor.execute("SELECT COUNT(*) as total FROM evidence")
            total_evidence = cursor.fetchone()['total']
            
            # Evidence status breakdown
            cursor.execute("SELECT status, COUNT(*) as count FROM evidence GROUP BY status")
            evidence_status = {row['status']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total_cases': total_cases,
                'case_status': case_status,
                'case_types': case_types,
                'total_evidence': total_evidence,
                'evidence_status': evidence_status,
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
    
    def bulk_update_status(self, evidence_ids: List[int], status: str):
        """
        Update status for multiple evidence files.
        
        Args:
            evidence_ids: List of evidence IDs
            status: New status value
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(evidence_ids))
            cursor.execute(
                f"UPDATE evidence SET status = ? WHERE id IN ({placeholders})",
                [status] + evidence_ids
            )
    
    def update_evidence_notes(self, evidence_id: int, notes: str):
        """Update notes for an evidence file."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE evidence SET notes = ? WHERE id = ?",
                (notes, evidence_id)
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
