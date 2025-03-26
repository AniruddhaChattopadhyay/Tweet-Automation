from litellm import completion
import json
def get_quote_response():
    try:
        with open('quotes.json', 'r') as f:
            quotes_list = json.load(f)
    except FileNotFoundError:
        quotes_list = []

    system_message = '''You are a helpful assistant that can generate a quote it's author and its explanation.
        Write in first person as if you are the me, a 26year old story teller from India. I intent to tweet this quote.
        Please don't make it sound like a quote, but a story. Make it engaging and interesting. Don't make it sound AI, make it sound natural.
        THE INTENTION IS TO MAKE THE TWEET VIRAL'''
        
    user_message = f'''Generate a quote for me to tweet. Make it short and engaging. Don't make it sound like a quote, but a story. Make it engaging and interesting. Don't make it sound AI, make it sound natural. Don't include the following quotes :
{quotes_list}'''
    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "quote": {
                        "type": "string",
                    },
                    "author": {
                        "type": "string",
                    },
                    "explanation": {
                        "type": "string",
                    }
                },
                "required": ["quote","author","explanation"],
            },
        }


    response = completion(
        model="gemini/gemini-2.0-flash", 
        messages=messages, 
        response_format={"type": "json_object", "response_schema": response_schema} # 👈 KEY CHANGE
        )
    response = json.loads(response.choices[0].message.content)
    response = response[0]
    print(response)
    tweet_str = f"{response['quote']}"# - {response['author']} \n\n {response['explanation']}"
    quotes_list.append(tweet_str)
    with open('quotes.json', 'w') as f:
        json.dump(quotes_list, f)
    return tweet_str


def get_psychology_fact():
    try:
        with open('psychology_facts.json', 'r') as f:
            facts_list = json.load(f)
    except FileNotFoundError:
        facts_list = []
        
    system_message = '''You are a helpful assistant that generates interesting psychological facts and their explanations.
        Write in first person as if you are me, a 26-year-old psychology enthusiast from India. I intend to tweet this fact.
        Make it engaging and relatable to everyday life. Focus on interesting psychological phenomena, cognitive biases, 
        or behavioral patterns. Don't make it sound academic - explain it like you're telling a friend.
        THE INTENTION IS TO MAKE THE TWEET VIRAL'''
        
    user_message = f'''Share an interesting psychological fact or phenomenon that people might not know about. 
    Make it engaging and easy to understand. Include a brief real-life example or application.
    Don't include any of these previously shared facts: {facts_list}'''

    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                    },
                    "phenomenon": {
                        "type": "string",
                    },
                    "explanation": {
                        "type": "string",
                    }
                },
                "required": ["fact", "phenomenon", "explanation"],
            },
        }

    response = completion(
        model="gemini/gemini-2.0-flash", 
        messages=messages, 
        response_format={"type": "json_object", "response_schema": response_schema}
        )
    
    response = json.loads(response.choices[0].message.content)
    response = response[0]
    tweet_str = f"🧠 {response['fact']}\n\n💡 {response['phenomenon']}\n\n📝 {response['explanation']}"
    
    facts_list.append(tweet_str)
    with open('psychology_facts.json', 'w') as f:
        json.dump(facts_list, f)
    
    return tweet_str



def get_cultural_insight():
    try:
        with open('cultural_insights.json', 'r') as f:
            insights_list = json.load(f)
    except FileNotFoundError:
        insights_list = []
        
    system_message = '''You are a cultural storyteller sharing fascinating insights about Indian culture, traditions,
    festivals, and customs. Write in first person as if you are a 26-year-old Indian sharing cultural knowledge.
    Focus on lesser-known aspects, interesting origins, and meaningful connections to modern life.
    Make it engaging and relatable while maintaining authenticity and respect for the traditions.
    THE INTENTION IS TO MAKE THE TWEET VIRAL'''
        
    user_message = f'''Share an interesting insight about Indian culture, tradition, or festival.
    It could be about food, customs, celebrations, art forms, or traditional practices.
    Make it engaging and informative. Explain its significance and how it relates to modern life.
    Don't include any of these previously shared insights: {insights_list}'''

    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response_schema = {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The cultural topic or tradition being discussed"
                },
                "significance": {
                    "type": "string",
                    "description": "Historical and cultural significance of the topic"
                },
                "modern_relevance": {
                    "type": "string",
                    "description": "How this tradition or custom relates to modern life"
                }
            },
            "required": ["topic", "significance", "modern_relevance"]
    }

    response = completion(
        model="gemini/gemini-2.0-flash", 
        messages=messages, 
        response_format={"type": "json_object", "response_schema": response_schema}
    )
    
    response = json.loads(response.choices[0].message.content)
    tweet_str = f"{response['topic']}\n\n📜 {response['significance']}\n\n🔄 {response['modern_relevance']}"
    
    insights_list.append(tweet_str)
    with open('cultural_insights.json', 'w') as f:
        json.dump(insights_list, f)
    
    return tweet_str