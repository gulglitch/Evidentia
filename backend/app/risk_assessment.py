"""
Risk Assessment Module
Automatically calculates risk levels for evidence files based on multiple factors
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta


class RiskAssessment:
    """Calculate risk levels for evidence files."""
    
    # High-risk file extensions
    HIGH_RISK_EXTENSIONS = {
        '.exe', '.dll', '.bat', '.sh', '.msi', '.cmd', '.ps1', '.vbs',
        '.jar', '.app', '.deb', '.rpm', '.dmg', '.pkg', '.scr', '.com'
    }
    
    # Medium-risk file extensions
    MEDIUM_RISK_EXTENSIONS = {
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
        '.js', '.html', '.htm', '.xml', '.sql', '.db', '.sqlite'
    }
    
    # Size thresholds (in bytes)
    MEDIUM_SIZE_THRESHOLD = 100 * 1024 * 1024  # 100 MB
    HIGH_SIZE_THRESHOLD = 500 * 1024 * 1024    # 500 MB
    
    # Recent modification threshold (days)
    RECENT_MODIFICATION_DAYS = 7
    
    @classmethod
    def calculate_risk_level(cls, file_data: Dict[str, Any]) -> str:
        """
        Calculate risk level for a file based on multiple factors.
        
        Args:
            file_data: Dictionary containing file information
                      (file_extension, file_size, modified_time, file_name)
        
        Returns:
            Risk level: 'Low', 'Medium', or 'High'
        """
        risk_score = 0
        
        # Factor 1: File extension
        extension = file_data.get('file_extension', '').lower()
        if extension in cls.HIGH_RISK_EXTENSIONS:
            risk_score += 3
        elif extension in cls.MEDIUM_RISK_EXTENSIONS:
            risk_score += 2
        else:
            risk_score += 1
        
        # Factor 2: File size
        file_size = file_data.get('file_size', 0)
        if file_size > cls.HIGH_SIZE_THRESHOLD:
            risk_score += 2
        elif file_size > cls.MEDIUM_SIZE_THRESHOLD:
            risk_score += 1
        
        # Factor 3: Recent modification
        modified_time = file_data.get('modified_time', '')
        if modified_time:
            try:
                if isinstance(modified_time, str):
                    # Parse ISO format datetime
                    if 'T' in modified_time:
                        modified_dt = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                    else:
                        modified_dt = datetime.fromisoformat(modified_time)
                else:
                    modified_dt = modified_time
                
                # Check if modified recently
                days_ago = (datetime.now() - modified_dt.replace(tzinfo=None)).days
                if days_ago <= cls.RECENT_MODIFICATION_DAYS:
                    risk_score += 1
            except:
                pass
        
        # Factor 4: Suspicious filename patterns
        file_name = file_data.get('file_name', '').lower()
        suspicious_keywords = [
            'crack', 'keygen', 'hack', 'exploit', 'malware', 'virus',
            'trojan', 'backdoor', 'rootkit', 'payload', 'shell', 'inject'
        ]
        if any(keyword in file_name for keyword in suspicious_keywords):
            risk_score += 2
        
        # Determine final risk level
        if risk_score >= 5:
            return 'High'
        elif risk_score >= 3:
            return 'Medium'
        else:
            return 'Low'
    
    @classmethod
    def get_risk_factors(cls, file_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Get detailed risk factors for a file.
        
        Returns:
            Dictionary with risk factor descriptions
        """
        factors = {}
        
        extension = file_data.get('file_extension', '').lower()
        if extension in cls.HIGH_RISK_EXTENSIONS:
            factors['extension'] = f"Executable file type ({extension})"
        elif extension in cls.MEDIUM_RISK_EXTENSIONS:
            factors['extension'] = f"Archive or script file ({extension})"
        
        file_size = file_data.get('file_size', 0)
        if file_size > cls.HIGH_SIZE_THRESHOLD:
            factors['size'] = f"Very large file ({file_size / (1024**3):.2f} GB)"
        elif file_size > cls.MEDIUM_SIZE_THRESHOLD:
            factors['size'] = f"Large file ({file_size / (1024**2):.2f} MB)"
        
        modified_time = file_data.get('modified_time', '')
        if modified_time:
            try:
                if isinstance(modified_time, str):
                    if 'T' in modified_time:
                        modified_dt = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                    else:
                        modified_dt = datetime.fromisoformat(modified_time)
                else:
                    modified_dt = modified_time
                
                days_ago = (datetime.now() - modified_dt.replace(tzinfo=None)).days
                if days_ago <= cls.RECENT_MODIFICATION_DAYS:
                    factors['recent'] = f"Modified {days_ago} day(s) ago"
            except:
                pass
        
        file_name = file_data.get('file_name', '').lower()
        suspicious_keywords = [
            'crack', 'keygen', 'hack', 'exploit', 'malware', 'virus',
            'trojan', 'backdoor', 'rootkit', 'payload', 'shell', 'inject'
        ]
        found_keywords = [kw for kw in suspicious_keywords if kw in file_name]
        if found_keywords:
            factors['suspicious'] = f"Suspicious filename contains: {', '.join(found_keywords)}"
        
        return factors
    
    @classmethod
    def bulk_calculate_risk(cls, evidence_list: list) -> Dict[int, str]:
        """
        Calculate risk levels for multiple evidence files.
        
        Args:
            evidence_list: List of evidence dictionaries
        
        Returns:
            Dictionary mapping evidence ID to risk level
        """
        risk_levels = {}
        for evidence in evidence_list:
            evidence_id = evidence.get('id')
            risk_level = cls.calculate_risk_level(evidence)
            risk_levels[evidence_id] = risk_level
        
        return risk_levels
