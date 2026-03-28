"""
Timeline Generator Module
Generates timeline data for visualization of evidence chronologically
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from backend.app.database import Database


class TimelineGenerator:
    """Generates timeline data for evidence visualization."""
    
    def __init__(self, database: Database = None):
        """
        Initialize the timeline generator.
        
        Args:
            database: Database instance (creates new if None)
        """
        self.database = database or Database()
    
    def get_timeline_data(self, case_id: int, date_from: str = None, date_to: str = None, 
                         date_field: str = 'modified_time') -> Dict[str, Any]:
        """
        Get timeline data for a case with optional date filtering.
        
        Args:
            case_id: Case ID to get timeline for
            date_from: Start date filter (ISO format string)
            date_to: End date filter (ISO format string)
            date_field: Which date field to use ('created_time' or 'modified_time')
            
        Returns:
            Dictionary containing evidence list, milestones, and date range
        """
        # Get all evidence for the case
        all_evidence = self.database.get_evidence_for_case(case_id)
        
        # Filter by date range if specified
        if date_from or date_to:
            all_evidence = self.filter_by_date_range(all_evidence, date_from, date_to, date_field)
        
        # Get milestones for the case
        milestones = self.database.get_milestones(case_id)
        
        # Calculate date range
        date_range = self.calculate_date_range(all_evidence, date_field)
        
        return {
            'evidence': all_evidence,
            'milestones': milestones,
            'date_range': date_range,
            'total_count': len(all_evidence),
            'date_field': date_field
        }
    
    def calculate_date_range(self, evidence_list: List[Dict[str, Any]], 
                            date_field: str = 'modified_time') -> Tuple[Optional[str], Optional[str]]:
        """
        Calculate the earliest and latest dates in evidence list.
        
        Args:
            evidence_list: List of evidence dictionaries
            date_field: Which date field to use
            
        Returns:
            Tuple of (earliest_date, latest_date) as ISO strings
        """
        if not evidence_list:
            return (None, None)
        
        dates = []
        for evidence in evidence_list:
            date_str = evidence.get(date_field)
            if date_str:
                try:
                    dt = self._parse_date(date_str)
                    if dt:
                        dates.append(dt)
                except:
                    continue
        
        if not dates:
            return (None, None)
        
        earliest = min(dates)
        latest = max(dates)
        
        return (earliest.isoformat(), latest.isoformat())
    
    def filter_by_date_range(self, evidence_list: List[Dict[str, Any]], 
                            date_from: str = None, date_to: str = None,
                            date_field: str = 'modified_time') -> List[Dict[str, Any]]:
        """
        Filter evidence by date range.
        
        Args:
            evidence_list: List of evidence dictionaries
            date_from: Start date (ISO format string)
            date_to: End date (ISO format string)
            date_field: Which date field to filter on
            
        Returns:
            Filtered list of evidence
        """
        if not date_from and not date_to:
            return evidence_list
        
        # Parse filter dates
        from_dt = self._parse_date(date_from) if date_from else None
        to_dt = self._parse_date(date_to) if date_to else None
        
        filtered = []
        for evidence in evidence_list:
            date_str = evidence.get(date_field)
            if not date_str:
                continue
            
            try:
                dt = self._parse_date(date_str)
                if not dt:
                    continue
                
                # Check if within range
                if from_dt and dt < from_dt:
                    continue
                if to_dt and dt > to_dt:
                    continue
                
                filtered.append(evidence)
            except:
                continue
        
        return filtered
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        # Try different date formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # Try ISO format
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def get_evidence_by_date(self, case_id: int, target_date: str, 
                            date_field: str = 'modified_time') -> List[Dict[str, Any]]:
        """
        Get all evidence files for a specific date.
        
        Args:
            case_id: Case ID
            target_date: Target date (YYYY-MM-DD)
            date_field: Which date field to check
            
        Returns:
            List of evidence for that date
        """
        all_evidence = self.database.get_evidence_for_case(case_id)
        target_dt = self._parse_date(target_date)
        
        if not target_dt:
            return []
        
        matching = []
        for evidence in all_evidence:
            date_str = evidence.get(date_field)
            if not date_str:
                continue
            
            try:
                dt = self._parse_date(date_str)
                if dt and dt.date() == target_dt.date():
                    matching.append(evidence)
            except:
                continue
        
        return matching
