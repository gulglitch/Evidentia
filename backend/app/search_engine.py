"""
Search Engine Module
Advanced search functionality with multi-field search and operators
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime


class SearchEngine:
    """Advanced search engine for evidence files."""
    
    @staticmethod
    def search_evidence(evidence_list: List[Dict[str, Any]], 
                       query: str,
                       search_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search evidence files using advanced query syntax.
        
        Args:
            evidence_list: List of evidence dictionaries
            query: Search query (supports operators)
            search_fields: List of fields to search in (default: all fields)
        
        Returns:
            List of matching evidence files
        """
        if not query or not query.strip():
            return evidence_list
        
        # Default search fields
        if search_fields is None:
            search_fields = ['file_name', 'file_extension', 'notes', 'metadata']
        
        # Parse query for operators
        parsed_query = SearchEngine._parse_query(query)
        
        results = []
        for evidence in evidence_list:
            if SearchEngine._matches_query(evidence, parsed_query, search_fields):
                results.append(evidence)
        
        return results
    
    @staticmethod
    def _parse_query(query: str) -> Dict[str, Any]:
        """
        Parse search query and extract operators.
        
        Supported operators:
        - "exact match" (quotes)
        - term1 OR term2
        - term1 NOT term2
        - term* (wildcard)
        - type:pdf (field-specific)
        - size:>10MB
        - created:2026-01-01..2026-03-01 (date range)
        """
        parsed = {
            'exact_phrases': [],
            'include_terms': [],
            'exclude_terms': [],
            'or_terms': [],
            'wildcards': [],
            'field_filters': {},
        }
        
        # Extract exact phrases (quoted text)
        exact_pattern = r'"([^"]+)"'
        for match in re.finditer(exact_pattern, query):
            parsed['exact_phrases'].append(match.group(1).lower())
        # Remove quoted text from query
        query = re.sub(exact_pattern, '', query)
        
        # Extract field-specific filters (field:value)
        field_pattern = r'(\w+):([^\s]+)'
        for match in re.finditer(field_pattern, query):
            field = match.group(1).lower()
            value = match.group(2)
            parsed['field_filters'][field] = value
        # Remove field filters from query
        query = re.sub(field_pattern, '', query)
        
        # Split remaining query into terms
        terms = query.split()
        
        i = 0
        while i < len(terms):
            term = terms[i].lower()
            
            # Handle OR operator
            if i + 2 < len(terms) and terms[i + 1].upper() == 'OR':
                parsed['or_terms'].append((term, terms[i + 2].lower()))
                i += 3
                continue
            
            # Handle NOT operator
            if i + 1 < len(terms) and terms[i].upper() == 'NOT':
                parsed['exclude_terms'].append(terms[i + 1].lower())
                i += 2
                continue
            
            # Handle wildcards
            if '*' in term:
                parsed['wildcards'].append(term)
            elif term and term not in ['or', 'not', 'and']:
                parsed['include_terms'].append(term)
            
            i += 1
        
        return parsed
    
    @staticmethod
    def _matches_query(evidence: Dict[str, Any], 
                      parsed_query: Dict[str, Any],
                      search_fields: List[str]) -> bool:
        """Check if evidence matches the parsed query."""
        
        # Build searchable text from specified fields
        searchable_text = []
        for field in search_fields:
            value = evidence.get(field, '')
            if value:
                searchable_text.append(str(value).lower())
        text = ' '.join(searchable_text)
        
        # Check exact phrases
        for phrase in parsed_query['exact_phrases']:
            if phrase not in text:
                return False
        
        # Check exclude terms (NOT operator)
        for term in parsed_query['exclude_terms']:
            if term in text:
                return False
        
        # Check include terms (must all be present)
        for term in parsed_query['include_terms']:
            if term not in text:
                return False
        
        # Check OR terms (at least one must be present)
        for term1, term2 in parsed_query['or_terms']:
            if term1 not in text and term2 not in text:
                return False
        
        # Check wildcards
        for wildcard in parsed_query['wildcards']:
            pattern = wildcard.replace('*', '.*')
            if not re.search(pattern, text):
                return False
        
        # Check field-specific filters
        for field, value in parsed_query['field_filters'].items():
            if not SearchEngine._matches_field_filter(evidence, field, value):
                return False
        
        return True
    
    @staticmethod
    def _matches_field_filter(evidence: Dict[str, Any], 
                             field: str, 
                             value: str) -> bool:
        """Check if evidence matches a field-specific filter."""
        
        # Type filter
        if field == 'type':
            file_ext = evidence.get('file_extension', '').lower()
            return value.lower() in file_ext or file_ext.replace('.', '') == value.lower()
        
        # Size filter
        if field == 'size':
            file_size = evidence.get('file_size', 0)
            return SearchEngine._matches_size_filter(file_size, value)
        
        # Date filters
        if field in ['created', 'modified']:
            date_field = f'{field}_time'
            date_value = evidence.get(date_field, '')
            return SearchEngine._matches_date_filter(date_value, value)
        
        # Status filter
        if field == 'status':
            return evidence.get('status', '').lower() == value.lower()
        
        # Risk filter
        if field == 'risk':
            return evidence.get('risk_level', '').lower() == value.lower()
        
        # Default: exact match on field value
        field_value = str(evidence.get(field, '')).lower()
        return value.lower() in field_value
    
    @staticmethod
    def _matches_size_filter(file_size: int, filter_value: str) -> bool:
        """Check if file size matches the filter."""
        try:
            # Parse size filter (e.g., ">10MB", "<5KB", "100MB")
            match = re.match(r'([<>]=?)?(\d+(?:\.\d+)?)(KB|MB|GB)?', filter_value, re.IGNORECASE)
            if not match:
                return False
            
            operator = match.group(1) or '=='
            size_value = float(match.group(2))
            unit = (match.group(3) or 'B').upper()
            
            # Convert to bytes
            multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
            size_bytes = size_value * multipliers.get(unit, 1)
            
            # Apply operator
            if operator == '>':
                return file_size > size_bytes
            elif operator == '>=':
                return file_size >= size_bytes
            elif operator == '<':
                return file_size < size_bytes
            elif operator == '<=':
                return file_size <= size_bytes
            else:
                return abs(file_size - size_bytes) < (size_bytes * 0.1)  # Within 10%
        except:
            return False
    
    @staticmethod
    def _matches_date_filter(date_value: str, filter_value: str) -> bool:
        """Check if date matches the filter."""
        try:
            if not date_value:
                return False
            
            # Parse date
            if 'T' in date_value:
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            else:
                date_obj = datetime.fromisoformat(date_value)
            date_obj = date_obj.replace(tzinfo=None)
            
            # Check for date range (e.g., "2026-01-01..2026-03-01")
            if '..' in filter_value:
                start_str, end_str = filter_value.split('..')
                start_date = datetime.fromisoformat(start_str)
                end_date = datetime.fromisoformat(end_str)
                return start_date <= date_obj <= end_date
            
            # Single date match
            filter_date = datetime.fromisoformat(filter_value)
            return date_obj.date() == filter_date.date()
        except:
            return False
    
    @staticmethod
    def highlight_matches(text: str, query: str) -> str:
        """
        Highlight matching terms in text (for UI display).
        
        Returns:
            Text with <mark> tags around matches
        """
        if not query or not text:
            return text
        
        # Simple highlighting for basic terms
        terms = query.lower().split()
        highlighted = text
        
        for term in terms:
            if term and term not in ['or', 'not', 'and']:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted = pattern.sub(f'<mark>{term}</mark>', highlighted)
        
        return highlighted
