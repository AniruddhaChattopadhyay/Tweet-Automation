import tweepy
import json
import os
from dotenv import load_dotenv
import pytz
from llm import generate_tweets_from_email
from slack_bot import SlackTweetBot
from slack_webhook import set_slack_bot
from logger_config import get_logger, log_performance

# Load environment variables
load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Get logger for this module
logger = get_logger("twitter")

# X API credentials
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

# Initialize Slack bot
slack_bot = SlackTweetBot()
set_slack_bot(slack_bot)  # Set global reference for webhook handler

timezone = pytz.timezone("Asia/Kolkata")


@log_performance
def send_tweet_for_approval():
    """Send the next tweet to Slack for approval instead of posting directly"""
    try:
        with open("generated_tweets.json", "r") as f:
            tweets = json.load(f)

        if tweets:
            # Get the next tweet in queue
            tweet_data = tweets[0]
            tweet_text = (
                tweet_data.get("tweet", "")
                if isinstance(tweet_data, dict)
                else tweet_data
            )

            # Send to Slack for approval
            message_ts = slack_bot.send_tweet_for_approval(tweet_text, 0)

            if message_ts:
                logger.info(
                    f"✅ Tweet sent to Slack for approval: {tweet_text[:50]}..."
                )
            else:
                logger.error("❌ Failed to send tweet to Slack")

        else:
            logger.warning("📭 No tweets in queue. Generating new tweets...")
            # generate_tweets_from_email()
            # # Try again after generating
            # send_tweet_for_approval()

    except FileNotFoundError:
        logger.warning("📄 generated_tweets.json not found. Generating new tweets...")
        generate_tweets_from_email()
        send_tweet_for_approval()
    except Exception as e:
        logger.error(f"❌ An error occurred: {e}")


def post_generated_tweet():
    """Legacy function - now redirects to Slack approval workflow"""
    logger.info("📨 Checking for tweets to send for approval...")
    send_tweet_for_approval()


# Generate tweets from email at the start
logger.info("🚀 Starting tweet automation with Slack approval workflow...")
logger.info("📧 Generating tweets from latest email...")
# generate_tweets_from_email()

# Send first tweet for approval
logger.info("📨 Sending first tweet to Slack for approval...")
send_tweet_for_approval()

logger.info("✅ Tweet automation ready!")
logger.info("📱 Make sure to run the Slack webhook server: python slack_webhook.py")
logger.info("🔄 Bot will send tweets to Slack for approval at scheduled times")
