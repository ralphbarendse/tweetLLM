# 🚀 tweetLLM: Unleash the Power of AI-Generated Threads! 🧠🐦

Welcome to the future of Twitter engagement! The tweetLLM is your ultimate companion for creating captivating, informative, and viral-worthy Twitter threads with the magic of AI. Say goodbye to writer's block and hello to a constant stream of engaging content! 🎉

## 🌟 Features

- 🤖 AI-powered content generation
- 📚 Automatic research on any given topic
- 🧵 Smart thread creation with storytelling elements
- 🖼️ Relevant image fetching for visual appeal
- #️⃣ Intelligent hashtag integration
- 😊 Appropriate emoji usage for added flair

## 🛠️ Installation

1. Clone this repository:
   ```
   git clone https://github.com/ralphbarendse/tweetLLM.git
   cd tweetLLM
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Copy the `dotenvexample.env` file to `.env`
   - Fill in your API keys and tokens in the `.env` file

4. Update the `config.py` file with your API keys and tokens

## 🔑 API Keys Required

To use the tweetLLM, you'll need to obtain API keys for the following services:

- Twitter API (v2)
- Tavily API
- Anthropic API (for Claude AI)
- Unsplash API

Make sure to keep your API keys secret and never share them publicly!

## 🚀 Usage

Run the script with:

```
python main.py
```

Follow the prompts to enter your desired thread topic, and watch as the AI weaves its magic! 🎩✨

## 🧠 How It Works

1. **Topic Research**: The script uses the Tavily API to gather relevant and up-to-date information on your chosen topic.

2. **Content Generation**: Leveraging the power of Claude AI (via the Anthropic API), the gathered information is transformed into an engaging Twitter thread.

3. **Image Selection**: The Unsplash API is used to fetch a relevant image for the first tweet, adding visual appeal to your thread.

4. **Thread Posting**: The script authenticates with the Twitter API and posts your AI-generated thread, complete with numbered tweets and the selected image.

## 📊 Thread Structure

Each generated thread follows a carefully crafted structure to maximize engagement:

- A captivating hook to grab attention
- A mix of facts, opinions, and anecdotes
- Thought-provoking questions and cliffhangers
- Relevant statistics and examples
- Seamlessly integrated hashtags
- A strong conclusion that invites interaction

## 🛡️ Error Handling

tweetLLM is built with robust error handling to ensure smooth operation. It gracefully manages API rate limits, connection issues, and content generation hiccups.

## 🤝 Contributing

We welcome contributions to make the tweetLLM even more awesome! Feel free to submit issues, feature requests, or pull requests.

## 🙏 Acknowledgements

- [Tweepy](https://www.tweepy.org/) for Twitter API handling
- [Anthropic](https://www.anthropic.com/) for the amazing Claude AI
- [Tavily](https://tavily.com/) for powerful web search capabilities
- [Unsplash](https://unsplash.com/) for beautiful, free images

---

Happy tweeting! May your threads go viral and your engagement soar! 🚀📈🎊
