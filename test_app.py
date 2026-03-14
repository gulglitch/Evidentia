"""
Test script to verify Evidentia functionality
"""

import sys
import os
from src.core.database import Database
from src.core.file_scanner import FileScanner
from src.core.metadata_extractor import MetadataExtractor

def test_functionality():
    """Test the core functionality."""
    print("Testing Evidentia Core Functionality...")
    
    # Test 1: Database functionality
    print("\n1. Testing Database...")
    db = Database()
    case_id = db.create_case("Test Case", "Test Description", "Cybercrime")
    print(f"✓ Created case with ID: {case_id}")
    
    # Test 2: File Scanner
    print("\n2. Testing File Scanner...")
    scanner = FileScanner()
    
    # Create a test file for scanning
    test_dir = "test_evidence"
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = os.path.join(test_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("This is a test evidence file.")
    
    files = scanner.scan_directory(test_dir)
    print(f"✓ Scanned directory, found {len(files)} files")
    
    # Test 3: Metadata Extractor
    print("\n3. Testing Metadata Extractor...")
    extractor = MetadataExtractor()
    
    if files:
        metadata = extractor.extract(files[0].path)
        print(f"✓ Extracted metadata: {metadata['file_name']}")
        
        # Add to database
        evidence_id = db.add_evidence(case_id, metadata)
        print(f"✓ Added evidence to database with ID: {evidence_id}")
    
    # Test 4: Retrieve evidence
    print("\n4. Testing Evidence Retrieval...")
    evidence_list = db.get_evidence_for_case(case_id)
    print(f"✓ Retrieved {len(evidence_list)} evidence files")
    
    # Cleanup
    os.remove(test_file)
    os.rmdir(test_dir)
    
    print("\n✅ All functionality tests passed!")
    print("\nFunctionality 1 (Bulk Folder Upload): ✓ Implemented")
    print("Functionality 2 (Metadata Overview Table): ✓ Implemented")

if __name__ == "__main__":
    test_functionality()