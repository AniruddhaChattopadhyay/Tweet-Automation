# 🚀 Slack Tweet Approval Bot Setup Guide

This guide will help you set up the Slack bot for tweet approval workflow.

## 📋 Prerequisites

- Python 3.8+
- A Slack workspace where you're an admin
- Gmail account with 2FA enabled
- Twitter/X API credentials
- Gemini API key

## 🔧 Environment Setup

### 1. Create a `.env` file in your project root:

```env
# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Twitter/X API Credentials
API_KEY=your_twitter_api_key_here
API_SECRET=your_twitter_api_secret_here
ACCESS_TOKEN=your_twitter_access_token_here
ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here

# Gmail IMAP Configuration
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password_here

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_CHANNEL=#tweets
SLACK_SIGNING_SECRET=your-slack-signing-secret-here
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

## 🤖 Slack Bot Setup

### Step 1: Create a Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "Tweet Approval Bot")
4. Select your workspace

### Step 2: Configure Bot Permissions

1. Go to "OAuth & Permissions" in your app settings
2. Add these **Bot Token Scopes**:
   - `chat:write` - Send messages
   - `chat:write.public` - Send messages to channels
   - `im:write` - Send DMs
   - `commands` - Use slash commands
   - `incoming-webhook` - Receive webhooks

### Step 3: Install the App

1. Still in "OAuth & Permissions", click "Install to Workspace"
2. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
3. Add it to your `.env` file as `SLACK_BOT_TOKEN`

### Step 3.5: Get the Signing Secret

1. Go to "Basic Information" in your app settings
2. Scroll down to "App Credentials"
3. Copy the **Signing Secret**
4. Add it to your `.env` file as `SLACK_SIGNING_SECRET`

### Step 4: Configure Interactivity

1. Go to "Interactivity & Shortcuts" in your app settings
2. Turn on "Interactivity"
3. Set the **Request URL** to: `https://your-domain.com/slack/interactions`
   - For local development, use ngrok (see below)

### Step 5: Set up ngrok (for local development)

1. Install ngrok: https://ngrok.com/download
2. Run: `ngrok http 5000`
3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
4. Use this URL in your Slack app settings: `https://abc123.ngrok.io/slack/interactions`

## 📧 Gmail Setup

### Enable App Password

1. Go to your Google Account settings
2. Enable 2-Factor Authentication (if not already enabled)
3. Go to Security → App passwords
4. Generate a new app password for "Mail"
5. Copy the 16-character password
6. Add to `.env` as `GMAIL_APP_PASSWORD`

## 🏃‍♂️ Running the Bot

### Terminal 1: Start the Slack webhook server

```bash
python slack_webhook.py
```

### Terminal 2: Start the main bot

```bash
python tweet.py
```

### Terminal 3: Start ngrok (for local development)

```bash
ngrok http 5000
```

## 🔄 How It Works

1. **Email Processing**: Bot fetches latest email from `news@smol.ai`
2. **Tweet Generation**: Uses Gemini to generate tweets from email content
3. **Slack Approval**: Sends tweets to Slack with interactive buttons
4. **User Actions**: You can:
   - ✅ **Approve & Tweet**: Posts immediately to Twitter
   - ✏️ **Edit Tweet**: Opens modal to edit, then posts
   - ❌ **Reject**: Removes tweet from queue
5. **Scheduling**: Automatically sends tweets for approval at scheduled times

## 📱 Slack Interface

Each tweet appears in Slack like this:

```
🐦 Tweet Ready for Approval

Your tweet content here...

[✅ Approve & Tweet] [✏️ Edit Tweet] [❌ Reject]
```

## 🛠️ Troubleshooting

### Common Issues:

1. **"Gmail credentials not found"**

   - Check your `.env` file has `GMAIL_USER` and `GMAIL_APP_PASSWORD`
   - Ensure Gmail App Password is correct

2. **"No emails found from news@smol.ai"**

   - Make sure you have emails from news@smol.ai in your inbox
   - Check spam folder

3. **Slack interactions not working**

   - Verify ngrok is running and URL is correct in Slack app settings
   - Check that Flask server is running on port 5000

4. **Twitter posting fails**
   - Verify Twitter API credentials in `.env`
   - Check Twitter API rate limits

### Debug Mode:

Run with debug output:

```bash
python -u tweet.py
```

## 🎯 Next Steps

1. Test the workflow with a sample email
2. Schedule the bot to run at your preferred times
3. Monitor the approval process in Slack
4. Customize tweet generation prompts as needed

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all credentials are correctly set
3. Test each component individually
4. Check server logs for error messages

---

🎉 **You're all set!** Your tweet approval bot is ready to help you maintain quality control over your automated tweets.
