import requests
import base64
import json
import os

# Find any image in your project folder
IMAGE_PATH = r"C:\Users\HP\Desktop\sahaayika\sahaayika\static\index.html"

# Let's just test with a simple text prompt first (no image)
print("=== TEST 1: Basic text (no image) ===")
r = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gemma3n:latest",
        "prompt": "Say hello in one word.",
        "stream": False
    },
    timeout=60
)
print(f"Status: {r.status_code}")
data = r.json()
print(f"Response: {data.get('response', data)}")

# Now test with a tiny test image (1x1 white pixel PNG in base64)
print("\n=== TEST 2: Vision test (tiny image) ===")
TINY_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="

r2 = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gemma3n:latest",
        "prompt": "What color is this image? One word answer.",
        "images": [TINY_PNG],
        "stream": False
    },
    timeout=60
)
print(f"Status: {r2.status_code}")
data2 = r2.json()
print(f"Response: {json.dumps(data2, indent=2)[:300]}")