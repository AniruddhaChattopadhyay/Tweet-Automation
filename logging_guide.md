# 📊 Logging System Guide

Your Tweet Automation Bot now has a comprehensive logging system that tracks everything that happens. Here's how to use it effectively.

## 🎯 **What Gets Logged**

### **📧 Email Processing** (`llm.py`)

- Email fetching from Gmail
- Email content processing
- Tweet generation with Gemini API
- Performance metrics

### **📱 Slack Integration** (`slack_bot.py`)

- Tweet approval requests
- Button clicks and interactions
- Modal operations
- Message updates

### **🔗 Webhook Events** (`slack_webhook.py`)

- Incoming Slack interactions
- Tweet approvals/rejections
- Twitter posting attempts
- Error handling

### **🐦 Twitter Operations** (`tweet.py`)

- Tweet queue management
- Scheduling activities
- Bot startup/shutdown

## 📁 **Log Files Structure**

```
logs/
├── tweet_bot.log      # Main application log (INFO+)
├── errors.log         # Errors and critical issues only
├── debug.log          # Everything (DEBUG+)
├── gmail.log          # Gmail-specific operations
├── slack.log          # Slack-specific operations
├── twitter.log        # Twitter-specific operations
├── llm.log           # LLM/AI-specific operations
└── webhook.log       # Webhook-specific operations
```

## 🎨 **Log Levels & Colors**

### **Console Output (Colored)**

- 🟢 **INFO**: General information (Green)
- 🟡 **WARNING**: Potential issues (Yellow)
- 🔴 **ERROR**: Errors that don't stop execution (Red)
- 🟣 **CRITICAL**: Fatal errors (Magenta)
- 🔵 **DEBUG**: Detailed debugging info (Cyan)

### **File Logging**

- All logs include timestamps, module names, function names, and line numbers
- Automatic log rotation (prevents huge files)
- Different retention policies for different log types

## 📊 **Log Rotation**

| Log File        | Max Size | Backup Count | Total Storage |
| --------------- | -------- | ------------ | ------------- |
| `tweet_bot.log` | 10MB     | 5 backups    | ~50MB         |
| `errors.log`    | 5MB      | 3 backups    | ~15MB         |
| `debug.log`     | 20MB     | 2 backups    | ~40MB         |
| Component logs  | 5MB      | 2 backups    | ~10MB each    |

## 🔍 **How to Use the Logs**

### **Real-time Monitoring**

```bash
# Watch main log
tail -f logs/tweet_bot.log

# Watch errors only
tail -f logs/errors.log

# Watch specific component
tail -f logs/slack.log
```

### **Search for Issues**

```bash
# Find all errors
grep "ERROR" logs/tweet_bot.log

# Find specific operations
grep "tweet posted" logs/twitter.log

# Find performance issues
grep "completed in" logs/debug.log
```

### **Analyze Performance**

```bash
# Find slow operations (>2 seconds)
grep -E "completed in [2-9][0-9]*\.[0-9]+s" logs/debug.log
```

## 🛠️ **Log Format Examples**

### **Console Output**

```
14:30:25 | llm | INFO | ✅ Generated 8 tweets successfully
14:30:26 | slack | INFO | ✅ Tweet sent to Slack for approval: Context engineering is the new prompt engineering...
14:30:27 | webhook | INFO | 🔘 Button clicked: approve_tweet_0 for tweet: Context engineering...
```

### **File Output**

```
2024-01-15 14:30:25 | llm | INFO | generate_tweets_from_email:142 | ✅ Generated 8 tweets successfully
2024-01-15 14:30:26 | slack | INFO | send_tweet_for_approval:45 | ✅ Tweet sent to Slack for approval: Context engineering is the new prompt engineering...
```

## 🚀 **Performance Tracking**

Functions decorated with `@log_performance` automatically track:

- **Execution time**
- **Success/failure status**
- **Function names and modules**

Example:

```
2024-01-15 14:30:25 | llm | DEBUG | ⚡ generate_tweets_from_email completed in 3.47s
2024-01-15 14:30:26 | slack | DEBUG | ⚡ send_tweet_for_approval completed in 0.12s
```

## 🔧 **Customizing Logging**

### **Change Log Levels**

Edit `logger_config.py`:

```python
# More verbose console output
console_handler.setLevel(logging.DEBUG)

# Less verbose file output
main_file_handler.setLevel(logging.WARNING)
```

### **Add New Component Logger**

```python
from logger_config import get_logger
logger = get_logger('my_component')
```

### **Use in Your Code**

```python
logger.info("✅ Operation successful")
logger.warning("⚠️ Something might be wrong")
logger.error("❌ Something failed")
logger.debug("🔍 Detailed debugging info")
```

## 📈 **Monitoring & Alerts**

### **Daily Log Review**

```bash
# Check yesterday's errors
grep "$(date -d yesterday '+%Y-%m-%d')" logs/errors.log

# Count daily operations
grep "$(date '+%Y-%m-%d')" logs/tweet_bot.log | wc -l
```

### **Common Issues to Watch For**

- **High error rates**: `grep -c "ERROR" logs/errors.log`
- **Slow operations**: `grep "completed in [5-9]" logs/debug.log`
- **API failures**: `grep "API.*failed" logs/*.log`
- **Authentication issues**: `grep "credentials" logs/*.log`

## 🎯 **Best Practices**

### **For Debugging**

1. **Start with errors**: Check `logs/errors.log` first
2. **Check component logs**: Look at specific component files
3. **Use debug mode**: Temporarily enable debug logging
4. **Follow the timeline**: Use timestamps to trace sequences

### **For Monitoring**

1. **Daily error checks**: Review error logs daily
2. **Performance monitoring**: Watch for slow operations
3. **Storage management**: Monitor log file sizes
4. **Backup important logs**: Archive logs for compliance

## 🔒 **Security & Privacy**

### **What's NOT Logged**

- **API keys or passwords**
- **Full email content** (only summaries)
- **Personal information**
- **Internal Slack tokens**

### **What IS Logged**

- **Operation outcomes**
- **Performance metrics**
- **Error messages**
- **Tweet content** (for debugging)

## 📞 **Troubleshooting**

### **No Logs Appearing**

1. Check if `logs/` directory exists
2. Verify file permissions
3. Check disk space
4. Restart the application

### **Log Files Too Large**

- Log rotation should handle this automatically
- Check rotation settings in `logger_config.py`
- Manually clean old logs if needed

### **Missing Component Logs**

- Ensure the component is importing `logger_config`
- Check if the component is using the correct logger name
- Verify the component is being executed

---

🎉 **Your logging system is now ready to help you monitor and debug your Tweet Automation Bot!**
