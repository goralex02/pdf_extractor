import requests

url = "http://127.0.0.1:8000/ai-tools/extract-text/"
file_path = "./data/kids.png"

with open(file_path, "rb") as file:
    response = requests.post(url, files={"file": file})

print(response.json())
