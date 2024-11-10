import requests

# URL of the endpoint
url = 'http://127.0.0.1:5000/gooPaths/hi'

# Send a POST request
response = requests.post(url)

# Print the response
print("Status Code goo:", response.status_code)
print("Response JSON:", response.json())



# URL of the endpoint for testing `/LocalPaths`
url_localpaths = 'http://127.0.0.1:5000/LocalPaths'

# Example JSON payload with file paths
payload = {
    "filePaths": ["/Users/kanishk/Downloads"]
}

# Send a POST request with the JSON payload
response = requests.post(url_localpaths, json=payload)

# Print the response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())



