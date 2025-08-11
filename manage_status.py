import os
import sys
import json
import praw
import prawcore
import requests  # Use the reliable requests library for the API call

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
    print(f"Sending request to {action_description}...")
    try:
        # Step 1: Force PRAW to authenticate and fetch an access token.
        # This is the "prime the pump" step. It requires the 'identity' scope.
        print("Priming authentication to fetch access token...")
        user = reddit.user.me()
        print(f"Authentication primed for user: u/{user.name}")

        # Step 2: Now that PRAW has authenticated, the token is guaranteed to exist.
        access_token = reddit._core._authorizer.access_token
        if not access_token:
            raise ValueError("Failed to retrieve access token after priming.")
        print("Successfully retrieved access token.")

        # Step 3: Build the headers for the manual request.
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
        }

        # Step 4: Make the API call using 'requests'.
        print(f"Payload being sent:\n{json.dumps(payload, indent=2)}")
        response = requests.post(GRAPHQL_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for 4xx or 5xx status codes

        response_json = response.json()
        if "errors" in response_json and response_json["errors"]:
            raise Exception(f"GraphQL API returned errors: {response_json['errors']}")

        print(f"Status: SUCCESS\nResponse: {json.dumps(response_json, indent=2)}")
        print(f"\n✅ SUCCESS! {action_description} completed.")

    except prawcore.exceptions.Forbidden as e:
        print("\n❌ FAILED! A 403 Forbidden error occurred.")
        print(
            "   This likely means your refresh token does not have the required 'identity' scope."
        )
        print(
            "   Please generate a new token with both 'modconfig' and 'identity' scopes."
        )
        sys.exit(1)
    except requests.RequestException as e:
        print(f"\n❌ FAILED! A network error occurred: {e}")
        if e.response is not None:
            print(f"Server responded with {e.response.status_code}:\n{e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FAILED! An unexpected error occurred: {e}")
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


# --- Main Execution Block ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_status.py [set-monday|set-saturday|clear]")
        sys.exit(1)

    try:
        reddit_instance = get_reddit_instance()
    except Exception as e:
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
