import requests

FLASK_API_URL = "http://192.168.59.114:31397/send"

for i in range(100):
    payload = {"message": f"Message number {i}"}
    try:
        response = requests.post(FLASK_API_URL, json=payload)
        if response.status_code == 200:
            print(f"[✓] Sent: {payload['message']}")
        else:
            print(f"[!] Failed: {response.status_code} → {response.text}")
    except Exception as e:
        print(f"[✗] Error sending message {i}: {e}")
