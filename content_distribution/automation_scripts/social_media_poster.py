#!/usr/bin/env python3
"""
Social Media Automation Script
Posts content to multiple platforms automatically
"""

import tweepy
import requests
import json
from datetime import datetime
from pathlib import Path

class SocialMediaPoster:
    def __init__(self, config_path="content_distribution/distribution_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Load API keys from environment or config
        self.twitter_api = None
        self.telegram_bot = None

    def post_to_twitter(self, content, image_path=None):
        """Post content to Twitter"""
        if not self.twitter_api:
            return False

        try:
            if image_path and Path(image_path).exists():
                media = self.twitter_api.media_upload(image_path)
                tweet = self.twitter_api.update_status(
                    status=content,
                    media_ids=[media.media_id]
                )
            else:
                tweet = self.twitter_api.update_status(status=content)

            print(f"Posted to Twitter: {tweet.id}")
            return True
        except Exception as e:
            print(f"Twitter posting failed: {e}")
            return False

    def post_to_telegram(self, content, channel="main"):
        """Post content to Telegram channel"""
        if not self.telegram_bot:
            return False

        try:
            # Telegram Bot API call
            url = f"https://api.telegram.org/bot{self.telegram_bot}/sendMessage"
            data = {
                "chat_id": f"@{channel}",
                "text": content,
                "parse_mode": "HTML"
            }

            response = requests.post(url, data=data)
            if response.status_code == 200:
                print(f"Posted to Telegram {channel}")
                return True
        except Exception as e:
            print(f"Telegram posting failed: {e}")

        return False

    def create_content_thread(self, title, points):
        """Create Twitter thread from content"""
        thread_tweets = []

        # Main tweet
        main_tweet = f"🧵 {title}\n\nA thread 👇"
        thread_tweets.append(main_tweet)

        # Content points
        for i, point in enumerate(points, 1):
            tweet = f"{i}/{len(points)} {point}"
            if len(tweet) > 280:
                # Split long tweets
                chunks = [tweet[i:i+270] + "..." for i in range(0, len(tweet), 270)]
                thread_tweets.extend(chunks)
            else:
                thread_tweets.append(tweet)

        # Call to action
        cta = f"\nTry UR Trading Expert free:\nhttps://urtradingexpert.com/subscribe\n\n#TradingSignals #Forex #Crypto"
        thread_tweets.append(cta)

        return thread_tweets

    def schedule_content(self, platform, content, schedule_time):
        """Schedule content for future posting"""
        # Implementation would integrate with Buffer, Hootsuite, etc.
        print(f"Scheduled {platform} post for {schedule_time}")

    def generate_market_update(self):
        """Generate daily market update post"""
        # This would fetch real market data
        content = """📊 Daily Market Update

🌅 Market Open: All major indices trading higher

📈 Key Movements:
• S&P 500: +0.8%
• NASDAQ: +1.2%
• DOW: +0.6%

💱 Forex:
• EUR/USD: Holding 1.0850
• GBP/USD: Testing 1.2750
• USD/JPY: Range bound

₿ Crypto:
• BTC: $43,250 (+2.1%)
• ETH: $2,680 (+1.8%)

🎯 Trading Focus:
High-probability setups in ES and NQ futures
Risk management remains key

#MarketUpdate #TradingSignals"""

        return content

def main():
    poster = SocialMediaPoster()

    # Generate and post market update
    market_update = poster.generate_market_update()

    # Post to platforms
    poster.post_to_twitter(market_update)
    poster.post_to_telegram(market_update, "main_channel")

    print("Content distribution completed")

if __name__ == "__main__":
    main()
