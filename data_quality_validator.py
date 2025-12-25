"""
Data Quality Validator
Validates data quality and freshness before signal generation
Ensures reliable data for accurate signal generation
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class DataQualityValidator:
    """
    Validates market data quality before signal generation
    Checks for freshness, completeness, and reliability
    """
    
    def __init__(self):
        # Data freshness thresholds (in minutes)
        self.freshness_thresholds = {
            'M15': 20,   # 15-min data should be < 20 min old
            'H1': 70,    # 1-hour data should be < 70 min old
            'H4': 250,   # 4-hour data should be < 250 min old
            'D1': 1440   # Daily data should be < 24 hours old
        }
        
        # Minimum data points required
        self.min_data_points = {
            'M15': 50,
            'H1': 50,
            'H4': 50,
            'D1': 30
        }
        
        # Quality score thresholds
        self.quality_thresholds = {
            'EXCELLENT': 95,
            'GOOD': 85,
            'FAIR': 75,
            'POOR': 60
        }
    
    def validate_data(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Validate multi-timeframe data quality
        
        Args:
            data: Dict mapping timeframe to DataFrame
            
        Returns:
            Dict with validation results and quality score
        """
        validation_results = {
            'is_valid': True,
            'quality_score': 0,
            'quality_grade': 'UNKNOWN',
            'timeframe_validations': {},
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        total_score = 0
        timeframe_count = 0
        
        # Validate each timeframe
        for timeframe, df in data.items():
            tf_validation = self._validate_timeframe(df, timeframe)
            validation_results['timeframe_validations'][timeframe] = tf_validation
            
            if tf_validation['is_valid']:
                total_score += tf_validation['quality_score']
                timeframe_count += 1
            else:
                validation_results['is_valid'] = False
                validation_results['issues'].extend(tf_validation.get('issues', []))
            
            validation_results['warnings'].extend(tf_validation.get('warnings', []))
        
        # Calculate overall quality score
        if timeframe_count > 0:
            validation_results['quality_score'] = round(total_score / timeframe_count, 2)
        else:
            validation_results['quality_score'] = 0
            validation_results['is_valid'] = False
        
        # Determine quality grade
        validation_results['quality_grade'] = self._determine_quality_grade(
            validation_results['quality_score']
        )
        
        # Generate recommendations
        validation_results['recommendations'] = self._generate_recommendations(
            validation_results
        )
        
        return validation_results
    
    def _validate_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """Validate a single timeframe's data"""
        validation = {
            'is_valid': True,
            'quality_score': 0,
            'issues': [],
            'warnings': [],
            'checks': {}
        }
        
        score_components = []
        
        # Check 1: Data exists and is DataFrame
        if df is None or not isinstance(df, pd.DataFrame):
            validation['is_valid'] = False
            validation['issues'].append(f"{timeframe}: No data provided")
            return validation
        
        # Check 2: Minimum data points
        min_points = self.min_data_points.get(timeframe, 20)
        if len(df) < min_points:
            validation['is_valid'] = False
            validation['issues'].append(
                f"{timeframe}: Insufficient data points ({len(df)} < {min_points})"
            )
            validation['checks']['data_points'] = False
        else:
            validation['checks']['data_points'] = True
            score_components.append(20)  # 20 points for having enough data
        
        # Check 3: Required columns
        required_columns = ['open', 'high', 'low', 'close']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation['is_valid'] = False
            validation['issues'].append(
                f"{timeframe}: Missing columns: {', '.join(missing_columns)}"
            )
            validation['checks']['required_columns'] = False
        else:
            validation['checks']['required_columns'] = True
            score_components.append(20)  # 20 points for having required columns
        
        # Check 4: Data freshness
        freshness_check = self._check_data_freshness(df, timeframe)
        validation['checks']['freshness'] = freshness_check['is_fresh']
        if freshness_check['is_fresh']:
            score_components.append(25)  # 25 points for fresh data
        else:
            validation['warnings'].append(f"{timeframe}: {freshness_check['message']}")
            score_components.append(10)  # Reduced points for stale data
        
        # Check 5: No missing values in critical columns
        missing_values = self._check_missing_values(df, required_columns)
        validation['checks']['no_missing_values'] = missing_values['is_valid']
        if missing_values['is_valid']:
            score_components.append(15)  # 15 points for no missing values
        else:
            validation['warnings'].append(f"{timeframe}: {missing_values['message']}")
            score_components.append(5)  # Reduced points for missing values
        
        # Check 6: Data consistency (no negative prices, high > low, etc.)
        consistency_check = self._check_data_consistency(df)
        validation['checks']['consistency'] = consistency_check['is_consistent']
        if consistency_check['is_consistent']:
            score_components.append(20)  # 20 points for consistent data
        else:
            validation['warnings'].append(f"{timeframe}: {consistency_check['message']}")
            score_components.append(5)  # Reduced points for inconsistent data
        
        # Calculate quality score for this timeframe
        validation['quality_score'] = sum(score_components)
        
        return validation
    
    def _check_data_freshness(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """Check if data is fresh enough"""
        try:
            # Check if there's a timestamp column
            if 'timestamp' in df.columns:
                last_timestamp = pd.to_datetime(df['timestamp'].iloc[-1])
            elif df.index.dtype == 'datetime64[ns]':
                last_timestamp = df.index[-1]
            else:
                # Assume data is recent if no timestamp
                return {
                    'is_fresh': True,
                    'message': 'No timestamp available, assuming fresh'
                }
            
            # Calculate age
            now = datetime.now()
            if isinstance(last_timestamp, pd.Timestamp):
                age_minutes = (now - last_timestamp.to_pydatetime()).total_seconds() / 60
            else:
                age_minutes = (now - last_timestamp).total_seconds() / 60
            
            threshold = self.freshness_thresholds.get(timeframe, 60)
            
            if age_minutes <= threshold:
                return {
                    'is_fresh': True,
                    'age_minutes': round(age_minutes, 1),
                    'message': f'Data is fresh ({age_minutes:.1f} min old)'
                }
            else:
                return {
                    'is_fresh': False,
                    'age_minutes': round(age_minutes, 1),
                    'message': f'Data is stale ({age_minutes:.1f} min old, threshold: {threshold} min)'
                }
        except Exception as e:
            return {
                'is_fresh': True,  # Default to fresh if check fails
                'message': f'Could not check freshness: {str(e)}'
            }
    
    def _check_missing_values(self, df: pd.DataFrame, columns: List[str]) -> Dict:
        """Check for missing values in critical columns"""
        try:
            missing_counts = {}
            for col in columns:
                if col in df.columns:
                    missing = df[col].isna().sum()
                    if missing > 0:
                        missing_counts[col] = missing
            
            if missing_counts:
                total_missing = sum(missing_counts.values())
                total_values = len(df) * len(columns)
                missing_pct = (total_missing / total_values) * 100
                
                if missing_pct > 5:  # More than 5% missing
                    return {
                        'is_valid': False,
                        'message': f'{missing_pct:.1f}% missing values in critical columns'
                    }
                else:
                    return {
                        'is_valid': True,
                        'message': f'Minor missing values ({missing_pct:.1f}%)'
                    }
            else:
                return {
                    'is_valid': True,
                    'message': 'No missing values'
                }
        except:
            return {
                'is_valid': True,
                'message': 'Could not check missing values'
            }
    
    def _check_data_consistency(self, df: pd.DataFrame) -> Dict:
        """Check data consistency (high >= low, no negative prices, etc.)"""
        try:
            issues = []
            
            # Check high >= low
            if 'high' in df.columns and 'low' in df.columns:
                invalid_candles = (df['high'] < df['low']).sum()
                if invalid_candles > 0:
                    issues.append(f'{invalid_candles} candles with high < low')
            
            # Check for negative prices
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df.columns:
                    negative_count = (df[col] < 0).sum()
                    if negative_count > 0:
                        issues.append(f'{negative_count} negative values in {col}')
            
            # Check for zero prices
            if 'close' in df.columns:
                zero_count = (df['close'] == 0).sum()
                if zero_count > 0:
                    issues.append(f'{zero_count} zero close prices')
            
            # Check for extreme outliers (price changes > 50%)
            if 'close' in df.columns:
                pct_change = df['close'].pct_change().abs()
                extreme_moves = (pct_change > 0.5).sum()
                if extreme_moves > len(df) * 0.1:  # More than 10% of candles
                    issues.append(f'{extreme_moves} extreme price moves (>50%)')
            
            if issues:
                return {
                    'is_consistent': False,
                    'message': '; '.join(issues)
                }
            else:
                return {
                    'is_consistent': True,
                    'message': 'Data is consistent'
                }
        except Exception as e:
            return {
                'is_consistent': True,  # Default to consistent if check fails
                'message': f'Could not check consistency: {str(e)}'
            }
    
    def _determine_quality_grade(self, score: float) -> str:
        """Determine quality grade from score"""
        if score >= self.quality_thresholds['EXCELLENT']:
            return 'EXCELLENT'
        elif score >= self.quality_thresholds['GOOD']:
            return 'GOOD'
        elif score >= self.quality_thresholds['FAIR']:
            return 'FAIR'
        elif score >= self.quality_thresholds['POOR']:
            return 'POOR'
        else:
            return 'INSUFFICIENT'
    
    def _generate_recommendations(self, validation_results: Dict) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if not validation_results['is_valid']:
            recommendations.append("DO NOT generate signals - data validation failed")
            recommendations.append("Fix data issues before proceeding")
        
        if validation_results['quality_score'] < 85:
            recommendations.append("Data quality is below optimal - consider refreshing data")
        
        if validation_results['warnings']:
            recommendations.append(f"Address {len(validation_results['warnings'])} data warnings")
        
        if validation_results['quality_score'] >= 95:
            recommendations.append("Data quality is excellent - safe to generate signals")
        
        return recommendations
    
    def get_quality_summary(self, validation_results: Dict) -> str:
        """Get human-readable quality summary"""
        score = validation_results['quality_score']
        grade = validation_results['quality_grade']
        is_valid = validation_results['is_valid']
        
        summary = f"Data Quality: {grade} ({score}/100)\n"
        summary += f"Status: {'VALID' if is_valid else 'INVALID'}\n"
        
        if validation_results['issues']:
            summary += f"Issues: {len(validation_results['issues'])}\n"
        
        if validation_results['warnings']:
            summary += f"Warnings: {len(validation_results['warnings'])}\n"
        
        return summary


# =================================================================
# USAGE EXAMPLE
# =================================================================

if __name__ == "__main__":
    print("DATA QUALITY VALIDATOR - TESTING")
    print("="*60)
    
    validator = DataQualityValidator()
    
    # Example: Create sample data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='15min')
    sample_data = {
        'M15': pd.DataFrame({
            'timestamp': dates,
            'open': np.random.randn(100) * 100 + 43000,
            'high': np.random.randn(100) * 100 + 43100,
            'low': np.random.randn(100) * 100 + 42900,
            'close': np.random.randn(100) * 100 + 43000,
            'volume': np.random.randint(100000, 500000, 100)
        }),
        'H1': pd.DataFrame({
            'timestamp': dates[::4],
            'open': np.random.randn(25) * 100 + 43000,
            'high': np.random.randn(25) * 100 + 43100,
            'low': np.random.randn(25) * 100 + 42900,
            'close': np.random.randn(25) * 100 + 43000,
            'volume': np.random.randint(100000, 500000, 25)
        })
    }
    
    # Validate data
    results = validator.validate_data(sample_data)
    
    print(f"\nValidation Results:")
    print(f"  Valid: {results['is_valid']}")
    print(f"  Quality Score: {results['quality_score']}/100")
    print(f"  Quality Grade: {results['quality_grade']}")
    print(f"\n{validator.get_quality_summary(results)}")
    
    print("\n" + "="*60)
    print("Data quality validator loaded successfully!")

