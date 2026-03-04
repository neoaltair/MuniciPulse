"""
Test script to verify duplicate detection functionality
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_duplicate_detection():
    """
    Test the 10-meter radius duplicate detection feature
    """
    
    print("🧪 Testing CivicFix Duplicate Detection\n")
    
    # Step 1: Register a test citizen
    print("1️⃣  Registering test citizen...")
    register_data = {
        "email": "testcitizen@civicfix.com",
        "password": "testpass123",
        "role": "citizen",
        "first_name": "Test",
        "last_name": "Citizen",
        "phone_number": "+1234567890"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 201:
        print("✅ Citizen registered successfully")
    elif response.status_code == 400:
        print("⚠️  Citizen already exists, continuing...")
    else:
        print(f"❌ Registration failed: {response.text}")
        return
    
    # Step 2: Login
    print("\n2️⃣  Logging in...")
    login_data = {
        "email": "testcitizen@civicfix.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 3: Create first report
    print("\n3️⃣  Creating first report at (40.7128, -74.0060)...")
    
    # Create a dummy image file
    test_image_path = Path("test_image.jpg")
    if not test_image_path.exists():
        # Create a minimal valid JPEG
        with open(test_image_path, "wb") as f:
            # JPEG header
            f.write(bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 
                          0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 
                          0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9]))
    
    files = {"images": open(test_image_path, "rb")}
    data = {
        "title": "Large Pothole on Main Street",
        "description": "Dangerous pothole causing traffic issues",
        "category": "pothole",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "priority": "high"
    }
    
    response = requests.post(f"{BASE_URL}/reports", headers=headers, files=files, data=data)
    files["images"].close()
    
    if response.status_code != 201:
        print(f"❌ First report creation failed: {response.text}")
        return
    
    first_report = response.json()
    print(f"✅ First report created: ID = {first_report['id']}")
    print(f"   - is_linked: {first_report.get('is_linked', False)}")
    print(f"   - linked_to_report_id: {first_report.get('linked_to_report_id', 'None')}")
    
    # Step 4: Create second report WITHIN 10 meters
    print("\n4️⃣  Creating second report at (40.71281, -74.00601) - ~1m away...")
    
    files = {"images": open(test_image_path, "rb")}
    data = {
        "title": "Same pothole from different angle",
        "description": "I think this is the same pothole",
        "category": "pothole",
        "latitude": 40.71281,  # ~1 meter north
        "longitude": -74.00601,  # ~1 meter east
        "priority": "medium"
    }
    
    response = requests.post(f"{BASE_URL}/reports", headers=headers, files=files, data=data)
    files["images"].close()
    
    if response.status_code != 201:
        print(f"❌ Second report creation failed: {response.text}")
        return
    
    second_report = response.json()
    print(f"✅ Second report created: ID = {second_report['id']}")
    print(f"   - is_linked: {second_report.get('is_linked', False)}")
    print(f"   - linked_to_report_id: {second_report.get('linked_to_report_id', 'None')}")
    print(f"   - linked_reason: {second_report.get('linked_reason', 'None')}")
    
    if second_report.get('is_linked'):
        print("\n🎉 SUCCESS! Duplicate detection worked!")
        print(f"   Report {second_report['id']} was linked to {second_report['linked_to_report_id']}")
    else:
        print("\n⚠️  WARNING: Reports were not linked. This may indicate an issue.")
    
    # Step 5: Create third report OUTSIDE 10 meters
    print("\n5️⃣  Creating third report at (40.7138, -74.0070) - ~100m away...")
    
    files = {"images": open(test_image_path, "rb")}
    data = {
        "title": "Different pothole on Oak Street",
        "description": "This is a completely different pothole",
        "category": "pothole",
        "latitude": 40.7138,  # ~100 meters north
        "longitude": -74.0070,  # ~100 meters west
        "priority": "low"
    }
    
    response = requests.post(f"{BASE_URL}/reports", headers=headers, files=files, data=data)
    files["images"].close()
    
    if response.status_code != 201:
        print(f"❌ Third report creation failed: {response.text}")
        return
    
    third_report = response.json()
    print(f"✅ Third report created: ID = {third_report['id']}")
    print(f"   - is_linked: {third_report.get('is_linked', False)}")
    print(f"   - linked_to_report_id: {third_report.get('linked_to_report_id', 'None')}")
    
    if not third_report.get('is_linked'):
        print("\n✅ CORRECT! Third report was NOT linked (too far away)")
    else:
        print("\n⚠️  WARNING: Third report was linked but shouldn't be.")
    
    # Step 6: Get linked reports
    print(f"\n6️⃣  Getting all reports linked to first report...")
    response = requests.get(
        f"{BASE_URL}/reports/{first_report['id']}/linked",
        headers=headers
    )
    
    if response.status_code == 200:
        linked_reports = response.json()
        print(f"✅ Found {len(linked_reports)} linked report(s):")
        for report in linked_reports:
            print(f"   - {report['id']}: {report['title']}")
    
    # Cleanup
    if test_image_path.exists():
        test_image_path.unlink()
    
    print("\n" + "="*60)
    print("🎯 Test Summary:")
    print("="*60)
    print(f"First Report:  Created independently (no duplicates)")
    print(f"Second Report: Should be LINKED to first (within 10m)")
    print(f"Third Report:  Should be INDEPENDENT (outside 10m)")
    print("="*60)


if __name__ == "__main__":
    try:
        test_duplicate_detection()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
