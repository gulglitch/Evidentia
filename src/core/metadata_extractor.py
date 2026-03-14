"""
Metadata Extractor Module
Extracts metadata from various file types (.docx, .pdf, .jpg, .txt)
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Document processing
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
import exifread


class MetadataExtractor:
    """Extract metadata from different file types."""
    
    SUPPORTED_EXTENSIONS = {
        'documents': ['.docx', '.pdf', '.txt'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
    }
    
    def __init__(self):
        self.extractors = {
            '.docx': self._extract_docx_metadata,
            '.pdf': self._extract_pdf_metadata,
            '.txt': self._extract_txt_metadata,
            '.jpg': self._extract_image_metadata,
            '.jpeg': self._extract_image_metadata,
            '.png': self._extract_image_metadata,
            '.gif': self._extract_image_metadata,
            '.bmp': self._extract_image_metadata,
        }
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get basic file system metadata
        stat = path.stat()
        metadata = {
            'file_name': path.name,
            'file_path': str(path.absolute()),
            'file_extension': path.suffix.lower(),
            'file_size': stat.st_size,
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'accessed_time': datetime.fromtimestamp(stat.st_atime),
        }
        
        # Extract type-specific metadata
        ext = path.suffix.lower()
        if ext in self.extractors:
            try:
                specific_metadata = self.extractors[ext](file_path)
                metadata.update(specific_metadata)
            except Exception as e:
                metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _extract_docx_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from Word documents."""
        doc = Document(file_path)
        core_props = doc.core_properties
        
        return {
            'author': core_props.author,
            'title': core_props.title,
            'subject': core_props.subject,
            'keywords': core_props.keywords,
            'comments': core_props.comments,
            'last_modified_by': core_props.last_modified_by,
            'revision': core_props.revision,
            'doc_created': core_props.created,
            'doc_modified': core_props.modified,
            'category': core_props.category,
        }
    
    def _extract_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF files."""
        reader = PdfReader(file_path)
        info = reader.metadata
        
        metadata = {
            'page_count': len(reader.pages),
        }
        
        if info:
            metadata.update({
                'author': info.get('/Author', None),
                'title': info.get('/Title', None),
                'subject': info.get('/Subject', None),
                'creator': info.get('/Creator', None),
                'producer': info.get('/Producer', None),
                'pdf_created': info.get('/CreationDate', None),
                'pdf_modified': info.get('/ModDate', None),
            })
        
        return metadata
    
    def _extract_txt_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from text files."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return {
            'line_count': content.count('\n') + 1,
            'word_count': len(content.split()),
            'character_count': len(content),
        }
    
    def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from image files."""
        metadata = {}
        
        # Get basic image info using PIL
        with Image.open(file_path) as img:
            metadata['width'] = img.width
            metadata['height'] = img.height
            metadata['image_format'] = img.format
            metadata['mode'] = img.mode
        
        # Get EXIF data for JPEG files
        if file_path.lower().endswith(('.jpg', '.jpeg')):
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
                exif_mapping = {
                    'EXIF DateTimeOriginal': 'date_taken',
                    'EXIF DateTimeDigitized': 'date_digitized',
                    'Image Make': 'camera_make',
                    'Image Model': 'camera_model',
                    'EXIF ExposureTime': 'exposure_time',
                    'EXIF FNumber': 'f_number',
                    'EXIF ISOSpeedRatings': 'iso',
                    'GPS GPSLatitude': 'gps_latitude',
                    'GPS GPSLongitude': 'gps_longitude',
                }
                
                for tag, key in exif_mapping.items():
                    if tag in tags:
                        metadata[key] = str(tags[tag])
        
        return metadata
    
    def is_supported(self, file_path: str) -> bool:
        """Check if a file type is supported for metadata extraction."""
        ext = Path(file_path).suffix.lower()
        return ext in self.extractors
