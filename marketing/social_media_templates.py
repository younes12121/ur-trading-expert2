"""
Social Media Content Templates for UR Trading Expert Bot
Templates for Twitter, LinkedIn, YouTube, and Telegram
"""

SOCIAL_MEDIA_TEMPLATES = {
    "twitter": {
        "morning_market_analysis": [
            "🌅 Good morning traders! Market analysis for today:\n\n📊 {market_summary}\n\n🎯 Key levels to watch:\n• Support: {support_level}\n• Resistance: {resistance_level}\n\n#TradingSignals #Forex #Crypto",
            "☕ Morning market update:\n\n{asset} showing {trend} signals\n\nEntry: {entry_price}\nStop Loss: {stop_loss}\nTake Profit: {take_profit}\n\n#TradingSignals #Bitcoin #Forex",
        ],
        "educational_tip": [
            "💡 Trading Tip of the Day:\n\n{tip}\n\nRemember: {reminder}\n\n#TradingTips #ForexEducation #TradingSignals",
            "📚 Did you know?\n\n{fact}\n\nThis is why {explanation}\n\n#TradingEducation #Forex #Crypto",
        ],
        "signal_results": [
            "📈 Signal Performance Update:\n\n✅ Win Rate: {win_rate}%\n💰 Profit Factor: {profit_factor}\n📊 Total Trades: {total_trades}\n\nTransparent results, real performance.\n\n#TradingSignals #Forex #Results",
            "🎯 Latest Signal Results:\n\n{asset}: {direction} signal\nResult: {result}\n\nTrack all signals: {link}\n\n#TradingSignals #Forex #Crypto",
        ],
        "testimonial": [
            "⭐ User Review:\n\n\"{testimonial}\" - {user_name}\n\nJoin {user_count}+ traders using our signals\n\n#TradingSignals #Testimonials",
        ],
        "backtest_results": [
            "📊 Backtest Results:\n\nPeriod: {period}\nWin Rate: {win_rate}%\nTotal Return: {return}%\n\nReal data, transparent results.\n\n#TradingSignals #Backtesting #Forex",
        ]
    },
    
    "linkedin": {
        "thought_leadership": [
            "The Future of AI in Trading: How Machine Learning is Revolutionizing Market Analysis\n\n{content}\n\n#AITrading #FinTech #TradingSignals",
            "Risk Management in Trading: Why 96% Win Rates Don't Guarantee Success\n\n{content}\n\n#RiskManagement #Trading #Finance",
        ],
        "case_study": [
            "Case Study: How One Trader Increased Their Win Rate by 40% Using AI-Powered Signals\n\n{content}\n\n#TradingCaseStudy #AITrading #Forex",
        ],
        "industry_insights": [
            "Market Analysis: {market_trend}\n\nKey insights:\n• {insight_1}\n• {insight_2}\n• {insight_3}\n\n#MarketAnalysis #Trading #Finance",
        ]
    },
    
    "youtube": {
        "video_titles": [
            "How to Use Trading Signals: Complete Beginner's Guide 2025",
            "AI Trading Bot Review: 96% Win Rate - Real or Fake?",
            "ES Futures Trading: Complete Strategy Guide",
            "Bitcoin Trading Signals: How to Read and Use Them",
            "Forex vs Crypto: Which is Better for Trading?",
            "Smart Money Concept Explained: Institutional Trading Secrets",
            "Risk Management Calculator: How to Size Your Trades",
            "Top 10 Telegram Trading Bots Reviewed (2025)",
            "How to Read Trading Signals Like a Pro",
            "Day Trading vs Swing Trading: Which Strategy Wins?",
        ],
        "video_descriptions": """
🎯 [Video Title]

In this video, we cover:
• {point_1}
• {point_2}
• {point_3}

📊 Get professional trading signals:
🔗 [Your Bot Link]

💡 Key Takeaways:
{key_takeaways}

📚 Resources:
• Free Trading Course: [Link]
• Signal Bot: [Link]
• Trading Community: [Link]

🔔 Subscribe for more trading content!

#TradingSignals #Forex #Crypto #TradingEducation

---
Disclaimer: Trading involves risk. Past performance does not guarantee future results.
        """
    },
    
    "telegram": {
        "channel_post": [
            "🚨 NEW SIGNAL ALERT\n\n{asset}: {direction}\nEntry: {entry}\nStop Loss: {stop_loss}\nTake Profit: {take_profit}\n\nConfidence: {confidence}%\n\n#TradingSignals",
            "📊 Market Update\n\n{market_summary}\n\nKey events today:\n• {event_1}\n• {event_2}\n\nStay tuned for signals!\n\n#MarketAnalysis",
        ],
        "community_announcement": [
            "🎉 Community Milestone!\n\nWe've reached {milestone} members!\n\nThank you for being part of our trading community.\n\n#Community #TradingSignals",
        ]
    }
}

HASHTAGS = {
    "general": ["#TradingSignals", "#Forex", "#Crypto", "#Trading", "#Investing"],
    "crypto": ["#Bitcoin", "#BTC", "#Ethereum", "#ETH", "#Crypto", "#Cryptocurrency"],
    "forex": ["#Forex", "#FX", "#EURUSD", "#GBPUSD", "#ForexTrading"],
    "futures": ["#ES", "#NQ", "#Futures", "#FuturesTrading", "#SP500"],
    "education": ["#TradingEducation", "#TradingTips", "#LearnTrading", "#TradingGuide"],
    "results": ["#TradingResults", "#WinRate", "#Backtesting", "#TradingPerformance"],
}

def generate_twitter_post(template_type: str, data: dict) -> str:
    """Generate a Twitter post from template"""
    if template_type not in SOCIAL_MEDIA_TEMPLATES["twitter"]:
        return "Template type not found"
    
    templates = SOCIAL_MEDIA_TEMPLATES["twitter"][template_type]
    import random
    template = random.choice(templates)
    
    # Replace placeholders
    for key, value in data.items():
        template = template.replace(f"{{{key}}}", str(value))
    
    return template

def generate_linkedin_post(template_type: str, content: str) -> str:
    """Generate a LinkedIn post"""
    if template_type not in SOCIAL_MEDIA_TEMPLATES["linkedin"]:
        return "Template type not found"
    
    templates = SOCIAL_MEDIA_TEMPLATES["linkedin"][template_type]
    import random
    template = random.choice(templates)
    
    return template.replace("{content}", content)

def get_hashtags(category: str, count: int = 5) -> list:
    """Get hashtags for a category"""
    if category in HASHTAGS:
        tags = HASHTAGS[category]
        import random
        return random.sample(tags, min(count, len(tags)))
    
    return HASHTAGS["general"][:count]

if __name__ == "__main__":
    # Example usage
    twitter_post = generate_twitter_post("morning_market_analysis", {
        "market_summary": "Markets showing bullish momentum",
        "support_level": "$50,000",
        "resistance_level": "$52,000"
    })
    print("Twitter Post:")
    print(twitter_post)
    print("\nHashtags:", " ".join(get_hashtags("crypto", 3)))



