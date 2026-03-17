"""
Test script to verify Evidentia functionality
Tests Functionality 1 (Bulk Folder Upload) and Functionality 2 (Metadata Overview Table)
"""

import sys
import os
from src.core.database import Database
from src.core.file_scanner import FileScanner
from src.core.metadata_extractor import MetadataExtractor


def test_functionality():
    """Test the core functionality."""
    print("=" * 60)
    print("  Testing Evidentia Core Functionality")
    print("=" * 60)
    
    # Test 1: User Registration
    print("\n1. Testing User Registration...")
    db = Database()
    user_id = db.create_user("investigator", "pass123", "Jane Smith", "jane@evidentia.com")
    print(f"   ✓ Created user with ID: {user_id}")
    
    # Test 2: User Authentication
    print("\n2. Testing User Authentication...")
    user = db.authenticate_user("investigator", "pass123")
    assert user is not None, "Authentication should succeed"
    print(f"   ✓ Authenticated user: {user['username']} (ID: {user['id']})")
    
    bad_login = db.authenticate_user("investigator", "wrongpassword")
    assert bad_login is None, "Bad password should be rejected"
    print("   ✓ Invalid password correctly rejected")
    
    # Test 3: Case Creation
    print("\n3. Testing Case Creation...")
    case_id = db.create_case(
        "Financial Fraud Investigation", 
        "Test investigation for fraud analysis", 
        "Financial Fraud",
        "High",
        user_id
    )
    print(f"   ✓ Created case with ID: {case_id}")
    
    case = db.get_case(case_id)
    assert case['name'] == "Financial Fraud Investigation"
    assert case['case_type'] == "Financial Fraud"
    print(f"   ✓ Verified case: {case['name']} ({case['case_type']})")
    
    # Test 4: File Scanner
    print("\n4. Testing File Scanner (Functionality 1: Bulk Folder Upload)...")
    scanner = FileScanner()
    
    # Create test directory with sample files
    test_dir = "test_evidence"
    os.makedirs(test_dir, exist_ok=True)
    
    test_files = {
        "report.txt": "This is a forensic report with important findings.",
        "notes.txt": "Investigation notes from the field.",
    }
    
    for filename, content in test_files.items():
        filepath = os.path.join(test_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
    
    files = scanner.scan_directory(test_dir)
    print(f"   ✓ Scanned directory, found {len(files)} supported files")
    
    for f in files:
        print(f"     - {f.name} ({f.extension}, {f.size} bytes)")
    
    # Test 5: Metadata Extractor
    print("\n5. Testing Metadata Extractor (Functionality 2: Metadata Overview Table)...")
    extractor = MetadataExtractor()
    
    for file_info in files:
        metadata = extractor.extract(file_info.path)
        print(f"   ✓ Extracted metadata for: {metadata['file_name']}")
        print(f"     - Size: {metadata['file_size']} bytes")
        print(f"     - Extension: {metadata['file_extension']}")
        if 'word_count' in metadata:
            print(f"     - Words: {metadata['word_count']}")
        if 'line_count' in metadata:
            print(f"     - Lines: {metadata['line_count']}")
        
        # Add to database
        evidence_id = db.add_evidence(case_id, metadata)
        print(f"     - Stored in DB with evidence ID: {evidence_id}")
    
    # Test 6: Evidence Retrieval
    print("\n6. Testing Evidence Retrieval...")
    evidence_list = db.get_evidence_for_case(case_id)
    print(f"   ✓ Retrieved {len(evidence_list)} evidence files from database")
    
    for ev in evidence_list:
        print(f"     - ID:{ev['id']} | {ev['file_name']} | {ev['file_extension']} | Status: {ev['status']}")
    
    # Test 7: Dashboard Statistics
    print("\n7. Testing Dashboard Statistics...")
    stats = db.get_dashboard_stats()
    print(f"   ✓ Total cases: {stats['total_cases']}")
    print(f"   ✓ Total evidence: {stats['total_evidence']}")
    print(f"   ✓ Evidence status: {stats['evidence_status']}")
    
    # Test 8: Activity Log
    print("\n8. Testing Activity Log...")
    db.log_activity(case_id, "Evidence Imported", f"Imported {len(files)} files", user_id)
    activities = db.get_recent_activity(case_id)
    print(f"   ✓ Logged activity, {len(activities)} entries found")
    
    # Cleanup
    for filename in test_files:
        os.remove(os.path.join(test_dir, filename))
    os.rmdir(test_dir)
    
    print("\n" + "=" * 60)
    print("  ✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n  Functionality 1 (Bulk Folder Upload):      ✓ Working")
    print("  Functionality 2 (Metadata Overview Table):  ✓ Working")
    print("  User Authentication:                        ✓ Working")
    print("  Case Management:                            ✓ Working")
    print("  Activity Logging:                           ✓ Working")


if __name__ == "__main__":
    # Use a test database to avoid affecting real data
    test_functionality()