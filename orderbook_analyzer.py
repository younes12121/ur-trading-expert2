"""
Order Book Analyzer - Similar to Bookmap
Analyzes order book depth, liquidity, and imbalances for BTC and Gold
"""

import requests
from datetime import datetime


class OrderBookAnalyzer:
    """Analyze order book data similar to Bookmap"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.futures_url = "https://fapi.binance.com/fapi/v1"
    
    def get_order_book(self, symbol, limit=100):
        """Get order book depth"""
        try:
            url = f"{self.base_url}/depth"
            params = {'symbol': symbol, 'limit': limit}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching order book for {symbol}: {e}")
            return None
    
    def analyze_liquidity(self, order_book, current_price):
        """Analyze liquidity levels"""
        if not order_book:
            return None
        
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        # Calculate total liquidity
        total_bid_volume = sum(float(bid[1]) for bid in bids)
        total_ask_volume = sum(float(ask[1]) for ask in asks)
        
        # Calculate liquidity at different levels
        bid_levels = self._calculate_levels(bids, current_price, 'bid')
        ask_levels = self._calculate_levels(asks, current_price, 'ask')
        
        # Find walls (large orders)
        bid_walls = self._find_walls(bids, 'bid')
        ask_walls = self._find_walls(asks, 'ask')
        
        return {
            'total_bid_volume': total_bid_volume,
            'total_ask_volume': total_ask_volume,
            'bid_ask_ratio': total_bid_volume / total_ask_volume if total_ask_volume > 0 else 0,
            'bid_levels': bid_levels,
            'ask_levels': ask_levels,
            'bid_walls': bid_walls,
            'ask_walls': ask_walls,
            'imbalance': (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume) * 100
        }
    
    def _calculate_levels(self, orders, current_price, side):
        """Calculate liquidity at different price levels"""
        levels = {
            '0.1%': 0,
            '0.5%': 0,
            '1.0%': 0,
            '2.0%': 0
        }
        
        for price_str, volume_str in orders:
            price = float(price_str)
            volume = float(volume_str)
            
            pct_diff = abs((price - current_price) / current_price * 100)
            
            if pct_diff <= 0.1:
                levels['0.1%'] += volume
            if pct_diff <= 0.5:
                levels['0.5%'] += volume
            if pct_diff <= 1.0:
                levels['1.0%'] += volume
            if pct_diff <= 2.0:
                levels['2.0%'] += volume
        
        return levels
    
    def _find_walls(self, orders, side, threshold_multiplier=3):
        """Find large orders (walls)"""
        if not orders:
            return []
        
        volumes = [float(order[1]) for order in orders]
        avg_volume = sum(volumes) / len(volumes)
        threshold = avg_volume * threshold_multiplier
        
        walls = []
        for price_str, volume_str in orders[:20]:  # Check top 20 levels
            volume = float(volume_str)
            if volume >= threshold:
                walls.append({
                    'price': float(price_str),
                    'volume': volume,
                    'side': side
                })
        
        return walls
    
    def print_order_book_analysis(self, symbol, asset_name):
        """Print complete order book analysis"""
        print(f"\n{'='*100}")
        print(f"{asset_name} ORDER BOOK ANALYSIS (Bookmap-style)")
        print(f"Symbol: {symbol}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CET')}")
        print(f"{'='*100}")
        
        # Get order book
        order_book = self.get_order_book(symbol)
        if not order_book:
            print(f"[ERROR] Could not fetch order book for {symbol}")
            return
        
        # Get current price
        try:
            ticker_url = f"{self.base_url}/ticker/price"
            response = requests.get(ticker_url, params={'symbol': symbol}, timeout=10)
            current_price = float(response.json()['price'])
        except:
            current_price = float(order_book['bids'][0][0])
        
        # Analyze
        analysis = self.analyze_liquidity(order_book, current_price)
        
        # Print summary table
        print(f"\n{'-'*100}")
        print(f"{'METRIC':<30} | {'VALUE':<65}")
        print(f"{'-'*100}")
        print(f"{'Current Price':<30} | ${current_price:,.2f}")
        print(f"{'Total Bid Volume':<30} | {analysis['total_bid_volume']:,.4f}")
        print(f"{'Total Ask Volume':<30} | {analysis['total_ask_volume']:,.4f}")
        print(f"{'Bid/Ask Ratio':<30} | {analysis['bid_ask_ratio']:.2f}")
        print(f"{'Order Book Imbalance':<30} | {analysis['imbalance']:+.2f}% ({'BUY PRESSURE' if analysis['imbalance'] > 0 else 'SELL PRESSURE'})")
        print(f"{'-'*100}")
        
        # Liquidity levels
        print(f"\n{'-'*100}")
        print(f"LIQUIDITY AT DIFFERENT LEVELS")
        print(f"{'-'*100}")
        print(f"{'DISTANCE':<20} | {'BID LIQUIDITY':<35} | {'ASK LIQUIDITY':<35}")
        print(f"{'-'*100}")
        
        for level in ['0.1%', '0.5%', '1.0%', '2.0%']:
            bid_liq = analysis['bid_levels'][level]
            ask_liq = analysis['ask_levels'][level]
            print(f"{'Within ' + level:<20} | {bid_liq:>15,.4f} | {ask_liq:>15,.4f}")
        
        print(f"{'-'*100}")
        
        # Walls
        if analysis['bid_walls'] or analysis['ask_walls']:
            print(f"\n{'-'*100}")
            print(f"LARGE ORDERS (WALLS) - Top Support/Resistance")
            print(f"{'-'*100}")
            print(f"{'SIDE':<10} | {'PRICE':<20} | {'VOLUME':<30} | {'DISTANCE FROM CURRENT':<30}")
            print(f"{'-'*100}")
            
            # Bid walls (support)
            for wall in analysis['bid_walls'][:5]:
                distance = ((current_price - wall['price']) / current_price) * 100
                print(f"{'BID':<10} | ${wall['price']:>18,.2f} | {wall['volume']:>28,.4f} | {distance:>28.2f}% below")
            
            # Ask walls (resistance)
            for wall in analysis['ask_walls'][:5]:
                distance = ((wall['price'] - current_price) / current_price) * 100
                print(f"{'ASK':<10} | ${wall['price']:>18,.2f} | {wall['volume']:>28,.4f} | {distance:>28.2f}% above")
            
            print(f"{'-'*100}")
        
        # Interpretation
        print(f"\n{'-'*100}")
        print(f"INTERPRETATION")
        print(f"{'-'*100}")
        
        if analysis['imbalance'] > 10:
            print(f"[BULLISH] Strong buy pressure ({analysis['imbalance']:.1f}% imbalance)")
            print(f"   - More bids than asks in order book")
            print(f"   - Potential upward price movement")
        elif analysis['imbalance'] < -10:
            print(f"[BEARISH] Strong sell pressure ({analysis['imbalance']:.1f}% imbalance)")
            print(f"   - More asks than bids in order book")
            print(f"   - Potential downward price movement")
        else:
            print(f"[NEUTRAL] Balanced order book ({analysis['imbalance']:.1f}% imbalance)")
            print(f"   - Roughly equal buy and sell pressure")
        
        if analysis['bid_walls']:
            print(f"\n[SUPPORT] {len(analysis['bid_walls'])} large bid walls detected")
            print(f"   - Strongest support at ${analysis['bid_walls'][0]['price']:,.2f}")
        
        if analysis['ask_walls']:
            print(f"\n[RESISTANCE] {len(analysis['ask_walls'])} large ask walls detected")
            print(f"   - Strongest resistance at ${analysis['ask_walls'][0]['price']:,.2f}")
        
        print(f"{'-'*100}\n")


def main():
    """Main function"""
    analyzer = OrderBookAnalyzer()
    
    print("\n" + "="*100)
    print("ORDER BOOK ANALYZER - BTC & GOLD")
    print("Similar to Bookmap - Free Binance Data")
    print("="*100)
    
    # Analyze BTC
    analyzer.print_order_book_analysis('BTCUSDT', 'BITCOIN (BTC/USDT)')
    
    # Analyze Gold (PAXG - tokenized gold)
    analyzer.print_order_book_analysis('PAXGUSDT', 'GOLD (PAXG/USDT)')
    
    print("\n[DONE] Order book analysis complete!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
