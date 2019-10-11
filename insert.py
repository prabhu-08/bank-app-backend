import requests
import time

url = "http://localhost:5000/api/add"

while(1):
    # Wait for 10 seconds
    response = requests.request("GET", url)
    print(response.text)
    time.sleep(10)