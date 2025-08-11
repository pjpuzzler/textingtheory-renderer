import os
import sys
import json
import praw
import requests

# --- Configuration ---
SUBREDDIT_ID = "t5_4kth6i"
USER_AGENT = "GitHub-Actions-Status-Bot/1.0"
GRAPHQL_URL = "https://www.reddit.com/svc/shreddit/graphql"


# --- PRAW Reddit Instance ---
def get_reddit_instance():
    """Initializes and returns an authenticated PRAW Reddit instance."""
    refresh_token = os.getenv("REDDIT_REFRESH_TOKEN")
    if not refresh_token:
        raise ValueError("Missing REDDIT_REFRESH_TOKEN in environment variables.")

    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_SECRET"),
        user_agent=USER_AGENT,
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        refresh_token=refresh_token,
    )
    return reddit


# --- Helper Function ---
def update_community_status(reddit, payload, action_description):
    """Sends the API request to update the community status."""
    # PRAW handles authentication, we just need the access token for the header
    access_token = reddit.auth.scopes() and reddit.auth.token_manager.access_token
    if not access_token:
        raise ConnectionError("Failed to get access token from PRAW.")

    # We need to manually get the csrf_token from the authenticated session
    csrf_token = reddit.auth.csrf_token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "user-agent": USER_AGENT,
        "origin": "https://www.reddit.com",
        "referer": "https://www.reddit.com/r/TextingTheory/",
        "content-type": "application/json",
        "x-csrf-token": csrf_token,
    }

    # The original payload uses a csrf_token in the body, which we add here
    payload_with_csrf = {**payload, "csrf_token": csrf_token}

    print(f"Sending request to {action_description}...")
    try:
        response = requests.post(GRAPHQL_URL, headers=headers, json=payload_with_csrf)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}\nResponse: {response.text}")
        print(f"\n✅ SUCCESS! {action_description} completed.")
    except requests.RequestException as e:
        print(f"\n❌ FAILED! An error occurred: {e}")
        if e.response:
            print(f"Response content: {e.response.text}")
        sys.exit(1)


# --- Action-specific Functions ---
def set_monday_status(reddit):
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
                        "t": " can give Megablunder classifications",
                        "f": [[2, 10, 11]],
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
    }
    update_community_status(reddit, payload, "SET Monday status")


def set_saturday_status(reddit):
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
                        "t": " can give Superbrilliant classifications",
                        "f": [[2, 10, 14]],
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
    }
    update_community_status(reddit, payload, "SET Saturday status")


def clear_status(reddit):
    """Builds and sends the payload to clear the community status."""
    payload = {
        "operation": "UpdateCommunityStatus",
        "variables": {"input": {"subredditId": SUBREDDIT_ID, "emojiId": ""}},
    }
    update_community_status(reddit, payload, "CLEAR community status")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_status.py [set-monday|set-saturday|clear]")
        sys.exit(1)

    try:
        reddit_instance = get_reddit_instance()
        print("Successfully authenticated with Reddit.")
    except (ValueError, praw.exceptions.PRAWException) as e:
        print(f"❌ FAILED to authenticate with Reddit: {e}")
        sys.exit(1)

    action = sys.argv[1].lower()
    print(f"Action triggered: '{action}'")

    if action == "set-monday":
        set_monday_status(reddit_instance)
    elif action == "set-saturday":
        set_saturday_status(reddit_instance)
    elif action == "clear":
        clear_status(reddit_instance)
    else:
        print(f"Error: Unknown action '{action}'.")
        sys.exit(1)
