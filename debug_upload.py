import requests
import time

base_url = "http://127.0.0.1:5000"

# Register first
r = requests.post(f"{base_url}/register", data={
    'username': 'testuser2',
    'email': 'test2@example.com',
    'password': 'password123'
})
print(f"Register: {r.status_code}")

# Session login
session = requests.Session()
login_r = session.post(f"{base_url}/login", data={
    'email': 'test2@example.com',
    'password': 'password123'
})
print(f"Login: {login_r.status_code}")

# Upload
files = {'file': ('test.txt', 'The Earth is a planet that orbits the sun. It is part of the solar system.')}
upload_r = session.post(f"{base_url}/api/upload", files=files)
print(f"Upload: {upload_r.status_code}, {upload_r.text}")

if upload_r.status_code == 200:
    data = upload_r.json()
    material_id = data['id']
    print(f"Processing material {material_id}...")
    proc_r = session.post(f"{base_url}/api/process/{material_id}")
    print(f"Process: {proc_r.status_code}, {proc_r.text}")
