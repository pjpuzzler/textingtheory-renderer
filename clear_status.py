import os, requests, json

COOKIE_STRING = os.getenv("REDDIT_COOKIE")
CSRF_TOKEN = os.getenv("REDDIT_CSRF_TOKEN")
if not COOKIE_STRING or not CSRF_TOKEN: raise ValueError("Missing credentials.")

headers = {'cookie': COOKIE_STRING, 'user-agent': 'GitHub-Actions-Status-Bot/1.0', 'origin': 'https://www.reddit.com', 'referer': 'https://www.reddit.com/r/TextingTheory/', 'content-type': 'application/json'}
clear_payload = {"operation": "UpdateCommunityStatus", "variables": {"input": {"subredditId": "t5_4kth6i", "emojiId": ""}}, "csrf_token": CSRF_TOKEN}

print("Sending request to CLEAR community status...")
response = requests.post("https://www.reddit.com/svc/shreddit/graphql", headers=headers, json=clear_payload)
print(f"Status Code: {response.status_code}\nResponse: {response.text}")
response.raise_for_status()
print("\n✅ SUCCESS! Status was cleared.")