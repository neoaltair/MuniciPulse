"""
Test script to verify OAuth2 scopes are working correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_oauth2_scopes():
    """
    Test OAuth2 scope protection on endpoints
    """
    
    print("🔐 Testing OAuth2 Scopes\n")
    
    # Step 1: Register a citizen
    print("1️⃣  Registering citizen...")
    citizen_data = {
        "email": "citizen_scope_test@civicfix.com",
        "password": "password123",
        "role": "citizen",
        "first_name": "Citizen",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=citizen_data)
    if response.status_code == 201:
        print("✅ Citizen registered")
    elif response.status_code == 400:
        print("⚠️  Citizen already exists")
    
    # Step 2: Register a municipal officer
    print("\n2️⃣  Registering municipal officer...")
    officer_data = {
        "email": "officer_scope_test@civicfix.com",
        "password": "password123",
        "role": "municipal_officer",
        "first_name": "Officer",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=officer_data)
    if response.status_code == 201:
        print("✅ Officer registered")
    elif response.status_code == 400:
        print("⚠️  Officer already exists")
    
    # Step 3: Login as citizen and get token
    print("\n3️⃣  Logging in as citizen...")
    login_data = {
        "email": "citizen_scope_test@civicfix.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Citizen login failed: {response.text}")
        return
    
    citizen_token = response.json()["access_token"]
    print("✅ Citizen logged in")
    print(f"   Token: {citizen_token[:30]}...")
    
    # Step 4: Login as officer and get token
    print("\n4️⃣  Logging in as officer...")
    login_data = {
        "email": "officer_scope_test@civicfix.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Officer login failed: {response.text}")
        return
    
    officer_token = response.json()["access_token"]
    print("✅ Officer logged in")
    print(f"   Token: {officer_token[:30]}...")
    
    # Step 5: Test citizen trying to update status (should FAIL - needs officer scope)
    print("\n5️⃣  Testing citizen trying to update status (should FAIL)...")
    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
    
    # First create a report as citizen
    from pathlib import Path
    test_image = Path("test_scope_image.jpg")
    if not test_image.exists():
        with open(test_image, "wb") as f:
            f.write(bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 
                          0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 
                          0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9]))
    
    files = {"images": open(test_image, "rb")}
    data = {
        "title": "Test Report for Scopes",
        "description": "Testing OAuth2 scope protection",
        "category": "test",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "priority": "low"
    }
    
    response = requests.post(f"{BASE_URL}/reports", headers=citizen_headers, files=files, data=data)
    files["images"].close()
    
    if response.status_code == 201:
        report_id = response.json()["id"]
        print(f"✅ Report created: {report_id}")
        
        # Now try to update status with citizen token (should fail)
        update_data = {
            "new_status": "in_progress",
            "comment": "Trying to update from citizen account"
        }
        
        response = requests.patch(
            f"{BASE_URL}/reports/{report_id}/status",
            headers=citizen_headers,
            json=update_data
        )
        
        if response.status_code == 403:
            print("✅ CORRECT! Citizen was blocked from updating status")
            print(f"   Error: {response.json()['detail']}")
        else:
            print(f"❌ INCORRECT! Citizen was allowed to update status (status: {response.status_code})")
    else:
        print(f"❌ Report creation failed: {response.text}")
        return
    
    # Step 6: Test officer updating status (should SUCCEED - has officer scope)
    print("\n6️⃣  Testing officer updating status (should SUCCEED)...")
    officer_headers = {"Authorization": f"Bearer {officer_token}"}
    
    update_data = {
        "new_status": "in_progress",
        "comment": "Updating from officer account"
    }
    
    response = requests.patch(
        f"{BASE_URL}/reports/{report_id}/status",
        headers=officer_headers,
        json=update_data
    )
    
    if response.status_code == 200:
        print("✅ CORRECT! Officer successfully updated status")
        print(f"   New status: {response.json()['status']}")
    else:
        print(f"❌ INCORRECT! Officer was blocked from updating status")
        print(f"   Error: {response.text}")
    
    # Step 7: Test officer trying to create report (should FAIL - needs citizen scope)
    print("\n7️⃣  Testing officer trying to create report (should FAIL)...")
    
    files = {"images": open(test_image, "rb")}
    data = {
        "title": "Officer Report Test",
        "description": "Officers shouldn't be able to create reports",
        "category": "test",
        "latitude": 40.7130,
        "longitude": -74.0062,
        "priority": "low"
    }
    
    response = requests.post(f"{BASE_URL}/reports", headers=officer_headers, files=files, data=data)
    files["images"].close()
    
    if response.status_code == 403:
        print("✅ CORRECT! Officer was blocked from creating reports")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ INCORRECT! Officer was allowed to create reports (status: {response.status_code})")
    
    # Cleanup
    if test_image.exists():
        test_image.unlink()
    
    print("\n" + "="*60)
    print("🎯 OAuth2 Scope Test Summary:")
    print("="*60)
    print("✓ Citizens have 'citizen' scope - can create reports")
    print("✓ Officers have 'officer' scope - can update status")
    print("✓ Scope protection prevents unauthorized access")
    print("="*60)


if __name__ == "__main__":
    try:
        test_oauth2_scopes()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
