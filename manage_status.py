import os
import sys
import json
import praw
import prawcore

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
        # requestor_kwargs={'session': requests.Session()} # Optional: For advanced proxy/header use
    )
    print("Successfully initialized PRAW Reddit instance.")
    return reddit


# --- Helper Function ---
def update_community_status(reddit, payload, action_description):
    """Sends the API request using PRAW's authenticated session."""
    print(f"Sending request to {action_description} using PRAW's session...")
    try:
        # Let PRAW handle the entire request. It will automatically include
        # the necessary Authorization and x-csrf-token headers.
        # We pass the payload directly using the `json` parameter.
        response = reddit.post(GRAPHQL_URL, json=payload)

        # GraphQL responses don't typically raise HTTP errors for bad
        # requests, they return a 200 OK with an 'errors' key.
        if "errors" in response and response["errors"]:
            raise prawcore.exceptions.PrawcoreException(
                f"GraphQL returned errors: {response['errors']}"
            )

        print(f"Status: SUCCESS\nResponse: {response}")
        print(f"\n✅ SUCCESS! {action_description} completed.")

    except prawcore.exceptions.PrawcoreException as e:
        print(f"\n❌ FAILED! An error occurred during the PRAW request: {e}")
        sys.exit(1)


# --- Action-specific Functions ---
# Note: The 'csrf_token' is no longer needed in these payloads
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
