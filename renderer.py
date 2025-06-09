import enum
import json
import os
import sys
import praw  # For posting to Reddit
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont, ImageColor
from pilmoji import Pilmoji
from pilmoji.source import AppleEmojiSource  # Or your preferred emoji source


# --- Rendering Logic (previously texting_theory.py) ---
class Classification(enum.Enum):
    ABANDON = "abandon"
    BEST = "best"
    BLUNDER = "blunder"
    BOOK = "book"
    BRILLIANT = "brilliant"
    CHECKMATED = "checkmated"
    DRAW = "draw"
    EXCELLENT = "excellent"
    FORCED = "forced"
    GOOD = "good"
    GREAT = "great"
    INACCURACY = "inaccuracy"
    INTERESTING = "interesting"
    MEGABLUNDER = "megablunder"
    MISS = "miss"
    MISTAKE = "mistake"
    RESIGN = "resign"
    TIMEOUT = "timeout"
    WINNER = "winner"

    def png_path(self, color: str) -> str:
        base_path = os.path.join(os.path.dirname(__file__), "badges")
        if not os.path.exists(base_path):
            base_path = "badges"

        match self:
            case Classification.CHECKMATED:
                return os.path.join(base_path, f"{self.value}_{color}.png")
            case _:
                return os.path.join(base_path, f"{self.value}.png")


@dataclass
class TextMessage:
    side: str
    content: str
    classification: Classification
    unsent: bool = False
    username: str = None
    avatar_url: str = None


def wrap_text(text, draw, font, max_width):
    def ellipsize(word):
        ellipsis = "..."
        ellipsis_width = draw.textbbox((0, 0), ellipsis, font=font)[2]
        if ellipsis_width > max_width:
            return ""
        truncated = ""
        for char in word:
            test_word = truncated + char + ellipsis
            test_width = draw.textbbox((0, 0), test_word, font=font)[2]
            if test_width <= max_width:
                truncated += char
            else:
                break
        return truncated + ellipsis

    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        line = ""
        for w in words:
            w_width = draw.textbbox((0, 0), w, font=font)[2]
            if w_width > max_width:
                w = ellipsize(w)
            test_line = (line + " " + w).strip()
            test_box = draw.textbbox((0, 0), test_line, font=font)
            if test_box[2] - test_box[0] <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
    return "\n".join(lines)


def render_conversation(
    messages: list[TextMessage],
    color_data_left,
    color_data_right,
    background_hex,
    output_path="output.png",
):
    base_w = 320
    scale = 4
    img_w = base_w * scale

    font = ImageFont.truetype("fonts/Arial.ttf", 14 * scale)
    pad = 12 * scale
    line_sp = 6 * scale
    radius = 16 * scale
    badge_sz = 36 * scale
    badge_margin = 42 * scale

    max_bubble_w = int(img_w * 0.75)

    dummy = Image.new("RGB", (1, 1))
    dd = ImageDraw.Draw(dummy)
    wrapped, dims = [], []
    with Pilmoji(dummy, source=AppleEmojiSource) as pilmoji:
        for m in messages:
            txt = wrap_text(m.content, dd, font, max_bubble_w - 2 * pad)
            wrapped.append(txt)
            w, h = pilmoji.getsize(txt, font=font, spacing=line_sp)
            dims.append((w, h))

    total_h = pad
    for i, (w, h) in enumerate(dims):
        bh = h + 2 * pad
        total_h += bh
        if i < len(dims) - 1:
            next_spacing = (
                pad // 5
                if messages[i + 1].side == messages[i].side
                else int(pad * 0.67)
            )
            total_h += next_spacing
    total_h += pad

    bg_rgba = ImageColor.getcolor(background_hex, "RGBA")
    img_bg = Image.new("RGBA", (img_w, total_h), bg_rgba)
    bubble_layer = Image.new("RGBA", (img_w, total_h), (0, 0, 0, 0))
    text_drawings = []
    y = pad
    text_offset = int(0 * scale)

    for i, (m, txt, (w, h)) in enumerate(zip(messages, wrapped, dims)):
        bw = w + 2 * pad
        bh = h + 2 * pad
        if m.side == "left":
            x0 = pad
            badge_x = x0 + bw - badge_sz + badge_margin
            bubble_color = color_data_left["bubble_hex"]
            text_hex = color_data_left["text_hex"]
        else:
            x0 = img_w - bw - pad
            badge_x = x0 - badge_margin
            bubble_color = color_data_right["bubble_hex"]
            text_hex = color_data_right["text_hex"]

        x1, y1 = x0 + bw, y + bh
        bubble_draw = ImageDraw.Draw(bubble_layer)

        if m.unsent:
            # ... (unsent bubble drawing logic - assuming it's correct) ...
            if m.side == "left":
                center_big = (x0 + 5 * scale, y1 - 5 * scale)
                big_rad = 7 * scale
                bbox_big = (
                    center_big[0] - big_rad,
                    center_big[1] - big_rad,
                    center_big[0] + big_rad,
                    center_big[1] + big_rad,
                )
                bubble_draw.ellipse(bbox_big, fill=bubble_color)

                center_small = (x0 - 3 * scale, y1 + 3 * scale)
                small_rad = 3 * scale
                bbox_small = (
                    center_small[0] - small_rad,
                    center_small[1] - small_rad,
                    center_small[0] + small_rad,
                    center_small[1] + small_rad,
                )
                bubble_draw.ellipse(bbox_small, fill=bubble_color)
            else:
                center_big = (x1 - 5 * scale, y1 - 5 * scale)
                big_rad = 7 * scale
                bbox_big = (
                    center_big[0] - big_rad,
                    center_big[1] - big_rad,
                    center_big[0] + big_rad,
                    center_big[1] + big_rad,
                )
                bubble_draw.ellipse(bbox_big, fill=bubble_color)

                center_small = (x1 + 3 * scale, y1 + 3 * scale)
                small_rad = 3 * scale
                bbox_small = (
                    center_small[0] - small_rad,
                    center_small[1] - small_rad,
                    center_small[0] + small_rad,
                    center_small[1] + small_rad,
                )
                bubble_draw.ellipse(bbox_small, fill=bubble_color)
        else:
            if m.side == "left":
                tail = [
                    (x0 + 2 * scale, y + bh - 16 * scale),
                    (x0 - 6 * scale, y + bh),
                    (x0 + 10 * scale, y + bh - 4 * scale),
                ]
                bubble_draw.polygon(tail, fill=bubble_color)
            else:
                tail = [
                    (x1 - 2 * scale, y + bh - 16 * scale),
                    (x1 + 6 * scale, y + bh),
                    (x1 - 10 * scale, y + bh - 4 * scale),
                ]
                bubble_draw.polygon(tail, fill=bubble_color)
        bubble_draw.rounded_rectangle((x0, y, x1, y1), radius, fill=bubble_color)

        text_drawings.append(
            (
                (x0 + pad, y + pad - text_offset),
                txt,
                font,
                text_hex,
                line_sp,
                -10 if m.side == "left" else 10,
            )
        )

        badge_path = m.classification.png_path(
            "white" if m.side == "right" else "black"
        )
        try:
            badge = Image.open(badge_path).resize((badge_sz, badge_sz))
            if badge.mode != "RGBA":
                badge = badge.convert("RGBA")
            by = y + (bh - badge_sz) // 2
            img_bg.paste(badge, (badge_x, by), badge)
        except FileNotFoundError:
            print(f"Warning: Badge file not found at {badge_path}. Skipping badge.")

        spacing = (
            pad // 5
            if (i < len(messages) - 1 and messages[i + 1].side == m.side)
            else int(pad * 0.67)
        )
        y += bh + spacing

    composite_img = Image.alpha_composite(img_bg, bubble_layer)
    with Pilmoji(composite_img, source=AppleEmojiSource) as pilmoji:
        for pos, t, f, col, sp, offs in text_drawings:
            pilmoji.text(
                pos,
                t,
                font=f,
                fill=col,
                spacing=sp,
                emoji_scale_factor=1.3,
                emoji_position_offset=(offs, 0),
            )

    final_img = composite_img.convert("RGB")
    final_img.save(output_path)


# --- CLI Main Function ---
def main():
    # Expected arguments: python renderer.py <command> <reply_to_id> <target_subreddit> <type>
    if len(sys.argv) < 5:
        print(
            "Usage: python renderer.py render_and_post_intermediate <reply_to_id> <target_subreddit> <type>"
        )
        sys.exit(1)

    command = sys.argv[1]
    reply_to_id = sys.argv[2]
    target_subreddit_name = sys.argv[3]
    job_type = sys.argv[4]

    # Read payload from environment variable
    payload_json_string = os.environ.get("RENDER_PAYLOAD_JSON")
    if not payload_json_string:
        print("Error: RENDER_PAYLOAD_JSON environment variable not set or empty.")
        sys.exit(1)

    try:
        payload = json.loads(payload_json_string)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from RENDER_PAYLOAD_JSON environment variable: {e}")
        print(
            f"Received string: {payload_json_string[:500]}..."
        )  # Print first 500 chars for debugging
        sys.exit(1)

    local_output_path = f"{reply_to_id}_rendered.png"
    if job_type == "analysis":
        intermediate_post_title = f"render_result_analysis:{reply_to_id}"
    elif job_type == "annotate":
        intermediate_post_title = f"render_result_annotate:{reply_to_id}"
    else:
        print("Unknown job type")
        sys.exit(1)

    print(
        f"Executing command: {command} for replying to: {reply_to_id} on subreddit: {target_subreddit_name}"
    )

    if command == "render_and_post_intermediate":
        print(f"Rendering image to temporary file: {local_output_path}")

        parsed_messages = []
        for msg_data in payload.get("messages", []):
            try:
                classification_str = msg_data.get("classification")
                if not classification_str:
                    print(
                        f"Warning: Message data missing classification: {msg_data}. Skipping message."
                    )
                    continue
                classification_enum = Classification(classification_str.lower())
                parsed_messages.append(
                    TextMessage(
                        side=msg_data["side"],
                        content=msg_data["content"],
                        classification=classification_enum,
                        unsent=msg_data.get("unsent", False),
                    )
                )
            except ValueError:
                print(
                    f"Warning: Unknown classification '{msg_data.get('classification')}' received. Skipping message."
                )
                continue
            except KeyError as ke:
                print(
                    f"Warning: Message data missing key {ke}: {msg_data}. Skipping message."
                )
                continue

        # Extract color data from the standard Analysis format
        color_block = payload.get("color", {})
        color_data_left = color_block.get("left")
        color_data_right = color_block.get("right")
        background_hex = color_block.get("background_hex")

        render_conversation(
            parsed_messages,
            color_data_left,
            color_data_right,
            background_hex,
            local_output_path,
        )
        print("Image rendered successfully.")

        print(f"Initializing PRAW to post to r/{target_subreddit_name}...")
        try:
            reddit = praw.Reddit(
                client_id=os.environ["REDDIT_CLIENT_ID"],
                client_secret=os.environ["REDDIT_CLIENT_SECRET"],
                user_agent=os.environ["REDDIT_USER_AGENT"],
                username=os.environ["REDDIT_USERNAME"],
                password=os.environ["REDDIT_PASSWORD"],
                check_for_async=False,
            )
            reddit.user.me()
            print("PRAW authenticated successfully.")
        except Exception as e:
            print(f"Error initializing or authenticating PRAW: {e}")
            if os.path.exists(local_output_path):
                os.remove(local_output_path)
            sys.exit(1)

        # Prepare minimized analysis for post body (strip message content, keep standard Analysis format)
        # comment_analysis = dict(payload)
        # if "messages" in comment_analysis:
        #     comment_analysis["messages"] = [
        #         {**msg, "content": ""} for msg in comment_analysis["messages"]
        #     ]
        comment_json = json.dumps(payload, separators=(",", ":"))

        try:
            subreddit = reddit.subreddit(target_subreddit_name)
            print(
                f"Submitting image {local_output_path} to r/{target_subreddit_name} with title '{intermediate_post_title}'..."
            )
            submission = subreddit.submit_image(
                title=intermediate_post_title,
                image_path=local_output_path,
                nsfw=False,
                spoiler=False,
            )
            print(
                f"Successfully posted intermediate image to Reddit: {submission.shortlink} (ID: {submission.id})"
            )
            # Post minimized analysis as a comment
            submission.reply(comment_json)
            print(
                "Posted minimized analysis as a comment on the intermediate image post."
            )
        except Exception as e:
            print(f"An error occurred during Reddit submission: {e}")
            import traceback

            traceback.print_exc()
            if os.path.exists(local_output_path):
                os.remove(local_output_path)
            sys.exit(1)
        finally:  # Ensure cleanup even if submission succeeds or fails (after initial error handling)
            if os.path.exists(local_output_path):
                try:
                    os.remove(local_output_path)
                    print(f"Cleaned up temporary file: {local_output_path}")
                except Exception as e_remove:
                    print(
                        f"Error cleaning up temporary file {local_output_path}: {e_remove}"
                    )

    else:
        print(f"Unknown command: {command}")
        # No local_output_path would have been created if command is unknown from the start
        sys.exit(1)

    # Note: Cleanup is now handled within the try/finally block of the command processing.
    # If the script exits earlier (e.g., bad args, payload error), local_output_path might not exist or be created.


if __name__ == "__main__":
    main()
