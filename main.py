import tweepy
import os
from dotenv import load_dotenv
import requests
import logging
from bs4 import BeautifulSoup
from config import TWITTER_API_KEY, TWITTER_API_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TAVILY_API_KEY, ANTHROPIC_API_KEY, UNSPLASH_ACCESS_TOKEN, UNSPLASH_ACCESS_TOKEN_SECRET
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from tweepy.errors import TweepyException
from tweepy.errors import BadRequest
from tavily import TavilyClient
import io
from PIL import Image, UnidentifiedImageError
import requests
import mimetypes

# Note: This script requires the Pillow library to be installed.
# You can install it using: pip install Pillow

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def authenticate_twitter():
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        logger.error("One or more required Twitter API keys are missing. Please check your config.py file.")
        return None, None
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET_KEY,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        logger.info("Twitter authentication successful")
        return client, api
    except TweepyException as e:
        logger.error(f"Error authenticating Twitter: {str(e)}")
        logger.error("Please check your API keys and tokens in the config.py file.")
        return None, None

def tavily_search(query):
    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        tavily = TavilyClient(api_key=tavily_api_key)
        response = tavily.search(query=query, search_depth="advanced", include_images=True)
        logger.info(f"Web search successful for query: {query}")
        return response
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        return None

def summarize_content(content, subject):
    try:
        anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""{HUMAN_PROMPT}Create an engaging and informative Twitter thread about {subject} based on the following content. Your reply should be a series of tweets, each separated by '---'. Follow these guidelines:

1. Create 8-12 tweets, each no longer than 280 characters.
2. Begin with a hook that captures attention and introduces the topic.
3. Each tweet should be self-contained but also flow well as part of the thread.
4. Use storytelling elements to maintain interest throughout the thread.
5. Include relevant statistics, quotes, or examples to support your points.
6. Incorporate thought-provoking questions or cliffhangers to encourage readers to continue.
7. Use a mix of information types: facts, opinions, anecdotes, and implications.
8. Address potential counterarguments or alternative viewpoints where appropriate.
9. Include 1-2 relevant hashtags per tweet, integrated naturally into the text.
10. Use emojis sparingly to add visual appeal without overwhelming the content.
11. Conclude with a strong summary tweet that reinforces the main points and invites engagement.

Ensure the thread is coherent, engaging, and provides valuable insights on {subject}. Here's the content to summarize:

{content}{AI_PROMPT}"""
        
        completion = anthropic.completions.create(
            model="claude-2.1",
            max_tokens_to_sample=2000,
            prompt=prompt
        )
        
        # Parse the AI's response into a list of tweets
        tweets = [tweet.strip() for tweet in completion.completion.split('---') if tweet.strip()]
        
        logger.info(f"Content summarization successful for subject: {subject}")
        return tweets
    except anthropic.APIError as e:
        logger.error(f"Error in content summarization: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in content summarization: {str(e)}")
        return None

def unsplash_image_search(query):
    try:
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_TOKEN}"
        }
        response = requests.get(
            f"https://api.unsplash.com/search/photos?query={query}&per_page=1",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data['results']:
            image_url = data['results'][0]['urls']['regular']
            image_response = requests.get(image_url, timeout=10)
            image_response.raise_for_status()
            
            image = Image.open(io.BytesIO(image_response.content))
            image_file = io.BytesIO()
            image.save(image_file, format='PNG')
            image_file.seek(0)
            image_file.name = 'image.png'
            logger.info(f"Successfully fetched Unsplash image for query: {query}")
            return image_file
        
        logger.warning(f"No suitable Unsplash image found for query: {query}")
        return None
    except requests.RequestException as e:
        logger.error(f"Network error while fetching Unsplash image for query '{query}': {str(e)}")
    except UnidentifiedImageError as e:
        logger.error(f"Error processing Unsplash image for query '{query}': {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching Unsplash image for query '{query}': {str(e)}")
    return None

def fetch_relevant_image(subject):
    queries = [
        f"{subject}",
        f"{subject} image",
        f"{subject} portrait",
        f"{subject} photograph"
    ]

    for query in queries:
        image = unsplash_image_search(query)
        if image:
            return image

    logger.error(f"Failed to fetch any relevant Unsplash image for subject: {subject}")
    return None



def create_twitter_thread(client, api, subject):
    search_results = tavily_search(subject)
    if not search_results:
        logger.warning("No search results found. Unable to create thread.")
        return False

    # Extract relevant information from search results
    content = ""
    for result in search_results.get('results', []):
        content += result.get('content', '') + "\n"

    if not content:
        logger.warning("No relevant content found in search results. Unable to create thread.")
        return False

    tweets = summarize_content(content, subject)
    if not tweets:
        logger.warning("Failed to summarize content. Unable to create thread.")
        return False

    # Fetch image for the first tweet
    image = fetch_relevant_image(subject)

    # Post the thread
    previous_tweet_id = None
    for i, tweet in enumerate(tweets, 1):
        try:
            numbered_tweet = f"{tweet}\n\n{i}/{len(tweets)}"
            if previous_tweet_id:
                tweet_response = client.create_tweet(text=numbered_tweet, in_reply_to_tweet_id=previous_tweet_id)
            else:
                if image:
                    media = api.media_upload(filename=image.name, file=image)
                    tweet_response = client.create_tweet(text=numbered_tweet, media_ids=[media.media_id])
                else:
                    logger.warning(f"No image available for the first tweet. Posting without image.")
                    tweet_response = client.create_tweet(text=numbered_tweet)
            previous_tweet_id = tweet_response.data['id']
            logger.info(f"Posted tweet {i}/{len(tweets)}: {numbered_tweet}")
        except TweepyException as e:
            logger.error(f"Error posting tweet {i}/{len(tweets)}: {str(e)}")
            return False
    logger.info("Twitter thread created successfully")
    return True

def validate_api_keys():
    missing_keys = []
    if not TWITTER_API_KEY:
        missing_keys.append("TWITTER_API_KEY")
    if not TWITTER_API_SECRET_KEY:
        missing_keys.append("TWITTER_API_SECRET_KEY")
    if not TWITTER_ACCESS_TOKEN:
        missing_keys.append("TWITTER_ACCESS_TOKEN")
    if not TWITTER_ACCESS_TOKEN_SECRET:
        missing_keys.append("TWITTER_ACCESS_TOKEN_SECRET")
    if not TAVILY_API_KEY:
        missing_keys.append("TAVILY_API_KEY")
    if not ANTHROPIC_API_KEY:
        missing_keys.append("ANTHROPIC_API_KEY")
    if not UNSPLASH_ACCESS_TOKEN:
        missing_keys.append("UNSPLASH_ACCESS_TOKEN")
    
    if missing_keys:
        logger.error(f"The following API keys are missing: {', '.join(missing_keys)}")
        return False
    logger.info("All API keys are present")
    return True

def check_api_connectivity():
    try:
        # Check Twitter API
        api = authenticate_twitter()
        if not api:
            raise Exception("Failed to authenticate with Twitter API")
        
        # Check Tavily API
        search_results = tavily_search("test query")
        if not search_results:
            raise Exception("Failed to get results from Tavily API")
        
        # Check Anthropic API
        summary = summarize_content("This is a test content.", "test")
        if not summary:
            raise Exception("Failed to get summary from Anthropic API")
        
        # Check Unsplash API
        test_image = unsplash_image_search("test")
        if not test_image:
            raise Exception("Failed to get image from Unsplash API")
        
        logger.info("All API connections are working")
        return True
    except Exception as e:
        logger.error(f"API connectivity check failed: {str(e)}")
        return False

def main():
    logger.info("Welcome to the Twitter Auto-Poster by ralphbarendse! Please be advised to use this tool carefully and appropriately.")
    
    if not validate_api_keys():
        logger.error("API key validation failed. Please check your config.py file. Exiting.")
        return
    logger.info("API keys validated successfully.")

    if not check_api_connectivity():
        logger.error("API connectivity check failed. Please check your internet connection and API keys. Exiting.")
        return
    logger.info("API connectivity check passed.")

    subject = input("Enter the subject for the Twitter thread: ")
    client, api = authenticate_twitter()
    if client and api:
        logger.info(f"Starting thread creation process for subject: {subject}")
        success = create_twitter_thread(client, api, subject)
        if success:
            logger.info("Twitter thread created successfully!")
        else:
            logger.error("Failed to create the Twitter thread. Please check the error messages above and your API keys.")
    else:
        logger.error("Failed to authenticate Twitter. Please check your credentials in the config.py file.")

if __name__ == "__main__":
    main()