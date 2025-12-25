"""
Signal Quality Scorer
Implements weighted scoring system for signal quality assessment
Returns quality score from 0-100 based on criteria importance
"""

from typing import Dict, List, Optional
import numpy as np
from datetime import datetime


class SignalQualityScorer:
    """
    Weighted quality scoring system for trading signals
    Different criteria have different importance weights
    """
    
    def __init__(self):
        # Define criteria weights (sum should be ~100 for easy interpretation)
        # Higher weight = more important for signal quality
        self.criteria_weights = {
            # Critical criteria (high weight)
            'mtf_alignment': 8.0,          # Multi-timeframe alignment is critical
            'trend_consistency': 7.0,      # Trend consistency across TFs
            'market_structure': 6.5,       # Market structure health
            'risk_reward_ratio': 6.0,      # Risk/reward is essential
            
            # Important criteria (medium-high weight)
            'rsi_momentum': 5.5,           # RSI momentum confirmation
            'macd_confirmation': 5.0,      # MACD trend confirmation
            'adx_strength': 5.0,           # Trend strength
            'volume_confirmation': 5.0,     # Volume supports move
            'htf_confirmation': 5.0,        # Higher timeframe confirmation
            
            # Supporting criteria (medium weight)
            'price_ema': 4.5,              # Price vs EMA position
            'stochastic_signal': 4.0,      # Stochastic confirmation
            'price_action_patterns': 4.0,  # Price action patterns
            'momentum_acceleration': 4.0,  # Momentum acceleration
            'sr_respect': 4.0,             # Support/resistance respect
            
            # Additional criteria (lower weight but still important)
            'bb_position': 3.5,            # Bollinger Bands position
            'atr_volatility': 3.5,         # Volatility check
            'ema_spacing': 3.0,            # EMA spacing
            'divergence_analysis': 3.5,    # Divergence check
            'session_timing': 3.0,         # Session timing
            'breakout_potential': 3.5,     # Breakout potential
        }
        
        # Normalize weights to sum to 100
        total_weight = sum(self.criteria_weights.values())
        self.criteria_weights = {k: (v / total_weight) * 100 for k, v in self.criteria_weights.items()}
        
        # Quality thresholds
        self.quality_thresholds = {
            'EXCELLENT': 90,   # 90-100: Excellent quality
            'VERY_GOOD': 85,    # 85-89: Very good quality
            'GOOD': 80,         # 80-84: Good quality
            'FAIR': 70,         # 70-79: Fair quality
            'POOR': 60,         # 60-69: Poor quality
            'INSUFFICIENT': 0   # <60: Insufficient quality
        }
    
    def calculate_quality_score(self, criteria_results: Dict[str, bool], 
                               criteria_details: Optional[Dict] = None) -> Dict:
        """
        Calculate weighted quality score from criteria results
        
        Args:
            criteria_results: Dict mapping criterion name to pass/fail (bool)
            criteria_details: Optional dict with detailed criterion analysis
            
        Returns:
            Dict with quality score, grade, and breakdown
        """
        try:
            total_score = 0.0
            passed_criteria = []
            failed_criteria = []
            weighted_scores = {}
            
            # Calculate weighted score for each criterion
            for criterion, passed in criteria_results.items():
                weight = self.criteria_weights.get(criterion, 0)
                
                if passed:
                    score_contribution = weight
                    passed_criteria.append(criterion)
                else:
                    score_contribution = 0
                    failed_criteria.append(criterion)
                
                total_score += score_contribution
                weighted_scores[criterion] = {
                    'weight': weight,
                    'passed': passed,
                    'contribution': score_contribution
                }
            
            # Determine quality grade
            grade = self._determine_grade(total_score)
            
            # Calculate confidence level
            confidence = self._calculate_confidence(total_score, len(passed_criteria), len(criteria_results))
            
            return {
                'quality_score': round(total_score, 2),
                'grade': grade,
                'confidence_level': confidence,
                'passed_criteria': passed_criteria,
                'failed_criteria': failed_criteria,
                'passed_count': len(passed_criteria),
                'total_count': len(criteria_results),
                'pass_rate': round(len(passed_criteria) / len(criteria_results) * 100, 1) if criteria_results else 0,
                'weighted_breakdown': weighted_scores,
                'top_failures': self._identify_critical_failures(failed_criteria, weighted_scores),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'quality_score': 0,
                'grade': 'ERROR',
                'confidence_level': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _determine_grade(self, score: float) -> str:
        """Determine quality grade based on score"""
        if score >= self.quality_thresholds['EXCELLENT']:
            return 'EXCELLENT'
        elif score >= self.quality_thresholds['VERY_GOOD']:
            return 'VERY_GOOD'
        elif score >= self.quality_thresholds['GOOD']:
            return 'GOOD'
        elif score >= self.quality_thresholds['FAIR']:
            return 'FAIR'
        elif score >= self.quality_thresholds['POOR']:
            return 'POOR'
        else:
            return 'INSUFFICIENT'
    
    def _calculate_confidence(self, score: float, passed_count: int, total_count: int) -> str:
        """Calculate confidence level based on score and pass rate"""
        pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        
        # High confidence: high score AND high pass rate
        if score >= 85 and pass_rate >= 85:
            return 'VERY_HIGH'
        elif score >= 80 and pass_rate >= 80:
            return 'HIGH'
        elif score >= 75 and pass_rate >= 75:
            return 'MODERATE'
        elif score >= 70:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _identify_critical_failures(self, failed_criteria: List[str], 
                                   weighted_scores: Dict) -> List[Dict]:
        """Identify most critical failed criteria (highest weight)"""
        critical_failures = []
        
        for criterion in failed_criteria:
            if criterion in weighted_scores:
                weight = weighted_scores[criterion]['weight']
                critical_failures.append({
                    'criterion': criterion,
                    'weight': weight,
                    'impact': f"Lost {weight:.1f} points"
                })
        
        # Sort by weight (highest first)
        critical_failures.sort(key=lambda x: x['weight'], reverse=True)
        
        return critical_failures[:5]  # Top 5 critical failures
    
    def get_quality_recommendation(self, quality_result: Dict) -> str:
        """Get human-readable recommendation based on quality score"""
        score = quality_result.get('quality_score', 0)
        grade = quality_result.get('grade', 'INSUFFICIENT')
        
        if grade == 'EXCELLENT':
            return "EXCELLENT signal quality - High confidence trade setup"
        elif grade == 'VERY_GOOD':
            return "VERY GOOD signal quality - Strong trade opportunity"
        elif grade == 'GOOD':
            return "GOOD signal quality - Valid trade setup"
        elif grade == 'FAIR':
            return "FAIR signal quality - Consider waiting for better setup"
        elif grade == 'POOR':
            return "POOR signal quality - Not recommended for trading"
        else:
            return "INSUFFICIENT signal quality - Do not trade"
    
    def compare_signals(self, signal1_quality: Dict, signal2_quality: Dict) -> Dict:
        """Compare two signals and recommend which is better"""
        score1 = signal1_quality.get('quality_score', 0)
        score2 = signal2_quality.get('quality_score', 0)
        
        if score1 > score2:
            better = 'signal1'
            difference = score1 - score2
        elif score2 > score1:
            better = 'signal2'
            difference = score2 - score1
        else:
            better = 'equal'
            difference = 0
        
        return {
            'better_signal': better,
            'score_difference': round(difference, 2),
            'signal1_score': score1,
            'signal2_score': score2,
            'recommendation': f"Signal {better.replace('signal', '')} is better" if better != 'equal' else "Signals are equal quality"
        }


# =================================================================
# USAGE EXAMPLE
# =================================================================

if __name__ == "__main__":
    print("SIGNAL QUALITY SCORER - TESTING")
    print("="*60)
    
    scorer = SignalQualityScorer()
    
    # Example criteria results
    example_criteria = {
        'mtf_alignment': True,
        'price_ema': True,
        'rsi_momentum': True,
        'macd_confirmation': True,
        'stochastic_signal': True,
        'adx_strength': True,
        'volume_confirmation': True,
        'bb_position': True,
        'atr_volatility': True,
        'ema_spacing': True,
        'price_action_patterns': True,
        'htf_confirmation': True,
        'momentum_acceleration': True,
        'sr_respect': True,
        'divergence_analysis': True,
        'session_timing': True,
        'breakout_potential': True,
        'risk_reward_ratio': True,
        'trend_consistency': True,
        'market_structure': True
    }
    
    # Calculate quality
    result = scorer.calculate_quality_score(example_criteria)
    
    print(f"\nQuality Score: {result['quality_score']}/100")
    print(f"Grade: {result['grade']}")
    print(f"Confidence: {result['confidence_level']}")
    print(f"Passed: {result['passed_count']}/{result['total_count']} criteria")
    print(f"\nRecommendation: {scorer.get_quality_recommendation(result)}")
    
    print("\n" + "="*60)
    print("Signal quality scorer loaded successfully!")

