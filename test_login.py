"""Script temporal para probar el login."""
import urllib.request
import json

url = "http://127.0.0.1:8000/api/auth/login"
data = json.dumps({"email": "admin@profematch.com", "password": "admin123"}).encode("utf-8")

req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

try:
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        print(f"STATUS: {resp.status}")
        print(f"BODY: {body[:600]}")
except urllib.error.HTTPError as e:
    print(f"ERROR STATUS: {e.code}")
    print(f"ERROR BODY: {e.read().decode('utf-8')[:600]}")
except Exception as e:
    print(f"CONNECTION ERROR: {e}")
