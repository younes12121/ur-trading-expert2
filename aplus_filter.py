"""
A+ Setup Filter - Only Shows Highest Probability Trades
Strict filtering to protect capital and force patience
"""

from news_fetcher import NewsFetcher

class APlusFilter:
    """
    Filters trading signals to only show A+ setups
    Based on multiple confirmation criteria + news awareness
    """
    
    def __init__(self):
        self.min_confidence = 70  # Minimum 70% confidence
        self.min_rr_ratio = 2.0   # Minimum 1:2 risk/reward
        self.news_fetcher = NewsFetcher()  # News integration
        
    def check_trend_confirmation(self, market_data):
        """
        Check if trend is confirmed across multiple timeframes
        Returns: (bool, str) - (is_confirmed, reason)
        """
        # For now, we'll use sentiment and volume as proxies
        sentiment = market_data.get('market_sentiment', 0.5)
        volume_ratio = market_data.get('volume_ratio', 1.0)
        
        # Strong bullish confirmation
        if sentiment > 0.65 and volume_ratio > 1.2:
            return True, "Strong bullish trend with volume"
        
        # Strong bearish confirmation
        if sentiment < 0.35 and volume_ratio > 1.2:
            return True, "Strong bearish trend with volume"
        
        # Weak or no trend
        return False, f"Weak trend (sentiment: {sentiment:.2f}, volume: {volume_ratio:.2f})"
    
    def check_support_resistance(self, current_price, signal_direction):
        """
        Check if price is near key support/resistance
        Returns: (bool, str) - (is_valid, reason)
        """
        # Key psychological levels
        key_levels = [85000, 86000, 87000, 88000, 89000, 90000]
        
        # Find nearest level
        nearest_level = min(key_levels, key=lambda x: abs(x - current_price))
        distance = abs(current_price - nearest_level)
        distance_pct = (distance / current_price) * 100
        
        # Price should be within 0.5% of a key level for best entries
        if distance_pct < 0.5:
            if signal_direction == "BUY" and current_price < nearest_level:
                return True, f"Near support at ${nearest_level:,}"
            elif signal_direction == "SELL" and current_price > nearest_level:
                return True, f"Near resistance at ${nearest_level:,}"
        
        return False, f"Not near key level (closest: ${nearest_level:,}, {distance_pct:.2f}% away)"
    
    def check_volatility(self, volatility):
        """
        Check if volatility is in acceptable range
        Returns: (bool, str) - (is_valid, reason)
        """
        # Volatility should be moderate (not too high, not too low)
        # Annual volatility between 30% and 80% is ideal
        vol_pct = volatility * 100
        
        if 30 <= vol_pct <= 80:
            return True, f"Healthy volatility ({vol_pct:.1f}%)"
        elif vol_pct > 80:
            return False, f"Too volatile ({vol_pct:.1f}%) - high risk"
        else:
            return False, f"Too quiet ({vol_pct:.1f}%) - low opportunity"
    
    def check_fear_greed(self, fear_greed_value):
        """
        Check Fear & Greed for extreme levels (contrarian signals)
        Returns: (bool, str) - (is_valid, reason)
        """
        # Extreme Fear (< 25) or Extreme Greed (> 75) are best for contrarian trades
        if fear_greed_value < 25:
            return True, f"Extreme Fear ({fear_greed_value}) - contrarian buy opportunity"
        elif fear_greed_value > 75:
            return True, f"Extreme Greed ({fear_greed_value}) - contrarian sell opportunity"
        else:
            return False, f"Neutral sentiment ({fear_greed_value}) - wait for extremes"
    
    def check_risk_reward(self, entry, stop_loss, take_profit_2):
        """
        Check if risk/reward ratio meets minimum threshold
        Returns: (bool, str, float) - (is_valid, reason, rr_ratio)
        """
        if stop_loss is None or take_profit_2 is None:
            return False, "No valid SL/TP levels", 0.0
        
        risk = abs(entry - stop_loss)
        reward = abs(take_profit_2 - entry)
        
        if risk == 0:
            return False, "Invalid risk calculation", 0.0
        
        rr_ratio = reward / risk
        
        if rr_ratio >= self.min_rr_ratio:
            return True, f"Excellent R:R (1:{rr_ratio:.2f})", rr_ratio
        else:
            return False, f"Poor R:R (1:{rr_ratio:.2f}) - need min 1:{self.min_rr_ratio}", rr_ratio
    
    def check_signal_confluence(self, signal_data):
        """
        Check if multiple indicators agree (confluence)
        Returns: (bool, str) - (is_valid, reason)
        """
        # Check if algebraic, probabilistic, and MC all agree
        market_analysis = signal_data.get('market_analysis', {})
        signal_strength = market_analysis.get('signal_strength', 0)
        
        # Signal strength should be > 2% for strong conviction
        if signal_strength > 2.0:
            return True, f"Strong signal confluence ({signal_strength:.2f}%)"
        else:
            return False, f"Weak confluence ({signal_strength:.2f}%) - need > 2%"
    
    def check_news(self, hours_back=2):
        """
        Check for high-impact BTC news
        Returns: (bool, str, list) - (is_safe, reason, news_items)
        Note: If news API unavailable, returns True (safe) to not block trades
        """
        try:
            news_check = self.news_fetcher.check_high_impact_news(hours_back=hours_back)
            
            if news_check['has_high_impact']:
                news_count = news_check['news_count']
                return False, f"[WARN] {news_count} important news item(s) in last {hours_back}h - HIGH RISK", news_check['recent_news']
            elif news_check['warning'] and 'unavailable' in news_check['warning'].lower():
                # API unavailable - don't block trade, but warn
                return True, f"[WARN] News API unavailable - trade with caution", []
            else:
                return True, f"[OK] No major news in last {hours_back}h - safe to trade", []
                
        except Exception as e:
            # If news fetch fails completely, don't block the trade but warn
            return True, f"[WARN] News check failed - proceed with caution", []
    
    def filter_signal(self, signal_data, market_data):
        """
        Main filter function - checks all criteria
        Returns: (bool, dict) - (is_aplus, reasons)
        """
        # Don't filter HOLD signals
        if signal_data['direction'] == 'HOLD':
            return False, {'overall': 'No trade signal'}
        
        reasons = {}
        all_checks_passed = True
        
        # 1. Confidence check
        confidence = signal_data.get('confidence', 0)
        if confidence >= self.min_confidence:
            reasons['confidence'] = f"[OK] High confidence ({confidence}%)"
        else:
            reasons['confidence'] = f"[FAIL] Low confidence ({confidence}%) - need min {self.min_confidence}%"
            all_checks_passed = False
        
        # 2. Trend confirmation
        trend_ok, trend_msg = self.check_trend_confirmation(market_data)
        reasons['trend'] = f"{'[OK]' if trend_ok else '[FAIL]'} {trend_msg}"
        if not trend_ok:
            all_checks_passed = False
        
        # 3. Support/Resistance
        current_price = market_data['btc_price']
        sr_ok, sr_msg = self.check_support_resistance(current_price, signal_data['direction'])
        reasons['support_resistance'] = f"{'[OK]' if sr_ok else '[FAIL]'} {sr_msg}"
        if not sr_ok:
            all_checks_passed = False
        
        # 4. Volatility check
        volatility = market_data['btc_volatility']
        vol_ok, vol_msg = self.check_volatility(volatility)
        reasons['volatility'] = f"{'[OK]' if vol_ok else '[FAIL]'} {vol_msg}"
        if not vol_ok:
            all_checks_passed = False
        
        # 5. Fear & Greed (if available)
        fear_greed = market_data.get('fear_greed_value', 50)
        fg_ok, fg_msg = self.check_fear_greed(fear_greed)
        reasons['fear_greed'] = f"{'[OK]' if fg_ok else '[FAIL]'} {fg_msg}"
        if not fg_ok:
            all_checks_passed = False
        
        # 6. Risk/Reward ratio
        rr_ok, rr_msg, rr_ratio = self.check_risk_reward(
            signal_data['entry_price'],
            signal_data['stop_loss'],
            signal_data['take_profit_2']
        )
        reasons['risk_reward'] = f"{'[OK]' if rr_ok else '[FAIL]'} {rr_msg}"
        if not rr_ok:
            all_checks_passed = False
        
        # 7. Signal confluence
        conf_ok, conf_msg = self.check_signal_confluence(signal_data)
        reasons['confluence'] = f"{'[OK]' if conf_ok else '[FAIL]'} {conf_msg}"
        if not conf_ok:
            all_checks_passed = False
        
        # 8. News check (important!)
        news_ok, news_msg, news_items = self.check_news(hours_back=2)
        reasons['news'] = f"{'[OK]' if news_ok else '[WARN]'} {news_msg}"
        if not news_ok:
            all_checks_passed = False
        
        # Store news items for display
        reasons['news_items'] = news_items
        
        # Overall verdict
        if all_checks_passed:
            reasons['overall'] = "[A+ SETUP] ALL CRITERIA MET!"
        else:
            passed_count = sum(1 for k, v in reasons.items() if k not in ['overall', 'news_items'] and '[OK]' in str(v))
            total_count = len([k for k in reasons.keys() if k not in ['overall', 'news_items']])
            reasons['overall'] = f"[NOT A+] ({passed_count}/{total_count} criteria passed)"
        
        return all_checks_passed, reasons


if __name__ == "__main__":
    # Test the filter
    print("A+ Filter Module Loaded Successfully!")
    print("This module will only show you the highest probability setups.")
