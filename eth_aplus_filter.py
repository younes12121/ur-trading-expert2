"""
ETH A+ Setup Filter - Highest Probability ETH Trades Only
Strict filtering adapted for Ethereum's unique market characteristics
"""

from news_fetcher import NewsFetcher
from advanced_data_fetcher import AdvancedDataFetcher
from datetime import datetime, timedelta

class ETHAPlusFilter:
    """
    ETH-specific A+ filter with crypto market adaptations
    Based on ETH dominance, ETH/BTC ratio, and crypto-specific news
    """

    def __init__(self):
        # ETH-specific thresholds (stricter than BTC due to higher volatility)
        self.min_confidence = 75  # Higher than BTC's 70%
        self.min_rr_ratio = 2.2   # Higher than BTC's 2.0
        self.news_fetcher = NewsFetcher()
        self.data_fetcher = AdvancedDataFetcher()

        # ETH-specific market levels (current ranges)
        self.eth_key_levels = {
            'major_support': [3200, 3000, 2800, 2600],
            'major_resistance': [3800, 4000, 4200, 4500],
            'medium_support': [3400, 3500, 3600],
            'medium_resistance': [3700, 3900, 4100],
            'psychological': [3000, 3500, 4000]  # Round numbers matter in crypto
        }

        # ETH volatility ranges (higher than BTC)
        self.eth_volatility_ranges = {
            'optimal_min': 50,   # 50% annual volatility minimum
            'optimal_max': 120,  # 120% annual volatility maximum
            'too_high': 150,     # Above this = too risky
            'too_low': 30        # Below this = low opportunity
        }

        # ETH correlation and dominance thresholds
        self.eth_correlation_thresholds = {
            'btc_correlation_min': 0.6,    # Minimum BTC correlation for valid signals
            'eth_dominance_min': 15.0,     # Minimum ETH dominance %
            'eth_dominance_max': 25.0,     # Maximum ETH dominance %
            'eth_btc_ratio_min': 0.055,    # Minimum ETH/BTC ratio
            'eth_btc_ratio_max': 0.080     # Maximum ETH/BTC ratio
        }

    def check_trend_confirmation(self, market_data):
        """
        ETH-specific trend confirmation using crypto metrics
        Returns: (bool, str) - (is_confirmed, reason)
        """
        # Get ETH-specific data
        eth_dominance = market_data.get('eth_dominance', 18.0)  # Typical ~18%
        eth_btc_ratio = market_data.get('eth_btc_ratio', 0.065)  # Typical ~6.5%
        btc_dominance = market_data.get('btc_dominance', 45.0)  # Typical ~45%

        # Check ETH dominance trend (should be stable/increasing)
        dominance_trend = market_data.get('eth_dominance_trend', 'stable')

        # Check ETH/BTC ratio trend
        ratio_trend = market_data.get('eth_btc_ratio_trend', 'stable')

        # Strong bullish confirmation for ETH
        if (eth_dominance > self.eth_correlation_thresholds['eth_dominance_min'] and
            eth_btc_ratio > self.eth_correlation_thresholds['eth_btc_ratio_min'] and
            dominance_trend in ['increasing', 'stable'] and
            ratio_trend in ['increasing', 'stable']):

            return True, f"Strong ETH bullish trend (dominance: {eth_dominance:.1f}%, ratio: {eth_btc_ratio:.3f})"
        # Strong bearish confirmation for ETH
        if (eth_dominance < 16.0 and  # Below average dominance
            eth_btc_ratio < 0.06 and  # Below average ratio
            (dominance_trend == 'decreasing' or ratio_trend == 'decreasing')):

            return True, f"Strong ETH bearish trend (dominance: {eth_dominance:.1f}%, ratio: {eth_btc_ratio:.3f})"
        # Weak or unclear trend
        return False, f"Weak ETH trend (dominance: {eth_dominance:.1f}%, ratio: {eth_btc_ratio:.3f})"

    def check_support_resistance(self, current_price, signal_direction):
        """
        ETH-specific support/resistance levels
        Returns: (bool, str) - (is_valid, reason)
        """
        # Combine all key levels
        all_levels = (self.eth_key_levels['major_support'] +
                     self.eth_key_levels['major_resistance'] +
                     self.eth_key_levels['medium_support'] +
                     self.eth_key_levels['medium_resistance'] +
                     self.eth_key_levels['psychological'])

        # Find nearest level
        nearest_level = min(all_levels, key=lambda x: abs(x - current_price))
        distance = abs(current_price - nearest_level)
        distance_pct = (distance / current_price) * 100

        # ETH allows slightly wider range than BTC due to volatility (0.8% vs 0.5%)
        if distance_pct < 0.8:
            if signal_direction == "BUY" and current_price < nearest_level:
                level_type = self._identify_level_type(nearest_level)
                return True, f"Near {level_type} support at ${nearest_level:,} ({distance_pct:.2f}% away)"
            elif signal_direction == "SELL" and current_price > nearest_level:
                level_type = self._identify_level_type(nearest_level)
                return True, f"Near {level_type} resistance at ${nearest_level:,} ({distance_pct:.2f}% away)"

        return False, f"Not near key level (closest: ${nearest_level:,}, {distance_pct:.2f}% away)"
    def _identify_level_type(self, level):
        """Identify if level is major, medium, or psychological"""
        if level in self.eth_key_levels['major_support'] or level in self.eth_key_levels['major_resistance']:
            return "major"
        elif level in self.eth_key_levels['medium_support'] or level in self.eth_key_levels['medium_resistance']:
            return "medium"
        elif level in self.eth_key_levels['psychological']:
            return "psychological"
        else:
            return "minor"

    def check_volatility(self, volatility):
        """
        ETH-specific volatility check (ETH is more volatile than BTC)
        Returns: (bool, str) - (is_valid, reason)
        """
        vol_pct = volatility * 100

        # ETH optimal range is higher than BTC
        if (self.eth_volatility_ranges['optimal_min'] <= vol_pct <=
            self.eth_volatility_ranges['optimal_max']):
            return True, f"Healthy ETH volatility ({vol_pct:.1f}%)"
        elif vol_pct > self.eth_volatility_ranges['too_high']:
            return False, f"ETH too volatile ({vol_pct:.1f}%) - high risk"
        else:
            return False, f"ETH too quiet ({vol_pct:.1f}%) - low opportunity"
    def check_fear_greed_crypto(self, fear_greed_value, eth_dominance=None):
        """
        ETH-specific Fear & Greed check with crypto market context
        Returns: (bool, str) - (is_valid, reason)
        """
        # Extreme Fear (< 25) or Extreme Greed (> 75) are best for contrarian trades
        if fear_greed_value < 25:
            # In extreme fear, check if ETH dominance is oversold
            if eth_dominance and eth_dominance < 16.0:
                return True, f"Extreme Fear ({fear_greed_value}) + ETH oversold ({eth_dominance:.1f}%) - strong contrarian buy"
            else:
                return True, f"Extreme Fear ({fear_greed_value}) - contrarian buy opportunity"
        elif fear_greed_value > 75:
            # In extreme greed, check if ETH dominance is overbought
            if eth_dominance and eth_dominance > 22.0:
                return True, f"Extreme Greed ({fear_greed_value}) + ETH overbought ({eth_dominance:.1f}%) - strong contrarian sell"
            else:
                return True, f"Extreme Greed ({fear_greed_value}) - contrarian sell opportunity"
        else:
            # Neutral - check for mean reversion opportunities
            if eth_dominance:
                if eth_dominance < 17.0 and fear_greed_value < 45:
                    return True, f"ETH oversold ({eth_dominance:.1f}% dominance) + neutral sentiment"
                elif eth_dominance > 21.0 and fear_greed_value > 55:
                    return True, f"ETH overbought ({eth_dominance:.1f}% dominance) + neutral sentiment"

            return False, f"Neutral sentiment ({fear_greed_value}) - wait for extremes or ETH dominance signals"

    def check_eth_correlation(self, market_data):
        """
        Check ETH correlation metrics for market context
        Returns: (bool, str) - (is_valid, reason)
        """
        eth_dominance = market_data.get('eth_dominance', 18.0)
        eth_btc_ratio = market_data.get('eth_btc_ratio', 0.065)
        btc_correlation = market_data.get('btc_correlation', 0.7)

        # Check dominance range
        if not (self.eth_correlation_thresholds['eth_dominance_min'] <=
                eth_dominance <=
                self.eth_correlation_thresholds['eth_dominance_max']):
            return False, f"ETH dominance ({eth_dominance:.1f}%) outside optimal range {self.eth_correlation_thresholds['eth_dominance_min']}-{self.eth_correlation_thresholds['eth_dominance_max']}%"
        # Check ETH/BTC ratio range
        if not (self.eth_correlation_thresholds['eth_btc_ratio_min'] <=
                eth_btc_ratio <=
                self.eth_correlation_thresholds['eth_btc_ratio_max']):
            return False, f"ETH/BTC ratio ({eth_btc_ratio:.3f}) outside optimal range {self.eth_correlation_thresholds['eth_btc_ratio_min']}-{self.eth_correlation_thresholds['eth_btc_ratio_max']}"
        # Check BTC correlation (ETH should correlate but not too strongly)
        if btc_correlation < self.eth_correlation_thresholds['btc_correlation_min']:
            return False, f"BTC correlation ({btc_correlation:.2f}) too weak (min: {self.eth_correlation_thresholds['btc_correlation_min']})"
        return True, f"ETH correlation healthy (dominance: {eth_dominance:.1f}%, ratio: {eth_btc_ratio:.3f}, BTC corr: {btc_correlation:.2f})"
    def check_funding_rate(self, symbol="ETHUSDT"):
        """
        Check ETH futures funding rate for institutional sentiment
        Returns: (bool, str) - (is_valid, reason)
        """
        try:
            funding_data = self.data_fetcher.get_funding_rate(symbol)
            if not funding_data:
                return True, "[WARN] Funding rate unavailable - proceed with caution"

            funding_rate = funding_data['funding_rate'] * 100  # Convert to percentage

            # Positive funding rate = longs paying shorts (bullish institutional bias)
            # Negative funding rate = shorts paying longs (bearish institutional bias)
            if funding_rate > 0.05:  # >0.05% positive funding
                return True, f"Positive ETH funding rate ({funding_rate:.3f}%) - institutional bullish bias"
            elif funding_rate < -0.05:  # <-0.05% negative funding
                return True, f"Negative ETH funding rate ({funding_rate:.3f}%) - institutional bearish bias"
            else:
                return False, f"Neutral ETH funding rate ({funding_rate:.3f}%) - mixed institutional sentiment"
        except Exception as e:
            return True, f"[WARN] Funding rate check failed: {str(e)}"

    def check_news_eth(self, hours_back=3):
        """
        ETH-specific news check with crypto keywords
        Returns: (bool, str, list) - (is_safe, reason, news_items)
        """
        try:
            news_check = self.news_fetcher.check_high_impact_news(hours_back=hours_back)

            if news_check['has_high_impact']:
                news_count = news_check['news_count']
                # Check if news specifically mentions ETH
                eth_related = any('eth' in str(item).lower() or 'ethereum' in str(item).lower()
                                for item in news_check['recent_news'])
                if eth_related:
                    return False, f"[BLOCK] {news_count} ETH-related news item(s) in last {hours_back}h - HIGH RISK", news_check['recent_news']
                else:
                    return True, f"[OK] {news_count} crypto news items (non-ETH) - ETH safe to trade", news_check['recent_news']
            elif news_check['warning'] and 'unavailable' in news_check['warning'].lower():
                return True, f"[WARN] News API unavailable - trade ETH with caution", []
            else:
                return True, f"[OK] No major crypto news in last {hours_back}h - safe to trade ETH", []

        except Exception as e:
            return True, f"[WARN] ETH news check failed - proceed with caution", []

    def check_volume_profile(self, market_data):
        """
        Check ETH volume profile for institutional activity
        Returns: (bool, str) - (is_valid, reason)
        """
        volume_ratio = market_data.get('volume_ratio', 1.0)
        volume_trend = market_data.get('volume_trend', 'stable')
        oi_change = market_data.get('open_interest_change', 0)

        # High volume + increasing OI = strong institutional interest
        if volume_ratio > 1.5 and volume_trend == 'increasing':
            if oi_change > 5:  # OI increased by >5%
                return True, f"Strong ETH institutional interest (volume: {volume_ratio:.1f}x, OI: +{oi_change:.1f}%)"
            elif oi_change > 0:
                return True, f"Good ETH volume + OI increase (volume: {volume_ratio:.1f}x, OI: +{oi_change:.1f}%)"
            else:
                return True, f"Strong ETH volume despite OI decrease (volume: {volume_ratio:.1f}x)"
        # Moderate volume is acceptable
        elif volume_ratio > 1.0:
            return True, f"Moderate ETH volume ({volume_ratio:.1f}x average)"
        else:
            return False, f"Low ETH volume ({volume_ratio:.1f}x average) - weak conviction"
    def filter_eth_signal(self, signal_data, market_data):
        """
        Main ETH A+ filter function - checks all ETH-specific criteria
        Returns: (bool, dict) - (is_aplus, reasons)
        """
        # Don't filter HOLD signals
        if signal_data['direction'] == 'HOLD':
            return False, {'overall': 'No ETH trade signal'}

        reasons = {}
        all_checks_passed = True

        # 1. Confidence check (higher threshold for ETH)
        confidence = signal_data.get('confidence', 0)
        if confidence >= self.min_confidence:
            reasons['confidence'] = f"[OK] High ETH confidence ({confidence}%)"
        else:
            reasons['confidence'] = f"[FAIL] Low confidence ({confidence}%) - need min {self.min_confidence}%"
            all_checks_passed = False

        # 2. ETH trend confirmation
        trend_ok, trend_msg = self.check_trend_confirmation(market_data)
        reasons['eth_trend'] = f"{'[OK]' if trend_ok else '[FAIL]'} {trend_msg}"
        if not trend_ok:
            all_checks_passed = False

        # 3. ETH support/resistance
        current_price = market_data.get('eth_price', signal_data.get('entry_price', 3500))
        sr_ok, sr_msg = self.check_support_resistance(current_price, signal_data['direction'])
        reasons['eth_support_resistance'] = f"{'[OK]' if sr_ok else '[FAIL]'} {sr_msg}"
        if not sr_ok:
            all_checks_passed = False

        # 4. ETH volatility check
        volatility = market_data.get('eth_volatility', 0.8)  # Default 80%
        vol_ok, vol_msg = self.check_volatility(volatility)
        reasons['eth_volatility'] = f"{'[OK]' if vol_ok else '[FAIL]'} {vol_msg}"
        if not vol_ok:
            all_checks_passed = False

        # 5. ETH Fear & Greed check
        fear_greed = market_data.get('fear_greed_value', 50)
        eth_dominance = market_data.get('eth_dominance', 18.0)
        fg_ok, fg_msg = self.check_fear_greed_crypto(fear_greed, eth_dominance)
        reasons['eth_fear_greed'] = f"{'[OK]' if fg_ok else '[FAIL]'} {fg_msg}"
        if not fg_ok:
            all_checks_passed = False

        # 6. Risk/Reward ratio (higher minimum for ETH)
        rr_ok, rr_msg, rr_ratio = self.check_risk_reward(
            signal_data['entry_price'],
            signal_data['stop_loss'],
            signal_data.get('take_profit_2', signal_data.get('take_profit_1', 0))
        )
        reasons['eth_risk_reward'] = f"{'[OK]' if rr_ok else '[FAIL]'} {rr_msg}"
        if not rr_ok:
            all_checks_passed = False

        # 7. ETH correlation check
        corr_ok, corr_msg = self.check_eth_correlation(market_data)
        reasons['eth_correlation'] = f"{'[OK]' if corr_ok else '[FAIL]'} {corr_msg}"
        if not corr_ok:
            all_checks_passed = False

        # 8. Funding rate check
        funding_ok, funding_msg = self.check_funding_rate("ETHUSDT")
        reasons['eth_funding_rate'] = f"{'[OK]' if funding_ok else '[FAIL]'} {funding_msg}"
        if not funding_ok:
            all_checks_passed = False

        # 9. ETH news check (longer window than BTC)
        news_ok, news_msg, news_items = self.check_news_eth(hours_back=3)
        reasons['eth_news'] = f"{'[OK]' if news_ok else '[BLOCK]'} {news_msg}"
        if not news_ok:
            all_checks_passed = False

        # 10. Volume profile check
        volume_ok, volume_msg = self.check_volume_profile(market_data)
        reasons['eth_volume'] = f"{'[OK]' if volume_ok else '[FAIL]'} {volume_msg}"
        if not volume_ok:
            all_checks_passed = False

        # Store news items for display
        reasons['news_items'] = news_items

        # Overall verdict
        if all_checks_passed:
            reasons['overall'] = "[ETH A+] ALL CRITERIA MET! 🔥"
        else:
            passed_count = sum(1 for k, v in reasons.items()
                             if k not in ['overall', 'news_items'] and '[OK]' in str(v))
            total_count = len([k for k in reasons.keys()
                             if k not in ['overall', 'news_items']])
            reasons['overall'] = f"[NOT ETH A+] ({passed_count}/{total_count} criteria passed)"

        return all_checks_passed, reasons

    # Keep the original methods for compatibility
    def check_risk_reward(self, entry, stop_loss, take_profit_2):
        """Use original risk/reward check but with ETH-specific minimum"""
        if stop_loss is None or take_profit_2 is None:
            return False, "No valid SL/TP levels", 0.0

        risk = abs(entry - stop_loss)
        reward = abs(take_profit_2 - entry)

        if risk == 0:
            return False, "Invalid risk calculation", 0.0

        rr_ratio = reward / risk

        if rr_ratio >= self.min_rr_ratio:
            return True, f"Excellent ETH R:R (1:{rr_ratio:.2f})", rr_ratio
        else:
            return False, f"Poor R:R (1:{rr_ratio:.2f}) - need min 1:{self.min_rr_ratio}", rr_ratio


if __name__ == "__main__":
    # Test the ETH A+ filter
    print("🔥 ETH A+ Filter Module Loaded Successfully!")
    print("This module provides the strictest filtering for ETH trades.")
    print("=" * 60)
    print("ETH A+ Criteria:")
    print("• Confidence: 75%+ (vs BTC 70%)")
    print("• Risk/Reward: 2.2:1+ (vs BTC 2.0:1)")
    print("• ETH Dominance: 15-25%")
    print("• ETH/BTC Ratio: 0.055-0.080")
    print("• Volatility: 50-120% annual")
    print("• News Window: 3 hours (vs BTC 2 hours)")
    print("• Volume Ratio: 1.0x+ average")
    print("=" * 60)
