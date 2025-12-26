import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def verify_update_logic():
    print("--- Starting Vitals Update Test ---")
    
    session = requests.Session()
    email = f"test_update_{int(time.time())}@example.com"
    password = "password123"
    
    # 1. Register/Login
    print(f"1. Registering user: {email}")
    session.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Update Test",
        "email": email,
        "password": password,
        "confirm_password": password
    })
    
    login_res = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password
    })
    
    if login_res.status_code != 200:
        print("Login failed")
        return
        
    token = login_res.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Post First Entry
    entry_a = {
        "heart_rate": "60",
        "bp_systolic": "110",
        "bp_diastolic": "70",
        "blood_sugar": "80"
    }
    print(f"2. Posting Entry A: {entry_a}")
    session.post(f"{BASE_URL}/api/health/log", headers=headers, json=entry_a)
    
    # Check Latest
    latest_a = session.get(f"{BASE_URL}/api/health/latest", headers=headers).json()
    print(f"   Latest after A: HR={latest_a.get('heart_rate')} (Expected 60)")
    
    # 3. Post Second Entry
    entry_b = {
        "heart_rate": "100",
        "bp_systolic": "140",
        "bp_diastolic": "90",
        "blood_sugar": "200"
    }
    print(f"3. Posting Entry B: {entry_b}")
    session.post(f"{BASE_URL}/api/health/log", headers=headers, json=entry_b)
    
    # Check Latest
    latest_b = session.get(f"{BASE_URL}/api/health/latest", headers=headers).json()
    print(f"   Latest after B: HR={latest_b.get('heart_rate')} (Expected 100)")
    
    if str(latest_b.get('heart_rate')) == "100":
        print("SUCCESS: Latest updated correctly.")
    else:
        print("FAILURE: Latest did NOT update.")

if __name__ == "__main__":
    verify_update_logic()
