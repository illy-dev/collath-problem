import requests

API_BASE_URL = "http://exampleapi:5000"
API_KEY = "xyz"

headers = {
    "X-API-KEY": API_KEY
}

print(requests.get(f"{API_BASE_URL}/get_results", headers=headers).json())
