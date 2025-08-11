import os
import sys
import json
import time
import random
from playwright.sync_api import sync_playwright, expect

# --- Configuration ---
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")


# --- Helper: Login Function ---
def login_to_reddit(page):
    """Logs into Reddit using the provided page object. Reusable for all actions."""
    if not REDDIT_USERNAME or not REDDIT_PASSWORD:
        raise ValueError(
            "Missing REDDIT_USERNAME or REDDIT_PASSWORD in environment variables."
        )

    print("Navigating to login page...")
    page.goto("https://www.reddit.com/login/")

    print("Entering username...")
    page.locator('input[name="username"]').fill(REDDIT_USERNAME)
    time.sleep(0.5)  # Brief pause

    print("Entering password...")
    page.locator('input[name="password"]').fill(REDDIT_PASSWORD)
    time.sleep(0.5)

    print("Clicking the 'Log In' button...")
    page.get_by_role("button", name="Log In").click()

    print("Waiting for login to complete...")
    expect(page.locator("#USER_DROPDOWN_ID")).to_be_visible(timeout=30000)
    print("✅ Login successful.")
    page.goto("https://www.reddit.com/r/TextingTheory")
    expect(page.get_by_role("heading", name="TextingTheory")).to_be_visible(
        timeout=15000
    )
    print("✅ Navigated to subreddit.")


# --- Action: Set Monday Status ---
def set_monday_status():
    """Sets the 'Megablunder Monday' status using full UI automation."""
    print("--- Starting: Set Monday Status ---")
    with sync_playwright() as p:
        # For local debugging, change to: browser = p.chromium.launch(headless=False, slow_mo=250)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            login_to_reddit(page)

            print("Opening community status modal...")
            page.get_by_role("button", name="Set a community status").click()

            print("Setting up Megablunder Monday...")
            page.locator("button.trigger-btn").click()
            page.get_by_role("listitem").filter(has_text="megablunder").click()

            page.locator("div.public-DraftEditor-content").click()
            time.sleep(0.5)

            # Type description using your sequence
            page.keyboard.press("Meta+B")
            page.keyboard.type("Megablunder Monday", delay=50)
            page.keyboard.press("Meta+B")
            page.keyboard.press("Enter")
            page.keyboard.type("u/textingtheorybot can give ", delay=50)
            page.keyboard.press("Meta+I")
            page.keyboard.type("Megablunder", delay=50)
            page.keyboard.press("Meta+I")
            page.keyboard.type(" classifications", delay=50)

            print("Applying status...")
            page.get_by_role("button", name="Apply").click()

            print("\n✅ SUCCESS! 'Set Monday Status' completed.")
            time.sleep(3)  # Pause to ensure completion
        except Exception as e:
            page.screenshot(path="debug_screenshot.png", full_page=True)
            raise e  # Re-raise the exception after screenshot
        finally:
            browser.close()


# --- Action: Set Saturday Status ---
def set_saturday_status():
    """Sets the 'Superbrilliant Saturday' status using full UI automation."""
    print("--- Starting: Set Saturday Status ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        try:
            login_to_reddit(page)

            print("Opening community status modal...")
            page.get_by_role("button", name="Set a community status").click()

            print("Setting up Superbrilliant Saturday...")
            page.locator("button.trigger-btn").click()
            page.get_by_role("listitem").filter(has_text="superbrilliant").click()

            page.locator("div.public-DraftEditor-content").click()
            time.sleep(0.5)

            page.keyboard.press("Meta+B")
            page.keyboard.type("Superbrilliant Saturday", delay=50)
            page.keyboard.press("Meta+B")
            page.keyboard.press("Enter")
            page.keyboard.type("u/textingtheorybot can give ", delay=50)
            page.keyboard.press("Meta+I")
            page.keyboard.type("Superbrilliant", delay=50)
            page.keyboard.press("Meta+I")
            page.keyboard.type(" classifications", delay=50)

            print("Applying status...")
            page.get_by_role("button", name="Apply").click()

            print("\n✅ SUCCESS! 'Set Saturday Status' completed.")
            time.sleep(3)
        except Exception as e:
            page.screenshot(path="debug_screenshot.png", full_page=True)
            raise e
        finally:
            browser.close()


# --- Action: Clear Status ---
def clear_status():
    """Clears the community status using full UI automation."""
    print("--- Starting: Clear Status ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            login_to_reddit(page)

            print("Opening community status modal...")
            page.get_by_role("button", name="Set a community status").click()

            print("Clearing community status...")
            page.get_by_role("button", name="Clear Status").click()

            print("Applying changes...")
            page.get_by_role("button", name="Apply").click()

            print("\n✅ SUCCESS! 'Clear Status' completed.")
            time.sleep(3)
        except Exception as e:
            page.screenshot(path="debug_screenshot.png", full_page=True)
            raise e
        finally:
            browser.close()


# --- Main Execution Block ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_status.py [set-monday|set-saturday|clear]")
        sys.exit(1)

    action = sys.argv[1].lower()
    print(f"Action triggered: '{action}'")

    try:
        if action == "set-monday":
            set_monday_status()
        elif action == "set-saturday":
            set_saturday_status()
        elif action == "clear":
            clear_status()
        else:
            print(f"Error: Unknown action '{action}'.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ A critical error occurred in the main execution block: {e}")
        print(
            "   Check the debug screenshot in the GitHub Actions artifacts for details."
        )
        sys.exit(1)


# # --- Action-specific Functions (Unchanged) ---
# def set_monday_status():
#     rich_text = {
#         "document": [
#             {
#                 "e": "par",
#                 "c": [{"e": "text", "t": "Megablunder Monday", "f": [[1, 0, 18]]}],
#             },
#             {
#                 "e": "par",
#                 "c": [
#                     {"e": "u/", "t": "textingtheorybot", "l": False},
#                     {
#                         "e": "text",
#                         "t": " can give Megablunder classifications",
#                         "f": [[2, 10, 11]],
#                     },
#                 ],
#             },
#         ]
#     }
#     variables = {
#         "input": {
#             "subredditId": SUBREDDIT_ID,
#             "emojiId": "megablunder",
#             "description": {"richText": json.dumps(rich_text)},
#         }
#     }
#     payload = {"operation": "UpdateCommunityStatus", "variables": variables}
#     update_community_status(payload, "SET Monday status")


# def set_saturday_status():
#     rich_text = {
#         "document": [
#             {
#                 "e": "par",
#                 "c": [{"e": "text", "t": "Superbrilliant Saturday", "f": [[1, 0, 24]]}],
#             },
#             {
#                 "e": "par",
#                 "c": [
#                     {"e": "u/", "t": "textingtheorybot", "l": False},
#                     {
#                         "e": "text",
#                         "t": " can give Superbrilliant classifications",
#                         "f": [[2, 10, 14]],
#                     },
#                 ],
#             },
#         ]
#     }
#     variables = {
#         "input": {
#             "subredditId": SUBREDDIT_ID,
#             "emojiId": "superbrilliant",
#             "description": {"richText": json.dumps(rich_text)},
#         }
#     }
#     payload = {"operation": "UpdateCommunityStatus", "variables": variables}
#     update_community_status(payload, "SET Saturday status")


# def clear_status():
#     variables = {"input": {"subredditId": SUBREDDIT_ID, "emojiId": ""}}
#     payload = {"operation": "UpdateCommunityStatus", "variables": variables}
#     update_community_status(payload, "CLEAR community status")
