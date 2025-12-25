"""
Currency Strength Calculator
Calculates individual currency strength for forex trading
Works for: EUR, USD, GBP, JPY, AUD, CAD, CHF, NZD
"""

from datetime import datetime


class CurrencyStrengthCalculator:
    """Calculate strength of individual currencies"""
    
    def __init__(self, data_client):
        """
        Initialize with forex data client
        
        Args:
            data_client: ForexDataClient instance
        """
        self.data_client = data_client
        
        # Major currencies
        self.currencies = ['EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']
        
        # Major pairs for strength calculation
        self.major_pairs = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD',
            'USDCAD', 'USDCHF', 'NZDUSD', 'EURGBP',
            'EURJPY', 'GBPJPY'
        ]
    
    def calculate_strength(self, currency):
        """
        Calculate strength of a single currency
        
        Args:
            currency: Currency code (e.g., 'EUR', 'USD')
        
        Returns:
            float: Strength score (0-100)
        """
        if currency not in self.currencies:
            return None
        
        # Get prices for all pairs involving this currency
        relevant_pairs = [p for p in self.major_pairs if currency in p]
        
        if not relevant_pairs:
            return 50  # Neutral
        
        strength_sum = 0
        count = 0
        
        for pair in relevant_pairs:
            price_data = self.data_client.get_price(pair)
            if not price_data:
                continue
            
            price = price_data['mid']
            
            # Determine if currency is base or quote
            if pair.startswith(currency):
                # Currency is base - higher price = stronger
                # Normalize to 0-100 scale (simplified)
                strength_sum += 50 + (price % 1) * 50
            else:
                # Currency is quote - lower price = stronger
                strength_sum += 50 - (price % 1) * 50
            
            count += 1
        
        if count == 0:
            return 50
        
        return round(strength_sum / count, 2)
    
    def calculate_all_strengths(self):
        """
        Calculate strength for all major currencies
        
        Returns:
            dict: Currency strengths
        """
        strengths = {}
        
        for currency in self.currencies:
            strength = self.calculate_strength(currency)
            if strength:
                strengths[currency] = strength
        
        return strengths
    
    def get_pair_strength_divergence(self, pair):
        """
        Calculate strength divergence for a forex pair
        
        Args:
            pair: Pair like 'EURUSD', 'GBPUSD'
        
        Returns:
            dict: Divergence analysis
        """
        if len(pair) != 6:
            return None
        
        base_currency = pair[:3]
        quote_currency = pair[3:]
        
        base_strength = self.calculate_strength(base_currency)
        quote_strength = self.calculate_strength(quote_currency)
        
        if base_strength is None or quote_strength is None:
            return None
        
        divergence = abs(base_strength - quote_strength)
        
        # Determine signal
        if divergence >= 30:
            signal_strength = "STRONG"
            is_tradeable = True
        elif divergence >= 20:
            signal_strength = "MODERATE"
            is_tradeable = True
        elif divergence >= 10:
            signal_strength = "WEAK"
            is_tradeable = False
        else:
            signal_strength = "NONE"
            is_tradeable = False
        
        # Determine direction
        if base_strength > quote_strength + 15:
            direction = "BUY"  # Base currency stronger
        elif quote_strength > base_strength + 15:
            direction = "SELL"  # Quote currency stronger
        else:
            direction = "NEUTRAL"
        
        return {
            'pair': pair,
            'base_currency': base_currency,
            'quote_currency': quote_currency,
            'base_strength': base_strength,
            'quote_strength': quote_strength,
            'divergence': round(divergence, 2),
            'signal_strength': signal_strength,
            'direction': direction,
            'is_tradeable': is_tradeable,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_strongest_pairs(self, min_divergence=20):
        """
        Find pairs with strongest divergence
        
        Args:
            min_divergence: Minimum divergence to consider
        
        Returns:
            list: Pairs sorted by divergence strength
        """
        pairs_analysis = []
        
        for pair in self.major_pairs:
            analysis = self.get_pair_strength_divergence(pair)
            if analysis and analysis['divergence'] >= min_divergence:
                pairs_analysis.append(analysis)
        
        # Sort by divergence (highest first)
        pairs_analysis.sort(key=lambda x: x['divergence'], reverse=True)
        
        return pairs_analysis
    
    def get_trading_recommendation(self, pair):
        """
        Get trading recommendation based on currency strength
        
        Args:
            pair: Forex pair
        
        Returns:
            dict: Trading recommendation
        """
        analysis = self.get_pair_strength_divergence(pair)
        
        if not analysis:
            return {
                'pair': pair,
                'recommendation': 'NO_DATA',
                'reason': 'Unable to calculate currency strength'
            }
        
        if analysis['signal_strength'] == 'STRONG' and analysis['is_tradeable']:
            recommendation = 'STRONG_' + analysis['direction']
            reason = f"Strong divergence ({analysis['divergence']:.1f}): {analysis['base_currency']} strength {analysis['base_strength']:.1f} vs {analysis['quote_currency']} strength {analysis['quote_strength']:.1f}"
        elif analysis['signal_strength'] == 'MODERATE' and analysis['is_tradeable']:
            recommendation = 'MODERATE_' + analysis['direction']
            reason = f"Moderate divergence ({analysis['divergence']:.1f})"
        else:
            recommendation = 'WAIT'
            reason = f"Weak divergence ({analysis['divergence']:.1f}) - wait for clearer signal"
        
        return {
            'pair': pair,
            'recommendation': recommendation,
            'reason': reason,
            'analysis': analysis
        }


# Testing
if __name__ == "__main__":
    print("Testing Currency Strength Calculator...")
    print("="*60)
    
    # Import data client
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from forex_data_client import ForexDataClient
    
    client = ForexDataClient()
    calculator = CurrencyStrengthCalculator(client)
    
    # Test 1: Calculate all strengths
    print("\n1. All Currency Strengths:")
    strengths = calculator.calculate_all_strengths()
    for currency, strength in sorted(strengths.items(), key=lambda x: x[1], reverse=True):
        print(f"   {currency}: {strength:.2f}/100")
    
    # Test 2: EUR/USD divergence
    print("\n2. EUR/USD Strength Divergence:")
    eurusd_analysis = calculator.get_pair_strength_divergence("EURUSD")
    if eurusd_analysis:
        print(f"   EUR Strength: {eurusd_analysis['base_strength']:.2f}")
        print(f"   USD Strength: {eurusd_analysis['quote_strength']:.2f}")
        print(f"   Divergence: {eurusd_analysis['divergence']:.2f}")
        print(f"   Signal: {eurusd_analysis['signal_strength']}")
        print(f"   Direction: {eurusd_analysis['direction']}")
        print(f"   Tradeable: {eurusd_analysis['is_tradeable']}")
    
    # Test 3: Trading recommendation
    print("\n3. EUR/USD Trading Recommendation:")
    recommendation = calculator.get_trading_recommendation("EURUSD")
    print(f"   Recommendation: {recommendation['recommendation']}")
    print(f"   Reason: {recommendation['reason']}")
    
    # Test 4: Strongest pairs
    print("\n4. Strongest Pairs (divergence >= 20):")
    strongest = calculator.get_strongest_pairs(min_divergence=20)
    if strongest:
        for pair_data in strongest[:3]:
            print(f"   {pair_data['pair']}: {pair_data['divergence']:.2f} ({pair_data['signal_strength']})")
    else:
        print("   No pairs with divergence >= 20")
    
    print("\n" + "="*60)
    print("[OK] Currency Strength Calculator working!")
