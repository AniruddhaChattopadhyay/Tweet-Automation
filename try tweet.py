import tweepy
import json
import random
import schedule
import time
import os
from dotenv import load_dotenv
import requests
import pytz
from llm import get_quote_response, get_cultural_insight, get_psychology_fact



# Load environment variables
load_dotenv()
os.environ['GEMINI_API_KEY'] = os.getenv("GEMINI_API_KEY")


# X API credentials
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

# Option 1: Load quotes from a local file
def load_local_quotes():
    with open("quotes.json", "r") as file:
        return json.load(file)

# Option 2: Fetch a random quote from an API
timezone = pytz.timezone('Asia/Kolkata')

def fetch_quote_from_api():
    url = "https://api.quotable.io/random"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    data = response.json()
    return f"{data['content']} - {data['author']}"
# Post a random quote
def post_quote():
    try:
        quote = get_quote_response()
        # client.create_tweet(text=quote)
        print(f"Posted: {quote}")
    except Exception as e:
        print(f"Error: {e}")

def post_cultural_insight():
    try:
        insight = get_cultural_insight()
        # client.create_tweet(text=insight)
        print(f"Posted: {insight}")
    except Exception as e:
        print(f"Error: {e}")

def post_psychology_fact():
    try:
        fact = get_psychology_fact()
        # client.create_tweet(text=fact)
        print(f"Posted: {fact}")
    except Exception as e:
        print(f"Error: {e}")

def choose_random_post():
    # Dictionary mapping of functions
    post_functions = {
        'quote': post_quote,
        'cultural': post_cultural_insight,
        'psychology': post_psychology_fact
    }
    
    # Randomly choose a function
    chosen_type = random.choice(list(post_functions.keys()))
    chosen_function = post_functions[chosen_type]
    
    try:
        print(f"Posting {chosen_type}...")
        chosen_function()
    except Exception as e:
        print(f"Error in {chosen_type}: {e}")

# # Schedule posts for IST timezone
# schedule.every().day.at("11:00",timezone).do(choose_random_post)  # 9:30 AM IST
# schedule.every().day.at("16:00",timezone).do(choose_random_post)  # 2:00 PM IST 
# schedule.every().day.at("21:00",timezone).do(choose_random_post)  # 7:30 PM IST

# while True:
#     schedule.run_pending()
#     time.sleep(900)  # Sleep for 15 minutes

if __name__ == "__main__":
    choose_random_post()


