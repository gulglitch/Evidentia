"""
File Scanner Module
Recursively scans folders and collects file information
"""

import os
from pathlib import Path
from typing import List, Generator, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    """Data class to hold basic file information."""
    name: str
    path: str
    extension: str
    size: int
    created: datetime
    modified: datetime
    
    @classmethod
    def from_path(cls, file_path: Path) -> 'FileInfo':
        """Create FileInfo from a Path object."""
        stat = file_path.stat()
        return cls(
            name=file_path.name,
            path=str(file_path.absolute()),
            extension=file_path.suffix.lower(),
            size=stat.st_size,
            created=datetime.fromtimestamp(stat.st_ctime),
            modified=datetime.fromtimestamp(stat.st_mtime),
        )


class FileScanner:
    """Scan directories for files and collect information."""
    
    # Supported file extensions for forensic analysis
    SUPPORTED_EXTENSIONS = {
        # Documents
        '.docx', '.doc', '.pdf', '.txt', '.rtf', '.odt',
        # Images
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.webp',
        # Videos
        '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v',
        # Spreadsheets
        '.xlsx', '.xls', '.csv', '.ods',
        # Presentations
        '.pptx', '.ppt', '.odp',
        # Archives
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
        # Executables
        '.exe', '.dll', '.bat', '.sh', '.msi',
        # Web
        '.html', '.htm', '.css', '.js', '.json', '.xml',
        # Databases
        '.db', '.sqlite', '.mdb', '.accdb',
        # Logs
        '.log', '.txt',
        # Other
        '.ini', '.cfg', '.conf', '.yaml', '.yml',
    }
    
    def __init__(self, supported_extensions: Optional[set] = None):
        """
        Initialize the file scanner.
        
        Args:
            supported_extensions: Set of extensions to scan for.
                                  Defaults to common forensic file types.
        """
        self.extensions = supported_extensions or self.SUPPORTED_EXTENSIONS
    
    def scan_directory(self, directory: str, recursive: bool = True, all_files: bool = False) -> List[str]:
        """
        Scan a directory for files.
        
        Args:
            directory: Path to the directory to scan
            recursive: Whether to scan subdirectories
            all_files: If True, scan all files. If False, only scan supported extensions.
            
        Returns:
            List of file paths
        """
        files = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise NotADirectoryError(f"Directory not found: {directory}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                # If all_files is True, include everything. Otherwise filter by extension
                if all_files or file_path.suffix.lower() in self.extensions:
                    try:
                        files.append(str(file_path.absolute()))
                    except (PermissionError, OSError):
                        # Skip files we can't access
                        continue
        
        return files
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract basic metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata
        """
        import hashlib
        
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        try:
            stat = path.stat()
            
            # Calculate file hash
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            return {
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'hash': hash_md5.hexdigest(),
            }
        except Exception as e:
            return {
                'size': 0,
                'created': '',
                'modified': '',
                'hash': '',
                'error': str(e)
            }
    
    def _scan_generator(self, directory: str, recursive: bool) -> Generator[FileInfo, None, None]:
        """Generator that yields FileInfo objects."""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise NotADirectoryError(f"Directory not found: {directory}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.extensions:
                try:
                    yield FileInfo.from_path(file_path)
                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue
    
    def get_file_count(self, directory: str, recursive: bool = True) -> int:
        """Count the number of supported files in a directory."""
        count = 0
        for _ in self._scan_generator(directory, recursive):
            count += 1
        return count
    
    def scan_with_progress(self, directory: str, recursive: bool = True) -> Generator[tuple, None, None]:
        """
        Scan directory and yield progress information.
        
        Yields:
            Tuple of (current_count, FileInfo)
        """
        count = 0
        for file_info in self._scan_generator(directory, recursive):
            count += 1
            yield (count, file_info)
