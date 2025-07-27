import httpx

api_key = "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"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "mistralai/mistral-7b-instruct:free",
    "messages": [
        {"role": "user", "content": "سلام! حالت چطوره؟"}
    ]
}

try:
    response = httpx.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    print("Status code:", response.status_code)
    print("Response text:", response.text)
except Exception as e:
    print("Error:", e)