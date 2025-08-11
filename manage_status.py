import os
import sys
import json
import praw
import prawcore
import requests  # We are using the requests library again for direct control

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
        refresh_token=refresh_token,
    )
    print("Successfully initialized PRAW Reddit instance.")
    return reddit


# --- Helper Function ---
def update_community_status(reddit, payload, action_description):
    """
    Uses PRAW to get an access token, then sends the request manually
    using the 'requests' library for maximum reliability.
    """
    print(f"Sending request to {action_description} via requests library...")
    try:
        # Step 1: Get the access token from the authenticated PRAW instance.
        # This is the only thing we will use PRAW for in this function.
        access_token = reddit._core._authorizer.access_token
        if not access_token:
            raise ValueError("Could not get access token from PRAW.")

        # Step 2: Build the headers for the manual request.
        # OAuth (Bearer) authentication does not require a CSRF token in the headers.
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "origin": "https://www.reddit.com",  # Including these helps mimic a browser
            "referer": "https://www.reddit.com/",
        }

        # Step 3: Make the API call using 'requests'.
        response = requests.post(GRAPHQL_URL, headers=headers, json=payload)
        response.raise_for_status()  # This will raise an error for 4xx or 5xx responses

        response_json = response.json()
        if "errors" in response_json and response_json["errors"]:
            raise Exception(f"GraphQL returned errors: {response_json['errors']}")

        print(f"Status: SUCCESS\nResponse: {json.dumps(response_json, indent=2)}")
        print(f"\n✅ SUCCESS! {action_description} completed.")

    except requests.RequestException as e:
        print(f"\n❌ FAILED! A network error occurred: {e}")
        if e.response is not None:
            print(f"Server responded with {e.response.status_code}:\n{e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FAILED! A general error occurred: {e}")
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
        # NOTE: A CSRF token is not needed in the body when using Bearer auth.
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


# --- Main Execution Block ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_status.py [set-monday|set-saturday|clear]")
        sys.exit(1)

    try:
        # A refresh token with just 'modconfig' scope is sufficient.
        reddit_instance = get_reddit_instance()
    except (ValueError, prawcore.exceptions.PrawcoreException) as e:
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
