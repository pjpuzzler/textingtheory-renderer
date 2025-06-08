# Privacy Policy for TextingTheory Bot

Last updated: [Date]

This Privacy Policy describes how TextingTheory Bot ("Bot", "we", "us", or "our") collects, uses, and shares information in connection with your use of our Reddit bot services.

## Information We Collect

*   **Public Reddit Data:** We access publicly available Reddit post IDs, image URLs, and the content of images you post in subreddits where the Bot operates.
*   **Analysis Data:** The textual content extracted from images is sent to the Google Gemini API for analysis. The results of this analysis are processed by the Bot.
*   **GitHub Actions Data:** Analysis data is passed to a GitHub Actions workflow for image rendering.

## How We Use Information

*   To analyze the text conversations in your images.
*   To generate a stylized image of the conversation.
*   To post a review comment, including the rendered image and analysis, back to your Reddit post.
*   To temporarily store analysis data in Devvit's Key-Value store during processing.

## Data Sharing

*   With **Google Gemini API:** For text analysis. (See Google's Privacy Policy)
*   With **GitHub Actions:** For image rendering. (See GitHub's Privacy Policy)
*   **Publicly on Reddit:** Rendered images and analysis summaries are posted as public comments.

## Data Retention

We temporarily store analysis data in Devvit's KV Store and rendered images on an intermediate subreddit only for the duration needed to complete the processing. This data is deleted after the final comment is posted.

## Your Choices

You can delete your Reddit posts. If a post is deleted before the Bot processes it, the Bot will not be able to process that data.

## Contact Us

If you have any questions about this Privacy Policy, please contact u/pjpuzzler.