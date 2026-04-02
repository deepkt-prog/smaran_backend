import urllib.request
import json

url = "http://127.0.0.1:8000/events/reverse-calc"
data = {
    "date": "1970-01-21",
    "latitude": 19.0760,
    "longitude": 72.8777
}

try:
    print(f"Sending POST to {url} with data: {data}")
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    jsondata = json.dumps(data).encode('utf-8')
    req.add_header('Content-Length', len(jsondata))
    
    response = urllib.request.urlopen(req, jsondata)
    
    print(f"Status Code: {response.getcode()}")
    print(f"Response Body: {response.read().decode('utf-8')}")
    
    if response.getcode() == 200:
        print("SUCCESS: Endpoint is working!")

except urllib.error.HTTPError as e:
    print(f"FAILURE: HTTP Error {e.code}")
    print(f"Error Body: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"EXCEPTION: Could not connect to server. Is it running? {e}")
