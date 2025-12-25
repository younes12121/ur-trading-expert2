"""
Smart Money Tracking Module
Tracks COT (Commitment of Traders) data, institutional positioning, and large order tracking
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

class SmartMoneyTracker:
    """Tracks institutional and smart money activity"""
    
    def __init__(self, data_file="smart_money_data.json"):
        self.data_file = data_file
        self.smart_money_data = {
            'cot_data': {},  # Commitment of Traders data
            'institutional_positions': {},  # Institutional positioning
            'large_orders': [],  # Large order tracking
            'smart_money_bias': {},  # Bullish/bearish bias per asset
            'last_updated': None
        }
        self.load_data()
    
    def load_data(self):
        """Load smart money data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.smart_money_data = json.load(f)
            except:
                pass
    
    def save_data(self):
        """Save smart money data"""
        self.smart_money_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.data_file, 'w') as f:
            json.dump(self.smart_money_data, f, indent=2)
    
    # ============================================================================
    # COMMITMENT OF TRADERS (COT) DATA
    # ============================================================================
    
    def fetch_cot_data(self, asset: str) -> Optional[Dict]:
        """
        Fetch Commitment of Traders data (for futures markets)
        
        Note: COT data is typically available for futures contracts
        For Forex, we use positioning data from brokers/exchanges
        
        Args:
            asset: Asset symbol (e.g., 'EUR', 'GBP', 'BTC')
        
        Returns:
            COT data dict or None
        """
        # In production, this would fetch from CFTC API or broker data
        # For now, return mock/placeholder data structure
        
        # Check if we have cached data
        if asset in self.smart_money_data['cot_data']:
            cot = self.smart_money_data['cot_data'][asset]
            # Check if data is recent (within 7 days)
            try:
                last_update = datetime.strptime(cot.get('last_updated', ''), '%Y-%m-%d')
                if (datetime.now() - last_update).days < 7:
                    return cot
            except:
                pass
        
        # Mock COT data structure (would be replaced with real API call)
        cot_data = {
            'asset': asset,
            'commercial_long': 0,  # Commercial traders long positions
            'commercial_short': 0,  # Commercial traders short positions
            'non_commercial_long': 0,  # Large speculators long
            'non_commercial_short': 0,  # Large speculators short
            'non_reportable_long': 0,  # Small traders long
            'non_reportable_short': 0,  # Small traders short
            'net_position': 0,  # Net commercial position
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'mock'  # Would be 'cftc' or 'broker' in production
        }
        
        # Store
        self.smart_money_data['cot_data'][asset] = cot_data
        self.save_data()
        
        return cot_data
    
    def analyze_cot_bias(self, cot_data: Dict) -> str:
        """
        Analyze COT data to determine institutional bias
        
        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        if not cot_data:
            return 'neutral'
        
        # Commercial traders (institutions) are typically contrarian
        # If commercials are net long, it's often bearish for price (they hedge)
        # If commercials are net short, it's often bullish
        
        net_commercial = cot_data.get('commercial_long', 0) - cot_data.get('commercial_short', 0)
        net_spec = cot_data.get('non_commercial_long', 0) - cot_data.get('non_commercial_short', 0)
        
        # Large speculators (hedge funds) are trend followers
        # If they're net long, bullish; net short, bearish
        
        if abs(net_spec) > abs(net_commercial):
            # Speculators dominate
            if net_spec > 0:
                return 'bullish'
            else:
                return 'bearish'
        else:
            # Commercials dominate (contrarian signal)
            if net_commercial > 0:
                return 'bearish'  # Commercials long = price might drop
            else:
                return 'bullish'  # Commercials short = price might rise
    
    # ============================================================================
    # INSTITUTIONAL POSITIONING
    # ============================================================================
    
    def track_institutional_positioning(self, asset: str, positioning_data: Dict) -> Dict:
        """
        Track institutional positioning
        
        Args:
            asset: Asset symbol
            positioning_data: Dict with long/short positioning info
        
        Returns:
            Positioning analysis
        """
        positioning = {
            'asset': asset,
            'institutional_long_pct': positioning_data.get('institutional_long', 0),
            'institutional_short_pct': positioning_data.get('institutional_short', 0),
            'retail_long_pct': positioning_data.get('retail_long', 0),
            'retail_short_pct': positioning_data.get('retail_short', 0),
            'net_institutional': positioning_data.get('institutional_long', 0) - positioning_data.get('institutional_short', 0),
            'net_retail': positioning_data.get('retail_long', 0) - positioning_data.get('retail_short', 0),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Determine bias
        if positioning['net_institutional'] > 20:
            bias = 'bullish'
        elif positioning['net_institutional'] < -20:
            bias = 'bearish'
        else:
            bias = 'neutral'
        
        positioning['bias'] = bias
        
        # Store
        self.smart_money_data['institutional_positions'][asset] = positioning
        self.smart_money_data['smart_money_bias'][asset] = bias
        self.save_data()
        
        return positioning
    
    # ============================================================================
    # LARGE ORDER TRACKING
    # ============================================================================
    
    def track_large_order(self, asset: str, order_data: Dict):
        """
        Track large institutional orders
        
        Args:
            asset: Asset symbol
            order_data: Dict with order details (size, price, direction, etc.)
        """
        large_order = {
            'asset': asset,
            'size': order_data.get('size', 0),
            'value': order_data.get('value', 0),
            'price': order_data.get('price', 0),
            'direction': order_data.get('direction', 'unknown'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': order_data.get('source', 'unknown')
        }
        
        # Store
        self.smart_money_data['large_orders'].append(large_order)
        # Keep last 200 orders
        self.smart_money_data['large_orders'] = self.smart_money_data['large_orders'][-200:]
        self.save_data()
    
    def get_recent_large_orders(self, asset: str, hours: int = 24) -> List[Dict]:
        """Get recent large orders for an asset"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = [
            order for order in self.smart_money_data['large_orders']
            if order['asset'] == asset and 
            datetime.strptime(order['timestamp'], '%Y-%m-%d %H:%M:%S') > cutoff
        ]
        
        return sorted(recent, key=lambda x: x['value'], reverse=True)
    
    # ============================================================================
    # ANALYSIS & REPORTING
    # ============================================================================
    
    def analyze_smart_money(self, asset: str, positioning_data: Optional[Dict] = None) -> Dict:
        """
        Complete smart money analysis
        
        Args:
            asset: Asset symbol
            positioning_data: Optional positioning data
        
        Returns:
            Complete analysis
        """
        # Fetch COT data
        cot_data = self.fetch_cot_data(asset)
        cot_bias = self.analyze_cot_bias(cot_data) if cot_data else 'neutral'
        
        # Track institutional positioning
        institutional = None
        if positioning_data:
            institutional = self.track_institutional_positioning(asset, positioning_data)
        elif asset in self.smart_money_data['institutional_positions']:
            institutional = self.smart_money_data['institutional_positions'][asset]
        
        # Get recent large orders
        large_orders = self.get_recent_large_orders(asset, hours=24)
        
        # Determine overall bias
        biases = []
        if cot_bias != 'neutral':
            biases.append(cot_bias)
        if institutional and institutional['bias'] != 'neutral':
            biases.append(institutional['bias'])
        
        if biases:
            # Majority vote
            overall_bias = max(set(biases), key=biases.count)
        else:
            overall_bias = 'neutral'
        
        return {
            'asset': asset,
            'cot_data': cot_data,
            'cot_bias': cot_bias,
            'institutional_positioning': institutional,
            'recent_large_orders': large_orders[:10],  # Top 10
            'total_large_orders_24h': len(large_orders),
            'overall_bias': overall_bias,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def format_analysis_message(self, analysis: Dict) -> str:
        """Format analysis as Telegram message"""
        msg = f"💰 **SMART MONEY ANALYSIS - {analysis['asset']}**\n\n"
        
        # Overall bias
        bias_emoji = {'bullish': '🟢', 'bearish': '🔴', 'neutral': '⚪'}
        emoji = bias_emoji.get(analysis['overall_bias'], '⚪')
        msg += f"{emoji} *Institutional Bias:* {analysis['overall_bias'].upper()}\n\n"
        
        # COT Data
        if analysis['cot_data']:
            cot = analysis['cot_data']
            msg += f"📊 *Commitment of Traders:*\n"
            msg += f"Commercial Net: {cot.get('net_position', 0):+,}\n"
            msg += f"COT Bias: {analysis['cot_bias'].upper()}\n\n"
        
        # Institutional Positioning
        if analysis['institutional_positioning']:
            inst = analysis['institutional_positioning']
            msg += f"🏦 *Institutional Positioning:*\n"
            msg += f"Long: {inst['institutional_long_pct']:.1f}%\n"
            msg += f"Short: {inst['institutional_short_pct']:.1f}%\n"
            msg += f"Net: {inst['net_institutional']:+.1f}%\n"
            msg += f"Bias: {inst['bias'].upper()}\n\n"
        
        # Large Orders
        if analysis['recent_large_orders']:
            msg += f"📈 *Large Orders (24h):* {analysis['total_large_orders_24h']}\n"
            for order in analysis['recent_large_orders'][:3]:
                direction_emoji = "🟢" if order['direction'] == 'buy' else "🔴"
                msg += f"{direction_emoji} ${order['value']:,.0f} @ ${order['price']:,.2f}\n"
            msg += "\n"
        
        msg += f"⏰ Updated: {analysis['timestamp']}"
        
        return msg


if __name__ == "__main__":
    # Test smart money tracker
    tracker = SmartMoneyTracker()
    
    # Mock positioning data
    positioning = {
        'institutional_long': 65,
        'institutional_short': 35,
        'retail_long': 40,
        'retail_short': 60
    }
    
    analysis = tracker.analyze_smart_money('EUR', positioning)
    print(tracker.format_analysis_message(analysis))

