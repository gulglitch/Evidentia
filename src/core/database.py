"""
Database Module
SQLite database operations for storing evidence and case data
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class Database:
    """SQLite database handler for Evidentia."""
    
    def __init__(self, db_path: str = "data/evidentia.db"):
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
            
            # Cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    case_type TEXT,
                    status TEXT DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            # Activity log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
    
    # Case operations
    def create_case(self, name: str, description: str = "", case_type: str = "") -> int:
        """Create a new case and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cases (name, description, case_type) VALUES (?, ?, ?)",
                (name, description, case_type)
            )
            return cursor.lastrowid
    
    def get_case(self, case_id: int) -> Optional[Dict[str, Any]]:
        """Get a case by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_cases(self) -> List[Dict[str, Any]]:
        """Get all cases."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cases ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_case_status(self, case_id: int, status: str):
        """Update the status of a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE cases SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.now(), case_id)
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
    
    # Activity log operations
    def log_activity(self, case_id: int, action: str, details: str = ""):
        """Log an activity for a case."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_log (case_id, action, details) VALUES (?, ?, ?)",
                (case_id, action, details)
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
    
    # Statistics
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
