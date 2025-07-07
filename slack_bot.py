import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from logger_config import get_logger, log_performance

load_dotenv()

# Get logger for this module
logger = get_logger("slack")


class SlackTweetBot:
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.channel = os.getenv("SLACK_CHANNEL")  # e.g., "#tweets" or "@username"
        self.pending_tweets = {}  # Store pending tweets with their message IDs

    @log_performance
    def send_tweet_for_approval(self, tweet_text, tweet_index=0):
        logger.info(f"channel: {self.channel}")
        """Send a tweet to Slack for approval with interactive buttons"""
        try:
            # Create the message blocks with interactive buttons
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🐦 Tweet Ready for Approval*\n\n_{tweet_text}_",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "✅ Approve & Tweet",
                            },
                            "style": "primary",
                            "action_id": f"approve_tweet_{tweet_index}",
                            "value": tweet_text,
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "✏️ Edit Tweet"},
                            "action_id": f"edit_tweet_{tweet_index}",
                            "value": tweet_text,
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "❌ Reject"},
                            "style": "danger",
                            "action_id": f"reject_tweet_{tweet_index}",
                            "value": tweet_text,
                        },
                    ],
                },
            ]

            # Send the message
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=f"Tweet approval needed: {tweet_text[:50]}...",
                blocks=blocks,
            )

            # Store the pending tweet
            message_ts = response["ts"]
            self.pending_tweets[message_ts] = {
                "text": tweet_text,
                "index": tweet_index,
                "status": "pending",
            }

            logger.info(f"✅ Tweet sent to Slack for approval: {tweet_text[:50]}...")
            return message_ts

        except SlackApiError as e:
            logger.error(f"❌ Error sending to Slack: {e}")
            return None

    @log_performance
    def send_edit_modal(self, trigger_id, tweet_text, tweet_index):
        """Send a modal for editing the tweet"""
        try:
            modal_view = {
                "type": "modal",
                "callback_id": f"edit_modal_{tweet_index}",
                "title": {"type": "plain_text", "text": "Edit Tweet"},
                "submit": {"type": "plain_text", "text": "Update & Approve"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "tweet_input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "tweet_text",
                            "multiline": True,
                            "initial_value": tweet_text,
                            "max_length": 280,
                        },
                        "label": {"type": "plain_text", "text": "Tweet Content"},
                    }
                ],
            }

            response = self.client.views_open(trigger_id=trigger_id, view=modal_view)
            logger.info(f"✏️ Edit modal opened for tweet: {tweet_text[:50]}...")
            return response

        except SlackApiError as e:
            logger.error(f"❌ Error opening edit modal: {e}")
            return None

    @log_performance
    def update_message_status(self, message_ts, status, new_text=None):
        """Update the original message to show the action taken and disable buttons"""
        try:
            if message_ts in self.pending_tweets:
                tweet_info = self.pending_tweets[message_ts]
                original_text = new_text if new_text else tweet_info["text"]

                # Create the updated blocks with disabled buttons
                if status == "approved":
                    status_text = "*✅ Tweet Approved & Posted*"
                    status_emoji = "✅"
                elif status == "rejected":
                    status_text = "*❌ Tweet Rejected*"
                    status_emoji = "❌"
                elif status == "edited":
                    status_text = "*✏️ Tweet Updated & Posted*"
                    status_emoji = "✏️"
                else:
                    status_text = f"*{status.title()}*"
                    status_emoji = "📝"

                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*🐦 Tweet Ready for Approval*\n\n_{original_text}_",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{status_text}",
                        },
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": f"{status_emoji} {status.title()}",
                                },
                                "style": "primary"
                                if status == "approved"
                                else "danger"
                                if status == "rejected"
                                else None,
                                "action_id": "disabled_button",
                                "value": "disabled",
                            }
                        ],
                    },
                ]

                # Update the message
                self.client.chat_update(
                    channel=self.channel,
                    ts=message_ts,
                    text=f"Tweet {status}",
                    blocks=blocks,
                )

                # Clean up
                del self.pending_tweets[message_ts]
                logger.info(f"📝 Message updated with status: {status}")

        except SlackApiError as e:
            logger.error(f"❌ Error updating message: {e}")

    def get_pending_tweet(self, message_ts):
        """Get pending tweet info by message timestamp"""
        return self.pending_tweets.get(message_ts)

    def send_simple_message(self, message):
        """Send a simple message to Slack"""
        try:
            response = self.client.chat_postMessage(channel=self.channel, text=message)
            logger.info(f"📤 Simple message sent: {message[:50]}...")
            return response
        except SlackApiError as e:
            logger.error(f"❌ Error sending message: {e}")
            return None
