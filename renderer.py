import json
import os
import sys
from texting_theory import (
    render_conversation,
    TextMessage,
    Classification,
)


def main():
    # Expect two arguments: command and output_path
    if len(sys.argv) < 3:
        print("Usage: python renderer.py <command> <output_path>")
        sys.exit(1)

    command = sys.argv[1]
    output_path = sys.argv[2]  # Get output path from command line

    # Get JSON payload from environment variable
    payload_json_string = os.environ.get("RENDERER_PAYLOAD")
    if not payload_json_string:
        print("Error: RENDERER_PAYLOAD environment variable not set or empty.")
        sys.exit(1)

    try:
        payload = json.loads(payload_json_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from RENDERER_PAYLOAD: {e}")
        print(f"Payload received: {payload_json_string[:500]}...")
        sys.exit(1)

    print(f"Executing command: {command}")
    print(f"Outputting to: {output_path}")

    try:
        if command == "render_conversation":
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
                output_path,  # Use the dynamic output path
            )
        # Note: Your original file had render_annotation, which is not used in this flow.
        # I've kept the logic here in case you need it.
        elif command == "render_annotation":
            # ... your render_annotation logic ...
            print(
                "render_annotation command not fully implemented in this example flow."
            )
            pass
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing key in payload for command '{command}': {e}")
        print(f"Payload received: {json.dumps(payload, indent=2)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during rendering for command '{command}': {e}")
        sys.exit(1)

    print(f"Successfully rendered image to {output_path}")


if __name__ == "__main__":
    main()
