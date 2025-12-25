"""
Market Maker Zones Module
Identifies key price levels (demand/supply zones), tracks stop loss clusters, and predicts liquidity grabs
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

class MarketMakerZones:
    """Identifies market maker zones and liquidity levels"""
    
    def __init__(self, data_file="market_maker_zones.json"):
        self.data_file = data_file
        self.zones_data = {
            'demand_zones': [],  # Support zones (buying interest)
            'supply_zones': [],  # Resistance zones (selling interest)
            'stop_clusters': [],  # Areas with many stop losses
            'liquidity_zones': [],  # Areas likely to be targeted for liquidity grabs
            'last_updated': None
        }
        self.load_data()
        
        # Zone parameters
        self.zone_strength_threshold = 0.7  # Minimum strength to be considered
        self.cluster_proximity = 0.001  # 0.1% price proximity for clustering
    
    def load_data(self):
        """Load market maker zones data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.zones_data = json.load(f)
            except:
                pass
    
    def save_data(self):
        """Save market maker zones data"""
        self.zones_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.data_file, 'w') as f:
            json.dump(self.zones_data, f, indent=2)
    
    # ============================================================================
    # DEMAND/SUPPLY ZONE IDENTIFICATION
    # ============================================================================
    
    def identify_demand_zone(self, pair: str, price_data: List[Dict]) -> Optional[Dict]:
        """
        Identify demand zone (support level with buying interest)
        
        Args:
            pair: Trading pair
            price_data: List of price points with volume/activity
        
        Returns:
            Demand zone dict if found
        """
        if not price_data or len(price_data) < 3:
            return None
        
        # Find price levels with high buying activity
        buy_levels = []
        for point in price_data:
            if 'buy_volume' in point and point['buy_volume'] > 0:
                buy_levels.append({
                    'price': point['price'],
                    'volume': point['buy_volume'],
                    'strength': point.get('strength', 0.5)
                })
        
        if not buy_levels:
            return None
        
        # Cluster nearby levels
        clusters = self._cluster_price_levels(buy_levels)
        
        # Find strongest cluster
        strongest = max(clusters, key=lambda c: c['total_volume'], default=None)
        
        if strongest and strongest['total_volume'] >= self.zone_strength_threshold:
            zone = {
                'pair': pair,
                'type': 'demand',
                'price_range': (strongest['min_price'], strongest['max_price']),
                'center_price': strongest['center_price'],
                'strength': strongest['total_volume'],
                'volume': strongest['total_volume'],
                'identified_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'active'
            }
            
            # Store zone
            self.zones_data['demand_zones'].append(zone)
            self.zones_data['demand_zones'] = self.zones_data['demand_zones'][-100:]
            self.save_data()
            
            return zone
        
        return None
    
    def identify_supply_zone(self, pair: str, price_data: List[Dict]) -> Optional[Dict]:
        """
        Identify supply zone (resistance level with selling interest)
        
        Args:
            pair: Trading pair
            price_data: List of price points with volume/activity
        
        Returns:
            Supply zone dict if found
        """
        if not price_data or len(price_data) < 3:
            return None
        
        # Find price levels with high selling activity
        sell_levels = []
        for point in price_data:
            if 'sell_volume' in point and point['sell_volume'] > 0:
                sell_levels.append({
                    'price': point['price'],
                    'volume': point['sell_volume'],
                    'strength': point.get('strength', 0.5)
                })
        
        if not sell_levels:
            return None
        
        # Cluster nearby levels
        clusters = self._cluster_price_levels(sell_levels)
        
        # Find strongest cluster
        strongest = max(clusters, key=lambda c: c['total_volume'], default=None)
        
        if strongest and strongest['total_volume'] >= self.zone_strength_threshold:
            zone = {
                'pair': pair,
                'type': 'supply',
                'price_range': (strongest['min_price'], strongest['max_price']),
                'center_price': strongest['center_price'],
                'strength': strongest['total_volume'],
                'volume': strongest['total_volume'],
                'identified_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'active'
            }
            
            # Store zone
            self.zones_data['supply_zones'].append(zone)
            self.zones_data['supply_zones'] = self.zones_data['supply_zones'][-100:]
            self.save_data()
            
            return zone
        
        return None
    
    def _cluster_price_levels(self, levels: List[Dict]) -> List[Dict]:
        """Cluster price levels that are close together"""
        if not levels:
            return []
        
        clusters = []
        sorted_levels = sorted(levels, key=lambda x: x['price'])
        
        current_cluster = {
            'prices': [sorted_levels[0]['price']],
            'volumes': [sorted_levels[0]['volume']],
            'strengths': [sorted_levels[0].get('strength', 0.5)]
        }
        
        for level in sorted_levels[1:]:
            # Check if close to current cluster
            avg_price = np.mean(current_cluster['prices'])
            if abs(level['price'] - avg_price) / avg_price <= self.cluster_proximity:
                current_cluster['prices'].append(level['price'])
                current_cluster['volumes'].append(level['volume'])
                current_cluster['strengths'].append(level.get('strength', 0.5))
            else:
                # Finalize current cluster
                clusters.append({
                    'min_price': min(current_cluster['prices']),
                    'max_price': max(current_cluster['prices']),
                    'center_price': np.mean(current_cluster['prices']),
                    'total_volume': sum(current_cluster['volumes']),
                    'avg_strength': np.mean(current_cluster['strengths'])
                })
                
                # Start new cluster
                current_cluster = {
                    'prices': [level['price']],
                    'volumes': [level['volume']],
                    'strengths': [level.get('strength', 0.5)]
                }
        
        # Add last cluster
        if current_cluster['prices']:
            clusters.append({
                'min_price': min(current_cluster['prices']),
                'max_price': max(current_cluster['prices']),
                'center_price': np.mean(current_cluster['prices']),
                'total_volume': sum(current_cluster['volumes']),
                'avg_strength': np.mean(current_cluster['strengths'])
            })
        
        return clusters
    
    # ============================================================================
    # STOP LOSS CLUSTER TRACKING
    # ============================================================================
    
    def identify_stop_clusters(self, pair: str, price_levels: List[float], current_price: float) -> List[Dict]:
        """
        Identify areas with many stop losses (liquidity zones)
        
        Args:
            pair: Trading pair
            price_levels: List of price levels where stops might be
            current_price: Current market price
        
        Returns:
            List of stop clusters
        """
        clusters = []
        
        # Common stop loss placement patterns
        # Above recent highs (for short stops)
        # Below recent lows (for long stops)
        
        if not price_levels:
            return clusters
        
        # Group nearby levels
        sorted_levels = sorted(price_levels)
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] <= self.cluster_proximity:
                current_cluster.append(level)
            else:
                if len(current_cluster) >= 3:  # Minimum 3 stops to be a cluster
                    clusters.append({
                        'pair': pair,
                        'price': np.mean(current_cluster),
                        'price_range': (min(current_cluster), max(current_cluster)),
                        'stop_count': len(current_cluster),
                        'distance_from_price': abs(np.mean(current_cluster) - current_price) / current_price,
                        'identified_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                current_cluster = [level]
        
        # Add last cluster
        if len(current_cluster) >= 3:
            clusters.append({
                'pair': pair,
                'price': np.mean(current_cluster),
                'price_range': (min(current_cluster), max(current_cluster)),
                'stop_count': len(current_cluster),
                'distance_from_price': abs(np.mean(current_cluster) - current_price) / current_price,
                'identified_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Store clusters
        if clusters:
            self.zones_data['stop_clusters'].extend(clusters)
            self.zones_data['stop_clusters'] = self.zones_data['stop_clusters'][-100:]
            self.save_data()
        
        return clusters
    
    # ============================================================================
    # LIQUIDITY GRAB PREDICTION
    # ============================================================================
    
    def predict_liquidity_grab(self, pair: str, current_price: float, zones: List[Dict]) -> Optional[Dict]:
        """
        Predict potential liquidity grabs based on zones and stop clusters
        
        Args:
            pair: Trading pair
            current_price: Current market price
            zones: List of identified zones
        
        Returns:
            Prediction dict if liquidity grab likely
        """
        # Find zones near current price
        nearby_zones = []
        for zone in zones:
            zone_price = zone.get('center_price', zone.get('price', 0))
            distance = abs(zone_price - current_price) / current_price
            
            if distance <= 0.02:  # Within 2%
                nearby_zones.append({
                    'zone': zone,
                    'distance': distance,
                    'type': zone.get('type', 'unknown')
                })
        
        if not nearby_zones:
            return None
        
        # Check for stop clusters above/below
        stop_clusters = [
            sc for sc in self.zones_data['stop_clusters']
            if sc['pair'] == pair and sc['distance_from_price'] <= 0.05
        ]
        
        # Predict liquidity grab if:
        # 1. Strong zone nearby
        # 2. Stop cluster in opposite direction
        # 3. Price approaching zone
        
        for zone_info in nearby_zones:
            zone = zone_info['zone']
            zone_price = zone.get('center_price', zone.get('price', 0))
            
            # Check for stops above (would grab on way up)
            stops_above = [sc for sc in stop_clusters if sc['price'] > current_price]
            stops_below = [sc for sc in stop_clusters if sc['price'] < current_price]
            
            if zone_info['type'] == 'demand' and stops_below:
                # Price might drop to grab stops below before rallying
                prediction = {
                    'pair': pair,
                    'type': 'liquidity_grab',
                    'direction': 'down_then_up',
                    'target_zone': zone_price,
                    'stop_cluster': stops_below[0]['price'],
                    'probability': min(0.8, zone.get('strength', 0.5) + 0.3),
                    'predicted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                self.zones_data['liquidity_zones'].append(prediction)
                self.zones_data['liquidity_zones'] = self.zones_data['liquidity_zones'][-50:]
                self.save_data()
                
                return prediction
            
            elif zone_info['type'] == 'supply' and stops_above:
                # Price might spike to grab stops above before dropping
                prediction = {
                    'pair': pair,
                    'type': 'liquidity_grab',
                    'direction': 'up_then_down',
                    'target_zone': zone_price,
                    'stop_cluster': stops_above[0]['price'],
                    'probability': min(0.8, zone.get('strength', 0.5) + 0.3),
                    'predicted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                self.zones_data['liquidity_zones'].append(prediction)
                self.zones_data['liquidity_zones'] = self.zones_data['liquidity_zones'][-50:]
                self.save_data()
                
                return prediction
        
        return None
    
    # ============================================================================
    # ANALYSIS & REPORTING
    # ============================================================================
    
    def analyze_market_maker_zones(self, pair: str, price_data: List[Dict], current_price: float) -> Dict:
        """
        Complete market maker zone analysis
        
        Args:
            pair: Trading pair
            price_data: Price data with volume/activity
            current_price: Current market price
        
        Returns:
            Complete analysis
        """
        # Identify zones
        demand_zone = self.identify_demand_zone(pair, price_data)
        supply_zone = self.identify_supply_zone(pair, price_data)
        
        # Get recent zones
        recent_demand = [
            z for z in self.zones_data['demand_zones']
            if z['pair'] == pair and z['status'] == 'active'
        ][-5:]
        
        recent_supply = [
            z for z in self.zones_data['supply_zones']
            if z['pair'] == pair and z['status'] == 'active'
        ][-5:]
        
        # Identify stop clusters (using round numbers as proxy)
        round_numbers = self._get_round_numbers(current_price)
        stop_clusters = self.identify_stop_clusters(pair, round_numbers, current_price)
        
        # Predict liquidity grab
        all_zones = (recent_demand + recent_supply)
        liquidity_prediction = self.predict_liquidity_grab(pair, current_price, all_zones)
        
        return {
            'pair': pair,
            'current_price': current_price,
            'demand_zones': recent_demand,
            'supply_zones': recent_supply,
            'stop_clusters': stop_clusters[:5],  # Top 5
            'liquidity_prediction': liquidity_prediction,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _get_round_numbers(self, price: float) -> List[float]:
        """Get round number price levels (psychological levels)"""
        if price < 1:
            # For pairs like EUR/USD
            base = round(price, 2)
            return [base - 0.01, base, base + 0.01]
        elif price < 100:
            # For pairs in 1-100 range
            base = round(price)
            return [base - 1, base, base + 1]
        elif price < 1000:
            # For prices like BTC
            base = round(price, -1)  # Round to nearest 10
            return [base - 10, base, base + 10]
        else:
            # For high prices
            base = round(price, -2)  # Round to nearest 100
            return [base - 100, base, base + 100]
    
    def format_analysis_message(self, analysis: Dict) -> str:
        """Format analysis as Telegram message"""
        msg = f"🎯 **MARKET MAKER ZONES - {analysis['pair']}**\n\n"
        msg += f"*Current Price:* ${analysis['current_price']:,.2f}\n\n"
        
        # Demand zones
        if analysis['demand_zones']:
            msg += f"🟢 *DEMAND ZONES (Support):*\n"
            for zone in analysis['demand_zones'][:3]:
                msg += f"• ${zone['center_price']:,.2f} (Strength: {zone['strength']:.2f})\n"
            msg += "\n"
        
        # Supply zones
        if analysis['supply_zones']:
            msg += f"🔴 *SUPPLY ZONES (Resistance):*\n"
            for zone in analysis['supply_zones'][:3]:
                msg += f"• ${zone['center_price']:,.2f} (Strength: {zone['strength']:.2f})\n"
            msg += "\n"
        
        # Stop clusters
        if analysis['stop_clusters']:
            msg += f"📍 *STOP CLUSTERS (Liquidity Zones):*\n"
            for cluster in analysis['stop_clusters'][:3]:
                msg += f"• ${cluster['price']:,.2f} ({cluster['stop_count']} stops)\n"
            msg += "\n"
        
        # Liquidity grab prediction
        if analysis['liquidity_prediction']:
            pred = analysis['liquidity_prediction']
            direction_emoji = "⬇️⬆️" if pred['direction'] == 'down_then_up' else "⬆️⬇️"
            msg += f"🎯 *LIQUIDITY GRAB PREDICTION:*\n"
            msg += f"{direction_emoji} {pred['direction'].replace('_', ' ').title()}\n"
            msg += f"Target: ${pred['target_zone']:,.2f}\n"
            msg += f"Stop Cluster: ${pred['stop_cluster']:,.2f}\n"
            msg += f"Probability: {pred['probability']*100:.0f}%\n\n"
        
        msg += f"⏰ Updated: {analysis['timestamp']}"
        
        return msg


if __name__ == "__main__":
    # Test market maker zones
    mm = MarketMakerZones()
    
    # Mock price data
    price_data = [
        {'price': 50000, 'buy_volume': 1000000, 'sell_volume': 500000, 'strength': 0.8},
        {'price': 50010, 'buy_volume': 800000, 'sell_volume': 600000, 'strength': 0.7},
        {'price': 50020, 'buy_volume': 600000, 'sell_volume': 800000, 'strength': 0.6},
    ]
    
    analysis = mm.analyze_market_maker_zones('BTC', price_data, 50015)
    print(mm.format_analysis_message(analysis))

