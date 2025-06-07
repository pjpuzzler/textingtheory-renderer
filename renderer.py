import json
import os
import sys
from imagekitio import ImageKit
from texting_theory import (
    render_conversation,
    TextMessage,
    Classification,
)


def main():
    # Expect two arguments: command and post_id
    if len(sys.argv) < 3:
        print("Usage: python renderer.py <command> <post_id>")
        sys.exit(1)

    command = sys.argv[1]
    post_id = sys.argv[2]
    # The image will be temporarily saved here before uploading
    local_output_path = f"{post_id}.png"

    # Get JSON payload from environment variable
    payload_json_string = os.environ.get("RENDERER_PAYLOAD")
    if not payload_json_string:
        print("Error: RENDERER_PAYLOAD environment variable not set.")
        sys.exit(1)
    payload = json.loads(payload_json_string)

    print(f"Executing command: {command} for post: {post_id}")

    try:
        if command == "render_and_upload":
            # --- 1. Render the image locally ---
            print(f"Rendering image to temporary file: {local_output_path}")
            messages = [
                TextMessage(
                    side=msg["side"],
                    content=msg["content"],
                    classification=Classification[msg["classification"].upper()],
                    unsent=msg.get("unsent", False),
                )
                for msg in payload.get("messages", [])
            ]
            render_conversation(
                messages,
                payload.get("color_data_left"),
                payload.get("color_data_right"),
                payload.get("background_hex"),
                local_output_path,
            )
            print("Image rendered successfully.")

            # --- 2. Initialize ImageKit client ---
            print("Initializing ImageKit...")
            imagekit = ImageKit(
                private_key=os.environ.get("IMAGEKIT_PRIVATE_KEY"),
                public_key=os.environ.get("IMAGEKIT_PUBLIC_KEY"),
                url_endpoint=os.environ.get("IMAGEKIT_URL_ENDPOINT"),
            )

            # --- 3. Upload the rendered file ---
            print(f"Uploading {local_output_path} to ImageKit...")
            # 'rb' is crucial: read the file in binary mode
            with open(local_output_path, "rb") as file:
                upload_info = imagekit.upload(
                    file=file,
                    file_name=f"{post_id}.png",  # Use the post ID as the public filename
                    options={
                        "folder": "game-reviews/",  # Optional: Keeps your ImageKit organized
                        "is_private_file": False,
                        "use_unique_file_name": False,  # Important: Ensures the filename is exactly post_id.png
                        "overwrite_file": True,  # In case of a re-run for the same post
                    },
                )
            print("Successfully uploaded to ImageKit.")
            print(f"Public URL: {upload_info.url}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        # Print a more detailed traceback for debugging in GitHub Actions
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        # --- 4. Clean up the local file ---
        if os.path.exists(local_output_path):
            os.remove(local_output_path)
            print(f"Cleaned up temporary file: {local_output_path}")


if __name__ == "__main__":
    main()
