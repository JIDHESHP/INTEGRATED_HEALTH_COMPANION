import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_vitals_flow():
    print("--- Starting Vitals Flow Test ---")
    
    # 1. Register/Login to get token
    session = requests.Session()
    email = f"test_user_{int(time.time())}@example.com"
    password = "password123"
    
    print(f"1. Registering user: {email}")
    reg_res = session.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Test User",
        "email": email,
        "password": password,
        "confirm_password": password
    })
    
    if reg_res.status_code != 201:
        # Maybe user exists, try login
        print(f"   Registration failed ({reg_res.status_code}), trying login...")
    
    print("2. Logging in...")
    login_res = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password
    })
    
    if login_res.status_code != 200:
        print(f"!!! Login failed: {login_res.text}")
        return
    
    token = login_res.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("   Login successful, token received.")
    
    # 2. Post Vitals
    print("\n3. Posting Vitals...")
    vitals_data = {
        "heart_rate": "75",
        "bp_systolic": "120",
        "bp_diastolic": "80",
        "blood_sugar": "95"
    }
    
    # Using json instead of data to avoid 400 Bad Request (backend expects json or multipart)
    post_res = session.post(
        f"{BASE_URL}/api/health/log",
        headers=headers,
        json=vitals_data 
    )
    
    # Actually, let's verify if the backend handles form-data correctly.
    # To send multipart/form-data with requests, we can just pass an empty files dict or just let it interpret data?
    # No, to send multipart, we typically need 'files'. 
    # Let's allow request to choose, or force it.
    
    print(f"   POST response: {post_res.status_code} - {post_res.text}")
    
    if post_res.status_code != 201:
        print("!!! Posting vitals failed.")
        return

    # 3. Check Latest
    print("\n4. Checking Latest Vitals...")
    latest_res = session.get(f"{BASE_URL}/api/health/latest", headers=headers)
    print(f"   GET Latest response: {latest_res.status_code} - {latest_res.text}")
    latest_data = latest_res.json()
    
    if str(latest_data.get('heart_rate')) == "75":
        print("   MATCH: Latest heart rate matches.")
    else:
        print(f"   MISMATCH: Expected 75, got {latest_data.get('heart_rate')}")

    # 4. Check Logs
    print("\n5. Checking Logs...")
    logs_res = session.get(f"{BASE_URL}/api/health/logs", headers=headers)
    print(f"   GET Logs response: {logs_res.status_code}")
    logs_data = logs_res.json()
    
    if len(logs_data) > 0:
        print(f"   Found {len(logs_data)} logs.")
        first_log = logs_data[0]
        print(f"   Top log timestamp: {first_log.get('timestamp')}")
        if str(first_log.get('heart_rate')) == "75":
            print("   MATCH: Top log heart rate matches.")
        else:
             print(f"   MISMATCH: Expected 75, got {first_log.get('heart_rate')}")
    else:
        print("   !!! No logs found.")

if __name__ == "__main__":
    try:
        test_vitals_flow()
    except Exception as e:
        print(f"An error occurred: {e}")
