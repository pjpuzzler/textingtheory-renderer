import os
import sys
import json
from playwright.sync_api import (
    sync_playwright,
    expect,
    TimeoutError as PlaywrightTimeoutError,
)

# --- Configuration ---
SUBREDDIT_ID = "t5_4kth6i"
USER_AGENT = "GitHub-Actions-Status-Bot/1.0"
GRAPHQL_URL = "https://www.reddit.com/svc/shreddit/graphql"
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")


# --- Helper Function ---
def update_community_status(payload, action_description):
    """
    Launches a browser, logs into Reddit, and sends the authenticated
    GraphQL request to update the community status.
    """
    if not REDDIT_USERNAME or not REDDIT_PASSWORD:
        raise ValueError(
            "Missing REDDIT_USERNAME or REDDIT_PASSWORD in environment variables."
        )

    print(f"Starting browser automation for: {action_description}")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
            # Use the browser's context to make requests. This shares cookies.
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()

            # --- Login ---
            print("Navigating to login page...")
            page.goto("https://www.reddit.com/login/")

            # Reddit's login is inside an iframe
            login_frame = page.frame_locator(
                "iframe[src^='https://www.reddit.com/login']"
            )

            print("Entering username...")
            login_frame.locator("#login-username").fill(REDDIT_USERNAME)

            print("Entering password...")
            login_frame.locator("#login-password").fill(REDDIT_PASSWORD)

            login_frame.locator("button[type='submit']").click()

            # Wait for successful login by looking for the user profile icon
            print("Waiting for login to complete...")
            expect(page.locator("#USER_DROPDOWN_ID")).to_be_visible(timeout=30000)
            print("✅ Login successful.")

            # --- API Call ---
            # Use the authenticated context to make the API call.
            # Playwright automatically includes all necessary cookies.
            print("Sending GraphQL request...")
            api_request_context = page.request
            response = api_request_context.post(GRAPHQL_URL, json=payload)

            if not response.ok:
                raise Exception(
                    f"API call failed with status {response.status}: {response.text()}"
                )

            response_json = response.json()
            if "errors" in response_json and response_json["errors"]:
                raise Exception(
                    f"GraphQL API returned errors: {response_json['errors']}"
                )

            print(f"Status: SUCCESS\nResponse: {json.dumps(response_json, indent=2)}")
            print(f"\n✅ SUCCESS! {action_description} completed.")

        except PlaywrightTimeoutError:
            print(
                "\n❌ FAILED! A timeout occurred. This might be due to a failed login or a change in Reddit's page layout."
            )
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ FAILED! An unexpected error occurred: {e}")
            sys.exit(1)
        finally:
            if "browser" in locals():
                browser.close()


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
                        "t": " can give Megablunder classifications",
                        "f": [[2, 10, 11]],
                    },
                ],
            },
        ]
    }
    variables = {
        "input": {
            "subredditId": SUBREDDIT_ID,
            "emojiId": "megablunder",
            "description": {"richText": json.dumps(rich_text)},
        }
    }
    payload = {"operation": "UpdateCommunityStatus", "variables": variables}
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
                        "t": " can give Superbrilliant classifications",
                        "f": [[2, 10, 14]],
                    },
                ],
            },
        ]
    }
    variables = {
        "input": {
            "subredditId": SUBREDDIT_ID,
            "emojiId": "superbrilliant",
            "description": {"richText": json.dumps(rich_text)},
        }
    }
    payload = {"operation": "UpdateCommunityStatus", "variables": variables}
    update_community_status(payload, "SET Saturday status")


def clear_status():
    """Builds and sends the payload to clear the community status."""
    variables = {"input": {"subredditId": SUBREDDIT_ID, "emojiId": ""}}
    payload = {"operation": "UpdateCommunityStatus", "variables": variables}
    update_community_status(payload, "CLEAR community status")


# --- Main Execution Block ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_status.py [set-monday|set-saturday|clear]")
        sys.exit(1)

    action = sys.argv[1].lower()

    # Note: No need for a separate reddit_instance anymore
    if action == "set-monday":
        set_monday_status()
    elif action == "set-saturday":
        set_saturday_status()
    elif action == "clear":
        clear_status()
    else:
        print(f"Error: Unknown action '{action}'.")
        sys.exit(1)
