"""
Order Flow Analysis Module
Analyzes order flow data to detect large orders, unusual volume, and institutional activity
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np

class OrderFlowAnalyzer:
    """Analyzes order flow to detect institutional activity and large orders"""
    
    def __init__(self, data_file="order_flow_data.json"):
        self.data_file = data_file
        self.order_flow_data = {
            'large_orders': [],  # Track large orders
            'unusual_volume': [],  # Track unusual volume spikes
            'institutional_activity': [],  # Track institutional patterns
            'last_updated': None
        }
        self.load_data()
        
        # Thresholds for detection
        self.large_order_threshold = 100000  # $100k+ orders
        self.volume_spike_threshold = 2.0  # 2x average volume
        self.institutional_pattern_threshold = 500000  # $500k+ cumulative
    
    def load_data(self):
        """Load order flow data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.order_flow_data = json.load(f)
            except:
                pass
    
    def save_data(self):
        """Save order flow data"""
        self.order_flow_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.data_file, 'w') as f:
            json.dump(self.order_flow_data, f, indent=2)
    
    # ============================================================================
    # LARGE ORDER DETECTION
    # ============================================================================
    
    def detect_large_orders(self, pair: str, order_book_data: Dict) -> List[Dict]:
        """
        Detect large orders in order book
        
        Args:
            pair: Trading pair
            order_book_data: Dict with bids/asks and sizes
        
        Returns:
            List of large orders detected
        """
        large_orders = []
        
        # Analyze bids (buy orders)
        if 'bids' in order_book_data:
            for bid in order_book_data['bids'][:10]:  # Top 10 levels
                price, size = bid[0], bid[1]
                order_value = price * size
                
                if order_value >= self.large_order_threshold:
                    large_orders.append({
                        'type': 'buy',
                        'price': price,
                        'size': size,
                        'value': order_value,
                        'pair': pair,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        # Analyze asks (sell orders)
        if 'asks' in order_book_data:
            for ask in order_book_data['asks'][:10]:  # Top 10 levels
                price, size = ask[0], ask[1]
                order_value = price * size
                
                if order_value >= self.large_order_threshold:
                    large_orders.append({
                        'type': 'sell',
                        'price': price,
                        'size': size,
                        'value': order_value,
                        'pair': pair,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        # Store for tracking
        if large_orders:
            self.order_flow_data['large_orders'].extend(large_orders)
            # Keep only last 100
            self.order_flow_data['large_orders'] = self.order_flow_data['large_orders'][-100:]
            self.save_data()
        
        return large_orders
    
    # ============================================================================
    # UNUSUAL VOLUME DETECTION
    # ============================================================================
    
    def detect_unusual_volume(self, pair: str, current_volume: float, avg_volume: float) -> Optional[Dict]:
        """
        Detect unusual volume spikes
        
        Args:
            pair: Trading pair
            current_volume: Current volume
            avg_volume: Average volume (last 24h)
        
        Returns:
            Alert dict if unusual volume detected, None otherwise
        """
        if avg_volume == 0:
            return None
        
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio >= self.volume_spike_threshold:
            alert = {
                'pair': pair,
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'ratio': volume_ratio,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'severity': 'high' if volume_ratio >= 3.0 else 'medium'
            }
            
            # Store for tracking
            self.order_flow_data['unusual_volume'].append(alert)
            self.order_flow_data['unusual_volume'] = self.order_flow_data['unusual_volume'][-50:]
            self.save_data()
            
            return alert
        
        return None
    
    # ============================================================================
    # INSTITUTIONAL ACTIVITY TRACKING
    # ============================================================================
    
    def track_institutional_activity(self, pair: str, recent_orders: List[Dict]) -> Dict:
        """
        Track institutional activity patterns
        
        Args:
            pair: Trading pair
            recent_orders: List of recent large orders
        
        Returns:
            Analysis of institutional activity
        """
        if not recent_orders:
            return {
                'has_activity': False,
                'bias': 'neutral',
                'total_value': 0,
                'buy_value': 0,
                'sell_value': 0
            }
        
        # Calculate totals
        buy_value = sum(o['value'] for o in recent_orders if o['type'] == 'buy')
        sell_value = sum(o['value'] for o in recent_orders if o['type'] == 'sell')
        total_value = buy_value + sell_value
        
        # Determine bias
        if total_value >= self.institutional_pattern_threshold:
            if buy_value > sell_value * 1.5:
                bias = 'bullish'
            elif sell_value > buy_value * 1.5:
                bias = 'bearish'
            else:
                bias = 'neutral'
            
            activity = {
                'has_activity': True,
                'bias': bias,
                'total_value': total_value,
                'buy_value': buy_value,
                'sell_value': sell_value,
                'pair': pair,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Store for tracking
            self.order_flow_data['institutional_activity'].append(activity)
            self.order_flow_data['institutional_activity'] = self.order_flow_data['institutional_activity'][-50:]
            self.save_data()
            
            return activity
        
        return {
            'has_activity': False,
            'bias': 'neutral',
            'total_value': total_value,
            'buy_value': buy_value,
            'sell_value': sell_value
        }
    
    # ============================================================================
    # ANALYSIS & REPORTING
    # ============================================================================
    
    def analyze_order_flow(self, pair: str, order_book_data: Dict, volume_data: Dict) -> Dict:
        """
        Complete order flow analysis
        
        Args:
            pair: Trading pair
            order_book_data: Order book data
            volume_data: Dict with current_volume and avg_volume
        
        Returns:
            Complete analysis report
        """
        # Detect large orders
        large_orders = self.detect_large_orders(pair, order_book_data)
        
        # Detect unusual volume
        unusual_volume = None
        if 'current_volume' in volume_data and 'avg_volume' in volume_data:
            unusual_volume = self.detect_unusual_volume(
                pair, 
                volume_data['current_volume'], 
                volume_data['avg_volume']
            )
        
        # Track institutional activity
        institutional = self.track_institutional_activity(pair, large_orders)
        
        # Calculate order flow imbalance
        buy_pressure = sum(o['value'] for o in large_orders if o['type'] == 'buy')
        sell_pressure = sum(o['value'] for o in large_orders if o['type'] == 'sell')
        imbalance = (buy_pressure - sell_pressure) / (buy_pressure + sell_pressure) if (buy_pressure + sell_pressure) > 0 else 0
        
        return {
            'pair': pair,
            'large_orders_count': len(large_orders),
            'large_orders': large_orders[:5],  # Top 5
            'unusual_volume': unusual_volume,
            'institutional_activity': institutional,
            'order_flow_imbalance': imbalance,
            'buy_pressure': buy_pressure,
            'sell_pressure': sell_pressure,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def format_analysis_message(self, analysis: Dict) -> str:
        """Format analysis as Telegram message"""
        msg = f"📊 **ORDER FLOW ANALYSIS - {analysis['pair']}**\n\n"
        
        # Large orders
        if analysis['large_orders_count'] > 0:
            msg += f"🔍 *Large Orders Detected:* {analysis['large_orders_count']}\n"
            for order in analysis['large_orders'][:3]:
                emoji = "🟢" if order['type'] == 'buy' else "🔴"
                msg += f"{emoji} {order['type'].upper()}: ${order['value']:,.0f} @ ${order['price']:,.2f}\n"
            msg += "\n"
        else:
            msg += "🔍 *Large Orders:* None detected\n\n"
        
        # Unusual volume
        if analysis['unusual_volume']:
            uv = analysis['unusual_volume']
            severity_emoji = "🚨" if uv['severity'] == 'high' else "⚠️"
            msg += f"{severity_emoji} *Unusual Volume:* {uv['ratio']:.1f}x average\n"
            msg += f"Current: {uv['current_volume']:,.0f} | Avg: {uv['avg_volume']:,.0f}\n\n"
        
        # Institutional activity
        inst = analysis['institutional_activity']
        if inst['has_activity']:
            bias_emoji = "🟢" if inst['bias'] == 'bullish' else "🔴" if inst['bias'] == 'bearish' else "⚪"
            msg += f"{bias_emoji} *Institutional Bias:* {inst['bias'].upper()}\n"
            msg += f"Total Activity: ${inst['total_value']:,.0f}\n"
            msg += f"Buy: ${inst['buy_value']:,.0f} | Sell: ${inst['sell_value']:,.0f}\n\n"
        
        # Order flow imbalance
        imbalance = analysis['order_flow_imbalance']
        if abs(imbalance) > 0.3:
            direction = "BUY" if imbalance > 0 else "SELL"
            msg += f"⚖️ *Order Flow Imbalance:* {direction} pressure ({imbalance*100:.1f}%)\n"
        
        msg += f"\n⏰ Updated: {analysis['timestamp']}"
        
        return msg
    
    def get_recent_activity(self, pair: str, hours: int = 24) -> Dict:
        """Get recent order flow activity for a pair"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Filter by pair and time
        large_orders = [
            o for o in self.order_flow_data['large_orders']
            if o['pair'] == pair and datetime.strptime(o['timestamp'], '%Y-%m-%d %H:%M:%S') > cutoff
        ]
        
        unusual_volume = [
            uv for uv in self.order_flow_data['unusual_volume']
            if uv['pair'] == pair and datetime.strptime(uv['timestamp'], '%Y-%m-%d %H:%M:%S') > cutoff
        ]
        
        institutional = [
            inst for inst in self.order_flow_data['institutional_activity']
            if inst['pair'] == pair and datetime.strptime(inst['timestamp'], '%Y-%m-%d %H:%M:%S') > cutoff
        ]
        
        return {
            'large_orders': large_orders,
            'unusual_volume': unusual_volume,
            'institutional_activity': institutional,
            'period_hours': hours
        }


if __name__ == "__main__":
    # Test order flow analyzer
    analyzer = OrderFlowAnalyzer()
    
    # Mock order book data
    order_book = {
        'bids': [[50000, 2.5], [49999, 1.0], [49998, 0.5]],
        'asks': [[50001, 1.5], [50002, 2.0], [50003, 0.8]]
    }
    
    volume_data = {
        'current_volume': 5000000,
        'avg_volume': 2000000
    }
    
    analysis = analyzer.analyze_order_flow('BTC', order_book, volume_data)
    print(analyzer.format_analysis_message(analysis))

