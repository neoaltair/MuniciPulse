import requests
import json

# Test registration endpoint
url = "http://localhost:8000/auth/register"
headers = {"Content-Type": "application/json"}
data = {
    "username": "testuser123",
    "email": "test123@example.com",
    "password": "password123",
    "role": "citizen",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": None
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")
