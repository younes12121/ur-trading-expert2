"""
Advanced Portfolio Optimizer for Multi-Asset Trading
Implements Modern Portfolio Theory with trading-specific enhancements
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
from scipy.optimize import minimize
from scipy import linalg
import warnings

warnings.filterwarnings('ignore')


class PortfolioOptimizer:
    """Advanced portfolio optimization with correlation analysis and risk management"""
    
    def __init__(self, trade_tracker=None):
        """
        Initialize portfolio optimizer
        
        Args:
            trade_tracker: TradeTracker instance for historical data
        """
        self.trade_tracker = trade_tracker
        self.correlation_matrix = None
        self.expected_returns = {}
        self.volatilities = {}
        self.asset_weights = {}
        
        # Risk parameters
        self.max_correlation_exposure = 0.7  # Max exposure to correlated assets
        self.max_single_asset_weight = 0.3   # Max 30% in any single asset
        self.target_volatility = 0.15        # 15% annual volatility target
        
    def calculate_asset_correlations(self, lookback_days: int = 90) -> Dict:
        """
        Calculate correlation matrix between trading assets
        
        Args:
            lookback_days: Number of days to look back for correlation calculation
            
        Returns:
            Dictionary with correlation matrix and related metrics
        """
        if not self.trade_tracker:
            # Mock data for demonstration
            assets = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'GOLD', 'BTC']
            mock_correlations = {
                'EURUSD': {'GBPUSD': 0.72, 'USDJPY': -0.15, 'AUDUSD': 0.65, 'GOLD': 0.25, 'BTC': 0.08},
                'GBPUSD': {'EURUSD': 0.72, 'USDJPY': -0.22, 'AUDUSD': 0.58, 'GOLD': 0.18, 'BTC': 0.12},
                'USDJPY': {'EURUSD': -0.15, 'GBPUSD': -0.22, 'AUDUSD': -0.45, 'GOLD': -0.35, 'BTC': -0.05},
                'AUDUSD': {'EURUSD': 0.65, 'GBPUSD': 0.58, 'USDJPY': -0.45, 'GOLD': 0.85, 'BTC': 0.15},
                'GOLD': {'EURUSD': 0.25, 'GBPUSD': 0.18, 'USDJPY': -0.35, 'AUDUSD': 0.85, 'BTC': 0.25},
                'BTC': {'EURUSD': 0.08, 'GBPUSD': 0.12, 'USDJPY': -0.05, 'AUDUSD': 0.15, 'GOLD': 0.25}
            }
            
            # Create symmetric matrix
            correlation_matrix = pd.DataFrame(index=assets, columns=assets, dtype=float)
            for i, asset1 in enumerate(assets):
                for j, asset2 in enumerate(assets):
                    if i == j:
                        correlation_matrix.loc[asset1, asset2] = 1.0
                    elif asset2 in mock_correlations.get(asset1, {}):
                        correlation_matrix.loc[asset1, asset2] = mock_correlations[asset1][asset2]
                    elif asset1 in mock_correlations.get(asset2, {}):
                        correlation_matrix.loc[asset1, asset2] = mock_correlations[asset2][asset1]
                    else:
                        correlation_matrix.loc[asset1, asset2] = 0.0
            
            self.correlation_matrix = correlation_matrix
            
        else:
            # Real implementation with trade tracker
            signals = self.trade_tracker.get_recent_signals(days=lookback_days)
            
            # Group signals by asset and calculate returns
            asset_returns = defaultdict(list)
            for signal in signals:
                if signal.get('exit_price') and signal.get('entry_price'):
                    pnl_pct = (signal['exit_price'] - signal['entry_price']) / signal['entry_price']
                    asset_returns[signal['asset']].append(pnl_pct)
            
            # Create correlation matrix
            assets = list(asset_returns.keys())
            if len(assets) < 2:
                return {"error": "Insufficient data for correlation analysis"}
            
            # Convert to DataFrame for correlation calculation
            max_len = max(len(returns) for returns in asset_returns.values())
            returns_df = pd.DataFrame()
            
            for asset in assets:
                returns = asset_returns[asset]
                # Pad shorter series with zeros or interpolate
                if len(returns) < max_len:
                    returns.extend([0] * (max_len - len(returns)))
                returns_df[asset] = returns[:max_len]
            
            self.correlation_matrix = returns_df.corr()
        
        # Analyze correlation clusters
        correlation_clusters = self._identify_correlation_clusters()
        
        return {
            'correlation_matrix': self.correlation_matrix.to_dict(),
            'correlation_clusters': correlation_clusters,
            'high_correlation_pairs': self._find_high_correlation_pairs(),
            'diversification_score': self._calculate_diversification_score()
        }
    
    def _identify_correlation_clusters(self, threshold: float = 0.6) -> Dict:
        """Identify groups of highly correlated assets"""
        if self.correlation_matrix is None:
            return {}
        
        clusters = {}
        processed = set()
        cluster_id = 0
        
        for asset in self.correlation_matrix.index:
            if asset in processed:
                continue
                
            # Find all assets correlated above threshold
            correlated_assets = []
            for other_asset in self.correlation_matrix.index:
                if (asset != other_asset and 
                    abs(self.correlation_matrix.loc[asset, other_asset]) >= threshold):
                    correlated_assets.append(other_asset)
            
            if correlated_assets:
                cluster_assets = [asset] + correlated_assets
                clusters[f'cluster_{cluster_id}'] = {
                    'assets': cluster_assets,
                    'avg_correlation': np.mean([
                        abs(self.correlation_matrix.loc[a1, a2])
                        for i, a1 in enumerate(cluster_assets)
                        for a2 in cluster_assets[i+1:]
                    ]),
                    'size': len(cluster_assets)
                }
                processed.update(cluster_assets)
                cluster_id += 1
        
        return clusters
    
    def _find_high_correlation_pairs(self, threshold: float = 0.7) -> List[Dict]:
        """Find pairs of assets with high correlation"""
        if self.correlation_matrix is None:
            return []
        
        high_corr_pairs = []
        for i, asset1 in enumerate(self.correlation_matrix.index):
            for asset2 in self.correlation_matrix.index[i+1:]:
                corr = self.correlation_matrix.loc[asset1, asset2]
                if abs(corr) >= threshold:
                    high_corr_pairs.append({
                        'asset1': asset1,
                        'asset2': asset2,
                        'correlation': round(corr, 3),
                        'relationship': 'positive' if corr > 0 else 'negative',
                        'strength': 'very_strong' if abs(corr) >= 0.8 else 'strong'
                    })
        
        return sorted(high_corr_pairs, key=lambda x: abs(x['correlation']), reverse=True)
    
    def _calculate_diversification_score(self) -> float:
        """Calculate portfolio diversification score (0-100)"""
        if self.correlation_matrix is None:
            return 0.0
        
        # Average absolute correlation (excluding diagonal)
        mask = ~np.eye(self.correlation_matrix.shape[0], dtype=bool)
        avg_abs_corr = np.abs(self.correlation_matrix.values[mask]).mean()
        
        # Convert to diversification score (lower correlation = higher diversification)
        diversification_score = (1 - avg_abs_corr) * 100
        return round(diversification_score, 1)
    
    def optimize_portfolio_weights(self, current_positions: Dict[str, float], 
                                 target_risk: float = 0.15) -> Dict:
        """
        Optimize portfolio weights considering current positions and correlations
        
        Args:
            current_positions: Dict of asset -> current weight/exposure
            target_risk: Target portfolio volatility
            
        Returns:
            Dictionary with optimized weights and recommendations
        """
        if self.correlation_matrix is None:
            self.calculate_asset_correlations()
        
        assets = list(current_positions.keys())
        n_assets = len(assets)
        
        if n_assets < 2:
            return {"error": "Need at least 2 assets for optimization"}
        
        # Mock expected returns and volatilities (in practice, calculate from historical data)
        expected_returns = {}
        volatilities = {}
        
        for asset in assets:
            if 'USD' in asset:  # Forex pairs
                expected_returns[asset] = np.random.uniform(0.05, 0.15)  # 5-15% annual
                volatilities[asset] = np.random.uniform(0.10, 0.20)      # 10-20% annual
            elif asset == 'BTC':
                expected_returns[asset] = np.random.uniform(0.20, 0.50)  # 20-50% annual
                volatilities[asset] = np.random.uniform(0.50, 1.00)      # 50-100% annual
            elif asset == 'GOLD':
                expected_returns[asset] = np.random.uniform(0.03, 0.08)  # 3-8% annual
                volatilities[asset] = np.random.uniform(0.15, 0.25)      # 15-25% annual
            else:
                expected_returns[asset] = np.random.uniform(0.08, 0.12)  # Default
                volatilities[asset] = np.random.uniform(0.15, 0.30)      # Default
        
        # Create covariance matrix
        corr_subset = self.correlation_matrix.loc[assets, assets]
        vol_array = np.array([volatilities[asset] for asset in assets])
        cov_matrix = corr_subset.values * np.outer(vol_array, vol_array)
        
        # Expected returns array
        mu = np.array([expected_returns[asset] for asset in assets])
        
        # Optimization constraints
        constraints = [
            # Weights sum to 1
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
            # Target volatility
            {'type': 'eq', 'fun': lambda w: np.sqrt(w.T @ cov_matrix @ w) - target_risk}
        ]
        
        # Bounds: max 30% per asset, min 0%
        bounds = [(0.0, self.max_single_asset_weight) for _ in range(n_assets)]
        
        # Objective function: maximize Sharpe ratio (minimize negative Sharpe)
        def objective(weights):
            portfolio_return = np.sum(weights * mu)
            portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)
            # Assume risk-free rate of 2%
            sharpe = (portfolio_return - 0.02) / portfolio_vol
            return -sharpe  # Minimize negative Sharpe
        
        # Initial guess: equal weights
        x0 = np.array([1.0/n_assets] * n_assets)
        
        try:
            # Run optimization
            result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                optimal_weights = dict(zip(assets, result.x))
                
                # Calculate portfolio metrics
                portfolio_return = np.sum(result.x * mu)
                portfolio_vol = np.sqrt(result.x.T @ cov_matrix @ result.x)
                sharpe_ratio = (portfolio_return - 0.02) / portfolio_vol
                
                # Generate rebalancing recommendations
                current_weights = np.array([current_positions.get(asset, 0.0) for asset in assets])
                weight_changes = result.x - current_weights
                
                recommendations = []
                for i, asset in enumerate(assets):
                    change = weight_changes[i]
                    if abs(change) > 0.05:  # Only recommend changes > 5%
                        action = 'increase' if change > 0 else 'decrease'
                        recommendations.append({
                            'asset': asset,
                            'action': action,
                            'current_weight': round(current_weights[i], 3),
                            'target_weight': round(result.x[i], 3),
                            'change': round(change, 3)
                        })
                
                return {
                    'success': True,
                    'optimal_weights': {asset: round(weight, 3) for asset, weight in optimal_weights.items()},
                    'portfolio_metrics': {
                        'expected_return': round(portfolio_return, 3),
                        'volatility': round(portfolio_vol, 3),
                        'sharpe_ratio': round(sharpe_ratio, 3)
                    },
                    'recommendations': recommendations,
                    'diversification_score': self._calculate_diversification_score()
                }
            
            else:
                return {"error": f"Optimization failed: {result.message}"}
                
        except Exception as e:
            return {"error": f"Optimization error: {str(e)}"}
    
    def analyze_risk_concentration(self, current_positions: Dict[str, float]) -> Dict:
        """
        Analyze risk concentration in current portfolio
        
        Args:
            current_positions: Dict of asset -> current weight/exposure
            
        Returns:
            Dictionary with risk concentration analysis
        """
        if self.correlation_matrix is None:
            self.calculate_asset_correlations()
        
        assets = list(current_positions.keys())
        weights = np.array([current_positions[asset] for asset in assets])
        
        # Calculate contribution to portfolio risk
        corr_subset = self.correlation_matrix.loc[assets, assets]
        
        # Risk concentration metrics
        risk_analysis = {
            'herfindahl_index': np.sum(weights ** 2),  # Concentration measure
            'effective_assets': 1 / np.sum(weights ** 2),  # Effective number of assets
            'max_weight': np.max(weights),
            'max_weight_asset': assets[np.argmax(weights)],
            'correlation_exposure': {}
        }
        
        # Analyze correlation exposure
        for i, asset1 in enumerate(assets):
            correlated_exposure = 0
            for j, asset2 in enumerate(assets):
                if i != j and abs(corr_subset.loc[asset1, asset2]) > 0.5:
                    correlated_exposure += weights[j] * abs(corr_subset.loc[asset1, asset2])
            
            risk_analysis['correlation_exposure'][asset1] = round(correlated_exposure, 3)
        
        # Risk warnings
        warnings = []
        if risk_analysis['herfindahl_index'] > 0.5:
            warnings.append("High concentration risk - consider diversifying")
        
        if risk_analysis['max_weight'] > self.max_single_asset_weight:
            warnings.append(f"Single asset ({risk_analysis['max_weight_asset']}) exceeds maximum weight")
        
        for asset, exposure in risk_analysis['correlation_exposure'].items():
            if exposure > self.max_correlation_exposure:
                warnings.append(f"High correlation exposure for {asset}: {exposure:.1%}")
        
        risk_analysis['warnings'] = warnings
        
        return risk_analysis
    
    def generate_rebalancing_schedule(self, current_positions: Dict[str, float],
                                    rebalancing_frequency: str = 'weekly') -> List[Dict]:
        """
        Generate a rebalancing schedule based on market conditions
        
        Args:
            current_positions: Current portfolio positions
            rebalancing_frequency: 'daily', 'weekly', 'monthly'
            
        Returns:
            List of rebalancing recommendations with dates
        """
        optimization_result = self.optimize_portfolio_weights(current_positions)
        
        if not optimization_result.get('success'):
            return []
        
        recommendations = optimization_result.get('recommendations', [])
        
        # Create rebalancing schedule
        frequency_days = {'daily': 1, 'weekly': 7, 'monthly': 30}
        days_ahead = frequency_days.get(rebalancing_frequency, 7)
        
        schedule = []
        for i in range(4):  # Next 4 rebalancing periods
            rebalance_date = datetime.now() + timedelta(days=days_ahead * (i + 1))
            
            # Simulate market condition changes (in practice, use forecasting)
            market_condition = ['stable', 'volatile', 'trending'][i % 3]
            
            # Adjust recommendations based on market conditions
            adjusted_recommendations = []
            for rec in recommendations:
                if market_condition == 'volatile':
                    # Reduce position changes in volatile markets
                    adjusted_change = rec['change'] * 0.5
                elif market_condition == 'trending':
                    # Increase momentum allocation in trending markets
                    if rec['asset'] in ['BTC', 'GOLD'] and rec['action'] == 'increase':
                        adjusted_change = rec['change'] * 1.2
                    else:
                        adjusted_change = rec['change']
                else:
                    adjusted_change = rec['change']
                
                if abs(adjusted_change) > 0.03:  # Only include significant changes
                    adjusted_recommendations.append({
                        'asset': rec['asset'],
                        'action': rec['action'],
                        'change': round(adjusted_change, 3),
                        'reason': f"Rebalancing for {market_condition} market"
                    })
            
            if adjusted_recommendations:
                schedule.append({
                    'date': rebalance_date.strftime('%Y-%m-%d'),
                    'market_condition': market_condition,
                    'recommendations': adjusted_recommendations
                })
        
        return schedule
    
    def export_analysis_report(self, current_positions: Dict[str, float], 
                              filename: str = None) -> str:
        """
        Export comprehensive portfolio analysis report
        
        Args:
            current_positions: Current portfolio positions
            filename: Optional filename for the report
            
        Returns:
            Filename of the exported report
        """
        if filename is None:
            filename = f"portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Generate all analyses
        correlation_analysis = self.calculate_asset_correlations()
        optimization_result = self.optimize_portfolio_weights(current_positions)
        risk_analysis = self.analyze_risk_concentration(current_positions)
        rebalancing_schedule = self.generate_rebalancing_schedule(current_positions)
        
        # Compile comprehensive report
        report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'current_positions': current_positions,
                'optimization_target_risk': self.target_volatility,
                'max_single_asset_weight': self.max_single_asset_weight
            },
            'correlation_analysis': correlation_analysis,
            'optimization_results': optimization_result,
            'risk_analysis': risk_analysis,
            'rebalancing_schedule': rebalancing_schedule,
            'summary': {
                'diversification_score': correlation_analysis.get('diversification_score', 0),
                'portfolio_risk_level': 'High' if risk_analysis.get('herfindahl_index', 0) > 0.5 else 'Moderate',
                'optimization_success': optimization_result.get('success', False),
                'total_warnings': len(risk_analysis.get('warnings', []))
            }
        }
        
        # Save report
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename


# Example usage and testing
if __name__ == "__main__":
    # Initialize optimizer
    optimizer = PortfolioOptimizer()
    
    # Example current positions
    current_positions = {
        'EURUSD': 0.25,
        'GBPUSD': 0.20,
        'USDJPY': 0.15,
        'AUDUSD': 0.20,
        'GOLD': 0.15,
        'BTC': 0.05
    }
    
    print("=" * 70)
    print("🎯 PORTFOLIO OPTIMIZER DEMONSTRATION")
    print("=" * 70)
    
    # 1. Correlation Analysis
    print("\n1. CORRELATION ANALYSIS")
    print("-" * 70)
    correlation_results = optimizer.calculate_asset_correlations()
    print(f"Diversification Score: {correlation_results['diversification_score']}/100")
    print(f"High Correlation Pairs: {len(correlation_results['high_correlation_pairs'])}")
    
    if correlation_results['high_correlation_pairs']:
        for pair in correlation_results['high_correlation_pairs'][:3]:
            print(f"  {pair['asset1']} - {pair['asset2']}: {pair['correlation']} ({pair['strength']})")
    
    # 2. Portfolio Optimization
    print("\n2. PORTFOLIO OPTIMIZATION")
    print("-" * 70)
    optimization_results = optimizer.optimize_portfolio_weights(current_positions)
    
    if optimization_results.get('success'):
        metrics = optimization_results['portfolio_metrics']
        print(f"Expected Return: {metrics['expected_return']:.1%}")
        print(f"Volatility: {metrics['volatility']:.1%}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        
        print(f"\nRecommendations: {len(optimization_results['recommendations'])}")
        for rec in optimization_results['recommendations'][:3]:
            print(f"  {rec['asset']}: {rec['action']} by {abs(rec['change']):.1%}")
    
    # 3. Risk Analysis
    print("\n3. RISK CONCENTRATION ANALYSIS")
    print("-" * 70)
    risk_analysis = optimizer.analyze_risk_concentration(current_positions)
    print(f"Concentration Index: {risk_analysis['herfindahl_index']:.3f}")
    print(f"Effective Assets: {risk_analysis['effective_assets']:.1f}")
    print(f"Max Weight: {risk_analysis['max_weight']:.1%} ({risk_analysis['max_weight_asset']})")
    print(f"Warnings: {len(risk_analysis['warnings'])}")
    
    # 4. Export Report
    print("\n4. EXPORTING COMPREHENSIVE REPORT")
    print("-" * 70)
    report_filename = optimizer.export_analysis_report(current_positions)
    print(f"📊 Report exported to: {report_filename}")
    
    print("\n✅ Portfolio optimizer demonstration complete!")
