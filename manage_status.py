import os
import sys
import json
import requests

# --- Configuration ---
COOKIE_STRING = os.getenv("REDDIT_COOKIE")
CSRF_TOKEN = os.getenv("REDDIT_CSRF_TOKEN")
SUBREDDIT_ID = "t5_4kth6i"
USER_AGENT = "GitHub-Actions-Status-Bot/1.0"
GRAPHQL_URL = "https://www.reddit.com/svc/shreddit/graphql"


# --- Helper Function ---
def update_community_status(payload, action_description):
    """Sends the API request to update the community status."""
    if not COOKIE_STRING or not CSRF_TOKEN:
        raise ValueError("Missing Reddit credentials in environment variables.")

    headers = {
        "cookie": COOKIE_STRING,
        "user-agent": USER_AGENT,
        "origin": "https://www.reddit.com",
        "referer": f"https://www.reddit.com/r/TextingTheory/",
        "content-type": "application/json",
    }
    print(f"Sending request to {action_description}...")
    try:
        response = requests.post(GRAPHQL_URL, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}\nResponse: {response.text}")
        print(f"\n✅ SUCCESS! {action_description} completed.")
    except requests.RequestException as e:
        print(f"\n❌ FAILED! An error occurred: {e}")
        sys.exit(1)


# --- Action-specific Functions ---
def set_monday_status():
    """Builds and sends the 'Megablunder Monday' status payload."""
    rich_text = {
        "document": [
            {
                "e": "par",
                "c": [{"e": "text", "t": "Megablunder Monday", "f": [[1, 0, 18]]}],
            },
            {
                "e": "par",
                "c": [
                    {"e": "u/", "t": "textingtheorybot", "l": False},
                    {
                        "e": "text",
                        "t": " has the ability to give Megablunder classifications",
                        "f": [[2, 25, 11]],
                    },
                ],
            },
        ]
    }
    payload = {
        "operation": "UpdateCommunityStatus",
        "variables": {
            "input": {
                "subredditId": SUBREDDIT_ID,
                "emojiId": "megablunder",
                "description": {"richText": json.dumps(rich_text)},
            }
        },
        "csrf_token": CSRF_TOKEN,
    }
    update_community_status(payload, "SET Monday status")


def set_saturday_status():
    """Builds and sends the 'Superbrilliant Saturday' status payload."""
    rich_text = {
        "document": [
            {
                "e": "par",
                "c": [{"e": "text", "t": "Superbrilliant Saturday", "f": [[1, 0, 24]]}],
            },
            {
                "e": "par",
                "c": [
                    {"e": "u/", "t": "textingtheorybot", "l": False},
                    {
                        "e": "text",
                        "t": " has the ability to give Superbrilliant classifications",
                        "f": [[2, 25, 14]],
                    },
                ],
            },
        ]
    }
    payload = {
        "operation": "UpdateCommunityStatus",
        "variables": {
            "input": {
                "subredditId": SUBREDDIT_ID,
                "emojiId": "superbrilliant",
                "description": {"richText": json.dumps(rich_text)},
            }
        },
        "csrf_token": CSRF_TOKEN,
    }
    update_community_status(payload, "SET Saturday status")


def clear_status():
    """Builds and sends the payload to clear the community status."""
    payload = {
        "operation": "UpdateCommunityStatus",
        "variables": {"input": {"subredditId": SUBREDDIT_ID, "emojiId": ""}},
        "csrf_token": CSRF_TOKEN,
    }
    update_community_status(payload, "CLEAR community status")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_status.py [set-monday|set-saturday|clear]")
        sys.exit(1)

    action = sys.argv[1].lower()
    print(f"Action triggered: '{action}'")

    if action == "set-monday":
        set_monday_status()
    elif action == "set-saturday":
        set_saturday_status()
    elif action == "clear":
        clear_status()
    else:
        print(f"Error: Unknown action '{action}'.")
        sys.exit(1)
