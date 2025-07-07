import os
import json
import tweepy
import hmac
import hashlib
import time
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from dotenv import load_dotenv
from logger_config import get_logger, log_performance

load_dotenv()

app = Flask(__name__)

# Get logger for this module
logger = get_logger("webhook")

# Initialize clients
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
twitter_client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

# Global reference to the slack bot instance
slack_bot = None


def set_slack_bot(bot_instance):
    global slack_bot
    slack_bot = bot_instance


def verify_slack_request(request_body, timestamp, signature):
    """Verify that the request came from Slack"""
    try:
        # Skip verification in development if no signing secret is set
        signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        if not signing_secret:
            logger.warning(
                "⚠️ SLACK_SIGNING_SECRET not set - skipping request verification"
            )
            return True

        # Check if the timestamp is too old (replay attack protection)
        if abs(time.time() - int(timestamp)) > 60 * 5:  # 5 minutes
            logger.warning("⚠️ Request timestamp is too old")
            return False

        # Create the signature
        sig_basestring = f"v0:{timestamp}:{request_body}"
        computed_signature = (
            "v0="
            + hmac.new(
                signing_secret.encode("utf-8"),
                sig_basestring.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
        )

        # Compare signatures
        if hmac.compare_digest(computed_signature, signature):
            return True
        else:
            logger.warning("⚠️ Request signature verification failed")
            return False

    except Exception as e:
        logger.error(f"❌ Error verifying Slack request: {e}")
        return False


@log_performance
def remove_tweet_from_json(tweet_text):
    """Remove a tweet from the generated_tweets.json file"""
    try:
        with open("generated_tweets.json", "r+") as f:
            tweets = json.load(f)
            original_count = len(tweets)
            # Remove the tweet if it exists
            tweets = [tweet for tweet in tweets if tweet.get("tweet", "") != tweet_text]
            new_count = len(tweets)
            f.seek(0)
            json.dump(tweets, f, indent=2)
            f.truncate()

        if original_count > new_count:
            logger.info(f"✅ Tweet removed from queue: {tweet_text[:50]}...")
        else:
            logger.warning(f"⚠️ Tweet not found in queue: {tweet_text[:50]}...")

    except Exception as e:
        logger.error(f"❌ Error removing tweet: {e}")


@log_performance
def post_tweet_to_twitter(tweet_text):
    """Post a tweet to Twitter"""
    try:
        response = twitter_client.create_tweet(text=tweet_text)
        logger.info(f"✅ Tweet posted to Twitter: {tweet_text[:50]}...")
        return True
    except Exception as e:
        logger.error(f"❌ Error posting tweet to Twitter: {e}")
        return False


@app.route("/slack/interactions", methods=["POST"])
def handle_slack_interactions():
    """Handle Slack button clicks and modal submissions"""
    try:
        logger.info("🔄 Handling Slack interaction")
        # Get request data for verification
        timestamp = request.headers.get("X-Slack-Request-Timestamp")
        signature = request.headers.get("X-Slack-Signature")
        request_body = request.get_data(as_text=True)

        # Verify the request came from Slack
        if not verify_slack_request(request_body, timestamp, signature):
            logger.error("❌ Request verification failed - rejecting request")
            return jsonify({"error": "Request verification failed"}), 403

        payload = json.loads(request.form.get("payload"))
        logger.debug(f"📨 Received Slack interaction: {payload.get('type', 'unknown')}")

        if payload["type"] == "block_actions":
            # Handle button clicks
            action = payload["actions"][0]
            action_id = action["action_id"]
            tweet_text = action["value"]
            message_ts = payload["message"]["ts"]

            logger.info(
                f"🔘 Button clicked: {action_id} for tweet: {tweet_text[:30]}..."
            )

            if action_id.startswith("approve_tweet_"):
                # Approve and post tweet
                logger.info(f"✅ Approving tweet: {tweet_text[:50]}...")
                success = post_tweet_to_twitter(tweet_text)
                if success:
                    remove_tweet_from_json(tweet_text)
                    if slack_bot:
                        slack_bot.update_message_status(message_ts, "approved")
                    return jsonify({"text": "✅ Tweet approved and posted!"})
                else:
                    logger.warning("❌ Failed to post tweet to Twitter")
                    return jsonify(
                        {"text": "❌ Failed to post tweet. Please try again."}
                    )

            elif action_id.startswith("edit_tweet_"):
                # Open edit modal
                logger.info(f"✏️ Opening edit modal for tweet: {tweet_text[:50]}...")
                trigger_id = payload["trigger_id"]
                tweet_index = action_id.split("_")[-1]

                modal_view = {
                    "type": "modal",
                    "callback_id": f"edit_modal_{tweet_index}_{message_ts}",
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
                                "max_length": 500,
                            },
                            "label": {"type": "plain_text", "text": "Tweet Content"},
                        }
                    ],
                }

                slack_client.views_open(trigger_id=trigger_id, view=modal_view)

                return jsonify({"text": "Opening edit modal..."})

            elif action_id.startswith("reject_tweet_"):
                # Reject tweet
                logger.info(f"❌ Rejecting tweet: {tweet_text[:50]}...")
                remove_tweet_from_json(tweet_text)
                if slack_bot:
                    slack_bot.update_message_status(message_ts, "rejected")
                return jsonify({"text": "❌ Tweet rejected and removed from queue."})

            elif action_id == "disabled_button":
                # Handle clicks on disabled buttons
                logger.info("🚫 User clicked on disabled button - ignoring")
                return jsonify({"text": "This tweet has already been processed."})

        elif payload["type"] == "view_submission":
            # Handle modal submission (edited tweet)
            logger.info("📝 Processing modal submission (edited tweet)")
            callback_id = payload["view"]["callback_id"]
            values = payload["view"]["state"]["values"]
            edited_tweet = values["tweet_input"]["tweet_text"]["value"]

            # Extract message timestamp from callback_id
            message_ts = callback_id.split("_")[-1]

            logger.info(f"📝 Posting edited tweet: {edited_tweet[:50]}...")

            # Post the edited tweet
            success = post_tweet_to_twitter(edited_tweet)
            if success:
                # Remove original tweet from queue
                remove_tweet_from_json(edited_tweet)
                if slack_bot:
                    slack_bot.update_message_status(message_ts, "edited", edited_tweet)

                return jsonify({"response_action": "clear"})
            else:
                logger.warning("❌ Failed to post edited tweet")
                return jsonify(
                    {
                        "response_action": "errors",
                        "errors": {
                            "tweet_input": "Failed to post tweet. Please try again."
                        },
                    }
                )

        return jsonify({"status": "ok"})

    except Exception as e:
        logger.error(f"❌ Error handling Slack interaction: {e}")
        return jsonify({"text": "❌ An error occurred processing your request."})


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    logger.debug("💓 Health check requested")
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    logger.info("🚀 Starting Slack webhook server on port 5003...")
    app.run(debug=True, port=5003, host="127.0.0.1")
