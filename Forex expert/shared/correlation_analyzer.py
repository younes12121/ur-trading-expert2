"""
Dynamic Correlation Analyzer
Analyzes real-time correlations between assets and market regimes
Adjusts signal generation based on inter-market relationships
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from data_fetcher import BinanceDataFetcher
import config


class DynamicCorrelationAnalyzer:
    """
    Analyzes dynamic correlations between trading assets
    Helps identify market regimes and inter-market relationships
    """

    def __init__(self):
        self.data_fetcher = BinanceDataFetcher()
        self.correlation_window = 100  # Days to analyze correlations
        self.assets = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT',  # Crypto
            'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD',  # Forex
            'GC=F', 'SI=F', 'CL=F'  # Commodities (limited free data)
        ]

        # Market regime thresholds
        self.regime_thresholds = {
            'HIGH_CORRELATION': 0.7,
            'MODERATE_CORRELATION': 0.5,
            'LOW_CORRELATION': 0.3,
            'RISK_ON': 0.6,  # When stocks/commodities correlate positively
            'RISK_OFF': -0.4  # When correlations break down
        }

        # Cache for correlation data
        self.correlation_cache = {}
        self.cache_timestamp = None
        self.cache_duration = 3600  # 1 hour cache

    def analyze_market_regime(self) -> Dict:
        """
        Analyze current market regime based on correlations
        Returns: regime analysis with implications for trading
        """
        try:
            correlations = self._calculate_correlations()

            if not correlations:
                return self._get_default_regime()

            # Analyze BTC vs traditional assets
            btc_correlations = correlations.get('BTCUSDT', {})

            # Risk-on/risk-off analysis
            risk_assets = ['EURUSD', 'GBPUSD', 'GC=F', 'SI=F']
            risk_correlations = [btc_correlations.get(asset, 0) for asset in risk_assets if asset in btc_correlations]
            avg_risk_corr = np.mean(risk_correlations) if risk_correlations else 0

            # Commodity correlation
            commodity_corr = btc_correlations.get('GC=F', 0)  # Gold correlation

            # Determine regime
            if avg_risk_corr > self.regime_thresholds['RISK_ON']:
                regime = 'RISK_ON'
                regime_desc = 'Risk-on environment - positive correlations across assets'
                btc_bias = 'BULLISH'  # BTC moves with risk assets
            elif avg_risk_corr < self.regime_thresholds['RISK_OFF']:
                regime = 'RISK_OFF'
                regime_desc = 'Risk-off environment - assets decoupling'
                btc_bias = 'VOLATILE'  # BTC may move independently
            elif commodity_corr > self.regime_thresholds['HIGH_CORRELATION']:
                regime = 'SAFE_HAVEN'
                regime_desc = 'Safe haven flows - BTC correlated with gold'
                btc_bias = 'DEFENSIVE'
            else:
                regime = 'NEUTRAL'
                regime_desc = 'Neutral correlation environment'
                btc_bias = 'MIXED'

            # Calculate correlation strength
            all_corrs = [abs(corr) for asset_corrs in correlations.values()
                        for corr in asset_corrs.values()]
            avg_correlation_strength = np.mean(all_corrs) if all_corrs else 0.5

            return {
                'regime': regime,
                'description': regime_desc,
                'btc_bias': btc_bias,
                'correlation_strength': avg_correlation_strength,
                'risk_correlation': avg_risk_corr,
                'commodity_correlation': commodity_corr,
                'recommendations': self._get_regime_recommendations(regime),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Correlation regime analysis error: {e}")
            return self._get_default_regime()

    def _calculate_correlations(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate rolling correlations between assets
        Returns: nested dict of asset correlations
        """
        # Check cache first
        if self._is_cache_valid():
            return self.correlation_cache

        try:
            correlations = {}

            # Get historical data for each asset
            asset_data = {}
            for asset in self.assets[:5]:  # Limit to first 5 for performance
                try:
                    data = self.data_fetcher.get_historical_data(symbol=asset, limit=self.correlation_window)
                    if data and len(data) > 30:
                        prices = [float(k) for k in data['close']]
                        asset_data[asset] = prices
                except:
                    continue

            # Calculate correlations
            if len(asset_data) >= 2:
                for asset1 in asset_data:
                    correlations[asset1] = {}
                    for asset2 in asset_data:
                        if asset1 != asset2:
                            try:
                                corr = np.corrcoef(asset_data[asset1], asset_data[asset2])[0, 1]
                                correlations[asset1][asset2] = round(corr, 3)
                            except:
                                correlations[asset1][asset2] = 0.0

            # Cache results
            self.correlation_cache = correlations
            self.cache_timestamp = datetime.now()

            return correlations

        except Exception as e:
            print(f"Correlation calculation error: {e}")
            return {}

    def _is_cache_valid(self) -> bool:
        """Check if correlation cache is still valid"""
        if not self.cache_timestamp:
            return False

        elapsed = (datetime.now() - self.cache_timestamp).total_seconds()
        return elapsed < self.cache_duration

    def _get_default_regime(self) -> Dict:
        """Get default regime when analysis fails"""
        return {
            'regime': 'UNKNOWN',
            'description': 'Unable to determine market regime',
            'btc_bias': 'NEUTRAL',
            'correlation_strength': 0.5,
            'risk_correlation': 0.0,
            'commodity_correlation': 0.0,
            'recommendations': ['Use standard risk management'],
            'timestamp': datetime.now().isoformat()
        }

    def _get_regime_recommendations(self, regime: str) -> List[str]:
        """Get trading recommendations based on market regime"""
        recommendations = {
            'RISK_ON': [
                'BTC likely to follow broader market trends',
                'Consider correlated assets for diversification',
                'Monitor equity markets for BTC direction signals',
                'Higher probability of trending moves'
            ],
            'RISK_OFF': [
                'BTC may decouple from traditional assets',
                'Focus on BTC-specific technicals',
                'Watch volatility - potential for sharp moves',
                'Consider safe-haven characteristics'
            ],
            'SAFE_HAVEN': [
                'BTC acting as digital gold',
                'Look for defensive buying opportunities',
                'Monitor gold and USD strength',
                'Lower correlation with risk assets'
            ],
            'NEUTRAL': [
                'Standard correlation environment',
                'Use regular technical analysis',
                'Monitor for regime changes',
                'Balanced risk approach'
            ]
        }

        return recommendations.get(regime, ['Use standard trading approach'])

    def get_asset_correlations(self, target_asset: str = 'BTCUSDT') -> Dict:
        """
        Get correlations for a specific asset
        Returns: correlation data for the target asset
        """
        correlations = self._calculate_correlations()

        if target_asset not in correlations:
            return {'error': f'No correlation data for {target_asset}'}

        asset_corrs = correlations[target_asset]

        # Sort by correlation strength
        sorted_corrs = sorted(asset_corrs.items(), key=lambda x: abs(x[1]), reverse=True)

        return {
            'asset': target_asset,
            'correlations': dict(sorted_corrs),
            'strongest_positive': [asset for asset, corr in sorted_corrs if corr > 0.5][:3],
            'strongest_negative': [asset for asset, corr in sorted_corrs if corr < -0.5][:3],
            'timestamp': datetime.now().isoformat()
        }

    def should_adjust_position_size(self, regime: str, base_position_size: float) -> float:
        """
        Adjust position size based on correlation regime
        Returns: adjusted position size
        """
        adjustments = {
            'RISK_ON': 1.2,      # Increase size in correlated environment
            'RISK_OFF': 0.8,     # Reduce size in volatile decoupling
            'SAFE_HAVEN': 1.0,   # Normal size for defensive moves
            'NEUTRAL': 1.0       # Normal size
        }

        multiplier = adjustments.get(regime, 1.0)
        adjusted_size = base_position_size * multiplier

        # Cap adjustments
        return max(0.5, min(2.0, adjusted_size))

    def get_regime_confidence_score(self, regime: str) -> float:
        """
        Get confidence score for regime detection
        Returns: 0-1 confidence score
        """
        # This would be based on how strongly correlations fit the regime
        # For now, return fixed confidence based on regime type
        confidences = {
            'RISK_ON': 0.8,
            'RISK_OFF': 0.9,  # Easier to detect breakdowns
            'SAFE_HAVEN': 0.7,
            'NEUTRAL': 0.6
        }

        return confidences.get(regime, 0.5)


# ============================================================================
# CORRELATION-BASED SIGNAL ADJUSTMENT
# ============================================================================

class CorrelationAdjustedSignal:
    """
    Adjusts trading signals based on correlation analysis
    """

    def __init__(self):
        self.correlation_analyzer = DynamicCorrelationAnalyzer()

    def adjust_signal(self, signal: Dict) -> Dict:
        """
        Adjust signal parameters based on correlation regime
        """
        try:
            # Get current regime
            regime_analysis = self.correlation_analyzer.analyze_market_regime()
            regime = regime_analysis['regime']

            # Adjust confidence based on regime
            confidence_multiplier = self._get_regime_confidence_multiplier(regime)
            original_confidence = signal.get('confidence', 50)
            adjusted_confidence = min(95, original_confidence * confidence_multiplier)

            # Adjust position size
            original_lot_size = signal.get('lot_size', 1.0)
            adjusted_lot_size = self.correlation_analyzer.should_adjust_position_size(
                regime, original_lot_size
            )

            # Add regime information to signal
            signal['correlation_adjustments'] = {
                'detected_regime': regime,
                'regime_description': regime_analysis['description'],
                'btc_bias': regime_analysis['btc_bias'],
                'original_confidence': original_confidence,
                'adjusted_confidence': round(adjusted_confidence, 1),
                'confidence_multiplier': confidence_multiplier,
                'original_lot_size': original_lot_size,
                'adjusted_lot_size': round(adjusted_lot_size, 3),
                'regime_recommendations': regime_analysis['recommendations']
            }

            # Update signal confidence
            signal['confidence'] = round(adjusted_confidence, 1)
            signal['lot_size'] = round(adjusted_lot_size, 3)

            return signal

        except Exception as e:
            print(f"Signal adjustment error: {e}")
            return signal

    def _get_regime_confidence_multiplier(self, regime: str) -> float:
        """Get confidence multiplier based on regime"""
        multipliers = {
            'RISK_ON': 1.1,      # Slightly boost confidence in correlated markets
            'RISK_OFF': 0.9,     # Reduce confidence in volatile decoupling
            'SAFE_HAVEN': 1.05,  # Slight boost in defensive moves
            'NEUTRAL': 1.0       # No adjustment
        }

        return multipliers.get(regime, 1.0)


if __name__ == "__main__":
    print("🔗 DYNAMIC CORRELATION ANALYZER TEST")
    print("=" * 50)

    analyzer = DynamicCorrelationAnalyzer()

    # Test regime analysis
    regime = analyzer.analyze_market_regime()
    print(f"Market Regime: {regime['regime']}")
    print(f"Description: {regime['description']}")
    print(f"BTC Bias: {regime['btc_bias']}")
    print(f"Correlation Strength: {regime['correlation_strength']:.3f}")
    print(f"Risk Correlation: {regime['risk_correlation']:.3f}")

    print("\nRecommendations:")
    for rec in regime['recommendations']:
        print(f"  • {rec}")

    # Test asset correlations
    btc_corrs = analyzer.get_asset_correlations('BTCUSDT')
    print(f"\nBTC Correlations (top 3):")
    if 'correlations' in btc_corrs:
        for asset, corr in list(btc_corrs['correlations'].items())[:3]:
            print(f"  {asset}: {corr:.3f}")

    print("\n✅ Correlation analysis complete!")
