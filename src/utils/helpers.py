"""
Helper Utilities Module
Common helper functions used across the application
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Union


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_datetime(dt: Union[datetime, str, None], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object or string
        format_str: Output format string
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ""
    if isinstance(dt, str):
        return dt
    return dt.strftime(format_str)


def get_file_category(extension: str) -> str:
    """
    Get file category based on extension.
    
    Args:
        extension: File extension (with or without dot)
        
    Returns:
        Category string
    """
    ext = extension.lower().lstrip('.')
    
    categories = {
        'documents': ['docx', 'doc', 'pdf', 'txt', 'rtf', 'odt'],
        'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
        'spreadsheets': ['xlsx', 'xls', 'csv', 'ods'],
        'presentations': ['pptx', 'ppt', 'odp'],
        'archives': ['zip', 'rar', '7z', 'tar', 'gz'],
        'emails': ['eml', 'msg', 'pst'],
    }
    
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    
    return 'other'


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, create if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def safe_filename(filename: str) -> str:
    """
    Remove or replace unsafe characters from filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename string
    """
    # Characters not allowed in Windows filenames
    unsafe_chars = '<>:"/\\|?*'
    
    result = filename
    for char in unsafe_chars:
        result = result.replace(char, '_')
    
    return result


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with suffix.
    
    Args:
        text: Original string
        max_length: Maximum length including suffix
        suffix: String to append when truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def calculate_hash(file_path: str, algorithm: str = 'md5') -> Optional[str]:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
        
    Returns:
        Hash string or None if error
    """
    import hashlib
    
    algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
    }
    
    if algorithm not in algorithms:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    try:
        hasher = algorithms[algorithm]()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError):
        return None


def get_relative_time(dt: datetime) -> str:
    """
    Get human-readable relative time string.
    
    Args:
        dt: Datetime object
        
    Returns:
        Relative time string (e.g., "2 hours ago")
    """
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return dt.strftime('%Y-%m-%d')
