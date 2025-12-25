"""
Volume Profile Analysis Module
Analyzes volume at different price levels to identify POC, HVN, LVN, and Value Area
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from collections import defaultdict

class VolumeProfileAnalyzer:
    """Analyzes volume profile to identify key price levels"""
    
    def __init__(self, data_file="volume_profile_data.json"):
        self.data_file = data_file
        self.profile_data = {
            'profiles': {},  # {pair: {price_levels: {price: volume}}}
            'poc_levels': {},  # Point of Control (highest volume price)
            'value_areas': {},  # Value Area High/Low
            'hvn_levels': {},  # High Volume Nodes
            'lvn_levels': {},  # Low Volume Nodes
            'last_updated': None
        }
        self.load_data()
        
        # Parameters
        self.value_area_percent = 0.70  # 70% of volume in value area
        self.hvn_threshold = 0.8  # 80% of max volume for HVN
        self.lvn_threshold = 0.2  # 20% of max volume for LVN
    
    def load_data(self):
        """Load volume profile data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.profile_data = json.load(f)
            except:
                pass
    
    def save_data(self):
        """Save volume profile data"""
        self.profile_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.data_file, 'w') as f:
            json.dump(self.profile_data, f, indent=2)
    
    # ============================================================================
    # VOLUME PROFILE CALCULATION
    # ============================================================================
    
    def build_volume_profile(self, pair: str, price_volume_data: List[Dict]) -> Dict:
        """
        Build volume profile from price-volume data
        
        Args:
            pair: Trading pair
            price_volume_data: List of {price, volume} dicts
        
        Returns:
            Volume profile dict
        """
        if not price_volume_data:
            return {}
        
        # Aggregate volume by price level
        price_volumes = defaultdict(float)
        for data_point in price_volume_data:
            price = data_point.get('price', 0)
            volume = data_point.get('volume', 0)
            price_volumes[price] += volume
        
        # Convert to sorted list
        profile = dict(sorted(price_volumes.items()))
        
        # Store profile
        self.profile_data['profiles'][pair] = profile
        self.save_data()
        
        return profile
    
    # ============================================================================
    # POINT OF CONTROL (POC)
    # ============================================================================
    
    def calculate_poc(self, pair: str, profile: Optional[Dict] = None) -> Optional[float]:
        """
        Calculate Point of Control (price level with highest volume)
        
        Args:
            pair: Trading pair
            profile: Optional volume profile (if None, uses stored)
        
        Returns:
            POC price level or None
        """
        if profile is None:
            profile = self.profile_data['profiles'].get(pair, {})
        
        if not profile:
            return None
        
        # Find price with maximum volume
        poc_price = max(profile.items(), key=lambda x: x[1])[0]
        poc_volume = profile[poc_price]
        
        # Store
        self.profile_data['poc_levels'][pair] = {
            'price': poc_price,
            'volume': poc_volume,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_data()
        
        return poc_price
    
    # ============================================================================
    # VALUE AREA
    # ============================================================================
    
    def calculate_value_area(self, pair: str, profile: Optional[Dict] = None) -> Optional[Dict]:
        """
        Calculate Value Area (price range containing 70% of volume)
        
        Args:
            pair: Trading pair
            profile: Optional volume profile
        
        Returns:
            Dict with value_area_high, value_area_low, poc
        """
        if profile is None:
            profile = self.profile_data['profiles'].get(pair, {})
        
        if not profile:
            return None
        
        # Sort by price
        sorted_prices = sorted(profile.items())
        total_volume = sum(profile.values())
        target_volume = total_volume * self.value_area_percent
        
        # Start from POC and expand outward
        poc_price = self.calculate_poc(pair, profile)
        poc_index = next(i for i, (p, v) in enumerate(sorted_prices) if p == poc_price)
        
        # Expand upward and downward from POC
        accumulated_volume = profile[poc_price]
        upper_index = poc_index
        lower_index = poc_index
        
        while accumulated_volume < target_volume:
            # Check which direction has more volume available
            upper_available = upper_index < len(sorted_prices) - 1
            lower_available = lower_index > 0
            
            if not upper_available and not lower_available:
                break
            
            upper_volume = sorted_prices[upper_index + 1][1] if upper_available else 0
            lower_volume = sorted_prices[lower_index - 1][1] if lower_available else 0
            
            if upper_volume >= lower_volume and upper_available:
                upper_index += 1
                accumulated_volume += upper_volume
            elif lower_available:
                lower_index -= 1
                accumulated_volume += lower_volume
        
        value_area_high = sorted_prices[upper_index][0]
        value_area_low = sorted_prices[lower_index][0]
        
        result = {
            'value_area_high': value_area_high,
            'value_area_low': value_area_low,
            'poc': poc_price,
            'volume_percent': (accumulated_volume / total_volume) * 100,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store
        self.profile_data['value_areas'][pair] = result
        self.save_data()
        
        return result
    
    # ============================================================================
    # HIGH/LOW VOLUME NODES
    # ============================================================================
    
    def identify_hvn_lvn(self, pair: str, profile: Optional[Dict] = None) -> Dict:
        """
        Identify High Volume Nodes (HVN) and Low Volume Nodes (LVN)
        
        Args:
            pair: Trading pair
            profile: Optional volume profile
        
        Returns:
            Dict with hvn and lvn lists
        """
        if profile is None:
            profile = self.profile_data['profiles'].get(pair, {})
        
        if not profile:
            return {'hvn': [], 'lvn': []}
        
        max_volume = max(profile.values())
        min_volume = min(profile.values())
        volume_range = max_volume - min_volume
        
        hvn = []
        lvn = []
        
        for price, volume in profile.items():
            # Normalize volume (0-1 scale)
            normalized = (volume - min_volume) / volume_range if volume_range > 0 else 0.5
            
            if normalized >= self.hvn_threshold:
                hvn.append({
                    'price': price,
                    'volume': volume,
                    'normalized': normalized
                })
            elif normalized <= self.lvn_threshold:
                lvn.append({
                    'price': price,
                    'volume': volume,
                    'normalized': normalized
                })
        
        # Sort by volume
        hvn.sort(key=lambda x: x['volume'], reverse=True)
        lvn.sort(key=lambda x: x['volume'])
        
        # Store
        self.profile_data['hvn_levels'][pair] = hvn[:10]  # Top 10
        self.profile_data['lvn_levels'][pair] = lvn[:10]  # Top 10
        self.save_data()
        
        return {'hvn': hvn[:10], 'lvn': lvn[:10]}
    
    # ============================================================================
    # ANALYSIS & REPORTING
    # ============================================================================
    
    def analyze_volume_profile(self, pair: str, price_volume_data: List[Dict]) -> Dict:
        """
        Complete volume profile analysis
        
        Args:
            pair: Trading pair
            price_volume_data: Price-volume data points
        
        Returns:
            Complete analysis
        """
        # Build profile
        profile = self.build_volume_profile(pair, price_volume_data)
        
        if not profile:
            return {
                'pair': pair,
                'error': 'No data available',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        # Calculate POC
        poc = self.calculate_poc(pair, profile)
        
        # Calculate Value Area
        value_area = self.calculate_value_area(pair, profile)
        
        # Identify HVN/LVN
        nodes = self.identify_hvn_lvn(pair, profile)
        
        # Get current price (from latest data point)
        current_price = price_volume_data[-1]['price'] if price_volume_data else None
        
        return {
            'pair': pair,
            'current_price': current_price,
            'poc': poc,
            'poc_volume': profile.get(poc, 0) if poc else 0,
            'value_area': value_area,
            'hvn': nodes['hvn'],
            'lvn': nodes['lvn'],
            'total_price_levels': len(profile),
            'total_volume': sum(profile.values()),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def format_analysis_message(self, analysis: Dict) -> str:
        """Format analysis as Telegram message"""
        if 'error' in analysis:
            return f"❌ **Volume Profile Analysis - {analysis['pair']}**\n\n{analysis['error']}"
        
        msg = f"📊 **VOLUME PROFILE - {analysis['pair']}**\n\n"
        
        if analysis['current_price']:
            msg += f"*Current Price:* ${analysis['current_price']:,.2f}\n\n"
        
        # POC
        if analysis['poc']:
            msg += f"🎯 *Point of Control (POC):*\n"
            msg += f"Price: ${analysis['poc']:,.2f}\n"
            msg += f"Volume: {analysis['poc_volume']:,.0f}\n\n"
        
        # Value Area
        if analysis['value_area']:
            va = analysis['value_area']
            msg += f"📈 *Value Area (70% volume):*\n"
            msg += f"High: ${va['value_area_high']:,.2f}\n"
            msg += f"Low: ${va['value_area_low']:,.2f}\n"
            msg += f"POC: ${va['poc']:,.2f}\n"
            msg += f"Coverage: {va['volume_percent']:.1f}%\n\n"
        
        # HVN
        if analysis['hvn']:
            msg += f"🟢 *High Volume Nodes (HVN):*\n"
            for hvn in analysis['hvn'][:5]:
                msg += f"• ${hvn['price']:,.2f} (Vol: {hvn['volume']:,.0f})\n"
            msg += "\n"
        
        # LVN
        if analysis['lvn']:
            msg += f"🔴 *Low Volume Nodes (LVN):*\n"
            for lvn in analysis['lvn'][:5]:
                msg += f"• ${lvn['price']:,.2f} (Vol: {lvn['volume']:,.0f})\n"
            msg += "\n"
        
        msg += f"*Total Levels:* {analysis['total_price_levels']}\n"
        msg += f"*Total Volume:* {analysis['total_volume']:,.0f}\n\n"
        msg += f"⏰ Updated: {analysis['timestamp']}"
        
        return msg


if __name__ == "__main__":
    # Test volume profile analyzer
    analyzer = VolumeProfileAnalyzer()
    
    # Mock price-volume data
    price_volume_data = [
        {'price': 50000, 'volume': 1000000},
        {'price': 50010, 'volume': 800000},
        {'price': 50020, 'volume': 1200000},  # High volume
        {'price': 50030, 'volume': 600000},
        {'price': 50040, 'volume': 500000},
    ]
    
    analysis = analyzer.analyze_volume_profile('BTC', price_volume_data)
    print(analyzer.format_analysis_message(analysis))

