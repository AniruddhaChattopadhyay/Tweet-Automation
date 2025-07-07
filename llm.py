import json
import imaplib
import email
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from logger_config import get_logger, log_performance

# Load environment variables
load_dotenv()

# Get logger for this module
logger = get_logger("llm")


class Tweet(BaseModel):
    tweet: str = Field(description="The tweet to be posted")


@log_performance
def fetch_latest_email_from_gmail():
    """Fetch the latest email from Gmail using IMAP"""
    try:
        # Gmail IMAP settings
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")

        if not gmail_user or not gmail_password:
            logger.error("Gmail credentials not found in environment variables")
            return None

        # Connect to Gmail
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_user, gmail_password)

        # Select inbox
        mail.select("inbox")

        # Search for emails from news@smol.ai and get the latest one
        status, messages = mail.search(None, 'FROM "news@smol.ai"')
        email_ids = messages[0].split()

        if not email_ids:
            logger.warning("No emails found from news@smol.ai")
            return None

        # Get the latest email (last ID in the list)
        latest_email_id = email_ids[-1]

        # Fetch the email
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)

        # Extract email content
        email_content = ""
        subject = email_message["subject"]
        from_email = email_message["from"]

        # Get email body
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    email_content = part.get_payload(decode=True).decode()
                    break
        else:
            email_content = email_message.get_payload(decode=True).decode()

        # Close connection
        mail.logout()

        # Combine subject and content
        full_email_content = (
            f"Subject: {subject}\nFrom: {from_email}\n\n{email_content}"
        )

        logger.info(f"✅ Successfully fetched email: {subject[:50]}...")
        return full_email_content

    except Exception as e:
        logger.error(f"💥 Error fetching email: {e}")
        return None


@log_performance
def generate_tweets_from_email():
    # Try to fetch from Gmail first, fallback to text file
    try:
        with open("email.txt", "r") as f:
            email_content = f.read()
        logger.info("📄 Using email content from email.txt file")
    except FileNotFoundError:
        logger.info("📧 email.txt not found, fetching from Gmail...")
        email_content = fetch_latest_email_from_gmail()

        if email_content:
            # save email to file
            with open("email.txt", "w") as f:
                f.write(email_content)
            logger.info("💾 Email content saved to email.txt")
        else:
            logger.error("❌ Failed to fetch email from Gmail")
            return None

    user_message = f"""### SYSTEM
You are "Ani on X” — an irreverent but insightful AI engineer who writes tweets that mix sharp analysis with light shit-posting.  
Assume the audience is technically literate (builders, PMs, VCs) and lives on tech Twitter.

### TASK
Turn the newsletter text I supply (inside the <NEWSLETTER> … </NEWSLETTER> tag) into fresh tweets.

### DELIVERABLE
Return valid JSON shaped like:
{
        [
            {"tweet": "tweet 1"},
            {"tweet": "tweet 2"},
        ]
    }

### HOW MANY
* Aim for 8–12 tweets per newsletter.
* Each tweet must be self-contained (no “1/🧵” unless explicitly asked).
* If the newsletter has a blockbuster story (e.g., paradigm-shifting model release) add **one** bonus “mini-thread”: 1 headline tweet + up to 3 follow-ups. Use the same JSON schema but wrap that thread inside a `"thread"` key.
* The tweets can be longer than 280 characters if needed.
### STYLE GUIDE
1. **Hook first**: open strong or weird. Examples:  
   * “Ilya just rage-quit the stealth mode.”  
   * “Context engineering is the new prompt engineering—fight me.”
2. **Voice**: plain English, short sentences, meme-ready. A sprinkle of 🚀, 💀 or 😂 is fine, but keep emoji below 2 per tweet.
3. **Substance**: always include at least one concrete detail (metric, quote, link) from the source.  
   * Good: “Perplexity just dropped Morningstar reports for free. Bloomberg terminal speed-run? 🤔”  
   * Bad: “Big news in AI today!”
4. **Take**: add a quick opinion, question, or joke so the tweet isn’t just a headline.
5. **Avoid**: LinkedIn­-style hype, “As an AI model…”, generic praise, over-formal syntax.
6. **Length**: The tweets can be longer than 280 characters if needed.

### CONTENT SELECTION RULES
* Prioritise stories with at least one of:
  * Major leadership change or new product launch.
  * Open-source model/tool release engineers can try today.
  * Data points that spark debate (benchmarks, power usage 📈).
* Skip duplicate coverage unless you can add a spicy angle.


### PROCESS (think step-by-step but don’t show steps)
1. Parse the newsletter into bullet-point facts.  
2. Score each fact on **tweet-worthiness** (novelty, impact, fun).  
3. Draft tweets following the style guide.  
4. Self-check against the Quality Checklist below.  
5. Output JSON.

### QUALITY CHECKLIST
- [ ] Hook in first 7 words.  
- [ ] Concrete fact or stat from source.  
- [ ] Opinion / quip adds human flavor.  
- [ ] Spelling / grammar clean.  

### INPUT
<NEWSLETTER>
{email_content}
</NEWSLETTER>
"""

    logger.info("🤖 Generating tweets using Gemini API...")
    client = genai.Client()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=user_message,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[Tweet],
            },
        )
        response_json = json.loads(response.text)

        # Log the number of tweets generated
        tweet_count = len(response_json)
        logger.info(f"✅ Generated {tweet_count} tweets successfully")

        with open("generated_tweets.json", "w") as f:
            json.dump(response_json, f, indent=2)

        logger.info("💾 Tweets saved to generated_tweets.json")
        return response

    except Exception as e:
        logger.error(f"💥 Error generating tweets with Gemini: {e}")
        return None
