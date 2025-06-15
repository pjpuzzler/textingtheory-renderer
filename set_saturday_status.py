import os, requests, json

COOKIE_STRING = os.getenv("REDDIT_COOKIE")
CSRF_TOKEN = os.getenv("REDDIT_CSRF_TOKEN")
if not COOKIE_STRING or not CSRF_TOKEN: raise ValueError("Missing credentials.")

headers = {'cookie': COOKIE_STRING, 'user-agent': 'GitHub-Actions-Status-Bot/1.0', 'origin': 'https://www.reddit.com', 'referer': 'https://www.reddit.com/r/TextingTheory/', 'content-type': 'application/json'}
rich_text_payload = {"document": [{"e": "par", "c": [{"e": "text", "t": "Superbrilliant Saturdays", "f": [[1, 0, 24]]}]}, {"e": "par", "c": [{"e": "u/", "t": "textingtheorybot", "l": False}, {"e": "text", "t": " has the ability to give Superbrilliant classifications", "f": [[2, 25, 14]]}]}]}
payload = {"operation": "UpdateCommunityStatus", "variables": {"input": {"subredditId": "t5_4kth6i", "emojiId": "superbrilliant", "description": {"richText": json.dumps(rich_text_payload)}}}, "csrf_token": CSRF_TOKEN}

print("Sending request to SET Saturday status...")
response = requests.post("https://www.reddit.com/svc/shreddit/graphql", headers=headers, json=payload)
print(f"Status Code: {response.status_code}\nResponse: {response.text}")
response.raise_for_status()
print("\n✅ SUCCESS! Saturday status was set.")