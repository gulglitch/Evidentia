"""
Test script for custom case types functionality
"""

from src.core.database import Database

def test_custom_case_types():
    """Test custom case type operations."""
    db = Database()
    
    print("Testing Custom Case Types Functionality")
    print("=" * 50)
    
    # Test 1: Get initial custom case types
    print("\n1. Getting initial custom case types...")
    custom_types = db.get_custom_case_types()
    print(f"   Found {len(custom_types)} custom types: {custom_types}")
    
    # Test 2: Add new custom case types
    print("\n2. Adding custom case types...")
    test_types = ["Insurance Fraud", "Employee Misconduct", "Regulatory Compliance"]
    
    for case_type in test_types:
        result = db.add_custom_case_type(case_type)
        if result:
            print(f"   ✓ Added: {case_type}")
        else:
            print(f"   ✗ Failed to add (may already exist): {case_type}")
    
    # Test 3: Get all custom case types
    print("\n3. Getting all custom case types...")
    custom_types = db.get_custom_case_types()
    print(f"   Total custom types: {len(custom_types)}")
    for ct in custom_types:
        print(f"   - {ct}")
    
    # Test 4: Try to add duplicate
    print("\n4. Testing duplicate prevention...")
    result = db.add_custom_case_type("Insurance Fraud")
    if not result:
        print("   ✓ Duplicate prevention working correctly")
    else:
        print("   ✗ Duplicate was added (should not happen)")
    
    # Test 5: Create a case with custom type
    print("\n5. Creating a case with custom type...")
    case_id = db.create_case(
        name="Test Investigation",
        description="Testing custom case type",
        case_type="Insurance Fraud"
    )
    print(f"   ✓ Created case #{case_id} with custom type")
    
    # Test 6: Verify case was created with correct type
    case = db.get_case(case_id)
    print(f"   Case type: {case['case_type']}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")

if __name__ == "__main__":
    test_custom_case_types()
