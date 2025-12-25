"""
AI Adaptive Trading Strategies
Implements reinforcement learning and adaptive algorithms for dynamic strategy optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import random
import logging
from datetime import datetime, timedelta
from collections import deque
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdaptiveStrategyManager:
    """Manages adaptive trading strategies using reinforcement learning"""

    def __init__(self, strategy_dir: str = "adaptive_strategies"):
        self.strategy_dir = strategy_dir
        self.strategies = {}
        self.performance_history = {}
        self.market_regime_memory = deque(maxlen=1000)

        if not os.path.exists(strategy_dir):
            os.makedirs(strategy_dir)

        # Initialize strategy parameters
        self._load_strategies()

    def _load_strategies(self):
        """Load existing adaptive strategies"""
        strategy_file = f"{self.strategy_dir}/strategies.json"
        if os.path.exists(strategy_file):
            try:
                with open(strategy_file, 'r') as f:
                    self.strategies = json.load(f)
                logger.info(f"Loaded {len(self.strategies)} adaptive strategies")
            except Exception as e:
                logger.error(f"Error loading strategies: {e}")
                self.strategies = {}

    def _save_strategies(self):
        """Save adaptive strategies to disk"""
        strategy_file = f"{self.strategy_dir}/strategies.json"
        try:
            with open(strategy_file, 'w') as f:
                json.dump(self.strategies, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving strategies: {e}")

    def create_adaptive_strategy(self, base_strategy: Dict, asset_symbol: str) -> Dict:
        """Create an adaptive version of a base trading strategy"""
        strategy_id = f"{asset_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        adaptive_strategy = {
            'id': strategy_id,
            'asset': asset_symbol,
            'base_strategy': base_strategy,
            'created_at': datetime.now(),
            'performance': {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            },
            'adaptation_params': {
                'learning_rate': 0.1,
                'exploration_rate': 0.1,
                'discount_factor': 0.95,
                'regime_sensitivity': 0.8
            },
            'regime_adaptations': {
                'bull_market': {},
                'bear_market': {},
                'sideways_market': {},
                'high_volatility': {},
                'low_volatility': {}
            },
            'active': True
        }

        self.strategies[strategy_id] = adaptive_strategy
        self._save_strategies()

        logger.info(f"Created adaptive strategy {strategy_id} for {asset_symbol}")
        return adaptive_strategy

    def adapt_strategy_to_market(self, strategy_id: str, market_data: pd.DataFrame,
                                current_regime: Dict) -> Dict:
        """Adapt strategy parameters based on current market conditions"""
        if strategy_id not in self.strategies:
            return {'error': f'Strategy {strategy_id} not found'}

        strategy = self.strategies[strategy_id]
        regime = current_regime.get('regime', 'unknown')

        # Store market regime for learning
        self.market_regime_memory.append({
            'timestamp': datetime.now(),
            'regime': regime,
            'volatility': current_regime.get('volatility', 0),
            'trend_strength': current_regime.get('trend_strength', 0)
        })

        # Adapt parameters based on regime
        adapted_params = self._calculate_adapted_parameters(strategy, regime, market_data)

        # Update strategy with adapted parameters
        strategy['adapted_params'] = adapted_params
        strategy['last_adaptation'] = datetime.now()

        self._save_strategies()

        return {
            'strategy_id': strategy_id,
            'regime': regime,
            'adapted_params': adapted_params,
            'adaptation_reason': f'Adapted for {regime} market conditions'
        }

    def _calculate_adapted_parameters(self, strategy: Dict, regime: str,
                                    market_data: pd.DataFrame) -> Dict:
        """Calculate optimal parameters for current market regime"""
        base_params = strategy.get('base_strategy', {})
        adaptation_history = strategy.get('regime_adaptations', {})

        # Base adaptations for different regimes
        regime_adaptations = {
            'bull_market': {
                'stop_loss_multiplier': 1.5,  # Wider stops in trending markets
                'take_profit_multiplier': 2.0,  # Higher targets in bull markets
                'position_size_multiplier': 1.2,  # Slightly larger positions
                'entry_confidence_threshold': 0.75
            },
            'bear_market': {
                'stop_loss_multiplier': 1.2,
                'take_profit_multiplier': 1.8,
                'position_size_multiplier': 1.1,
                'entry_confidence_threshold': 0.8  # More conservative entries
            },
            'sideways_market': {
                'stop_loss_multiplier': 0.8,  # Tighter stops in ranging markets
                'take_profit_multiplier': 1.2,  # Lower targets
                'position_size_multiplier': 0.9,  # Smaller positions
                'entry_confidence_threshold': 0.85  # Very conservative
            },
            'high_volatility': {
                'stop_loss_multiplier': 1.8,  # Much wider stops
                'take_profit_multiplier': 2.5,  # Higher targets
                'position_size_multiplier': 0.7,  # Smaller positions for safety
                'entry_confidence_threshold': 0.9
            },
            'low_volatility': {
                'stop_loss_multiplier': 0.6,  # Tighter stops
                'take_profit_multiplier': 1.5,
                'position_size_multiplier': 1.3,  # Larger positions when volatility is low
                'entry_confidence_threshold': 0.7
            }
        }

        # Get base adaptations
        adapted = regime_adaptations.get(regime, {}).copy()

        # Apply learning from historical performance
        if regime in adaptation_history and adaptation_history[regime]:
            learned_params = self._apply_learning(adaptation_history[regime], regime)
            adapted.update(learned_params)

        # Add market-specific adjustments
        volatility = market_data['close'].pct_change().rolling(20).std().iloc[-1]
        if volatility > 0.03:  # High volatility threshold
            adapted['stop_loss_multiplier'] = adapted.get('stop_loss_multiplier', 1.0) * 1.3
            adapted['position_size_multiplier'] = adapted.get('position_size_multiplier', 1.0) * 0.8

        return adapted

    def _apply_learning(self, historical_performance: Dict, regime: str) -> Dict:
        """Apply reinforcement learning from historical performance"""
        # Simple Q-learning style adaptation
        learning_rate = 0.1

        if 'win_rate' in historical_performance:
            win_rate = historical_performance['win_rate']

            # Adjust position sizing based on win rate
            if win_rate > 0.7:
                position_adjustment = learning_rate * 0.2  # Increase position size
            elif win_rate < 0.5:
                position_adjustment = -learning_rate * 0.3  # Decrease position size
            else:
                position_adjustment = 0

            # Adjust confidence threshold
            if win_rate > 0.8:
                confidence_adjustment = -learning_rate * 0.05  # Can be less conservative
            elif win_rate < 0.6:
                confidence_adjustment = learning_rate * 0.1  # Be more conservative
            else:
                confidence_adjustment = 0

            return {
                'position_size_learning': position_adjustment,
                'confidence_threshold_learning': confidence_adjustment
            }

        return {}

    def update_strategy_performance(self, strategy_id: str, trade_result: Dict):
        """Update strategy performance and learn from results"""
        if strategy_id not in self.strategies:
            return

        strategy = self.strategies[strategy_id]

        # Update performance metrics
        perf = strategy['performance']
        perf['total_trades'] += 1

        if trade_result.get('pnl', 0) > 0:
            # Track win rate
            current_wins = perf.get('wins', 0) + 1
            perf['wins'] = current_wins
            perf['win_rate'] = current_wins / perf['total_trades']

        # Update profit factor
        total_pnl = perf.get('total_pnl', 0) + trade_result.get('pnl', 0)
        total_losses = abs(sum([t.get('pnl', 0) for t in [] if t.get('pnl', 0) < 0]))  # Would track losses
        if total_losses > 0:
            perf['profit_factor'] = abs(total_pnl) / total_losses

        # Store regime-specific performance
        current_regime = self._get_current_regime()
        if current_regime:
            regime_key = current_regime.get('regime', 'unknown')
            if regime_key not in strategy['regime_adaptations']:
                strategy['regime_adaptations'][regime_key] = {}

            regime_perf = strategy['regime_adaptations'][regime_key]
            regime_perf['trades'] = regime_perf.get('trades', 0) + 1

            if trade_result.get('pnl', 0) > 0:
                regime_perf['wins'] = regime_perf.get('wins', 0) + 1

            regime_perf['total_pnl'] = regime_perf.get('total_pnl', 0) + trade_result.get('pnl', 0)

            # Calculate regime-specific win rate
            if regime_perf['trades'] > 0:
                regime_perf['win_rate'] = regime_perf['wins'] / regime_perf['trades']

        self._save_strategies()

    def _get_current_regime(self) -> Optional[Dict]:
        """Get current market regime from memory"""
        if self.market_regime_memory:
            return self.market_regime_memory[-1]
        return None

    def get_strategy_recommendation(self, strategy_id: str, market_conditions: Dict) -> Dict:
        """Get AI recommendation for strategy execution"""
        if strategy_id not in self.strategies:
            return {'error': f'Strategy {strategy_id} not found'}

        strategy = self.strategies[strategy_id]
        current_regime = market_conditions.get('regime', 'unknown')

        # Get adapted parameters
        adapted_params = strategy.get('adapted_params', {})

        # Generate recommendation based on learning
        recommendation = {
            'strategy_id': strategy_id,
            'recommended_action': 'hold',
            'confidence': 0.5,
            'risk_level': 'medium',
            'rationale': []
        }

        # Analyze market conditions vs historical performance
        regime_perf = strategy.get('regime_adaptations', {}).get(current_regime, {})

        if regime_perf:
            win_rate = regime_perf.get('win_rate', 0)
            total_pnl = regime_perf.get('total_pnl', 0)

            if win_rate > 0.7 and total_pnl > 0:
                recommendation['recommended_action'] = 'enter'
                recommendation['confidence'] = min(win_rate, 0.95)
                recommendation['rationale'].append(f"Strong historical performance in {current_regime} ({win_rate:.1%} win rate)")
            elif win_rate < 0.4:
                recommendation['recommended_action'] = 'avoid'
                recommendation['confidence'] = 0.8
                recommendation['rationale'].append(f"Poor historical performance in {current_regime} ({win_rate:.1%} win rate)")

        # Add risk assessment
        volatility = market_conditions.get('volatility', 0)
        if volatility > 0.03:
            recommendation['risk_level'] = 'high'
            recommendation['rationale'].append("High market volatility detected")
        elif volatility < 0.01:
            recommendation['risk_level'] = 'low'
            recommendation['rationale'].append("Low market volatility - favorable conditions")

        return recommendation

    def optimize_strategy_portfolio(self, available_strategies: List[str],
                                  market_data: Dict) -> Dict:
        """Optimize portfolio allocation across adaptive strategies"""
        if not available_strategies:
            return {'error': 'No strategies available'}

        # Simple portfolio optimization based on recent performance
        strategy_weights = {}
        total_weight = 0

        for strategy_id in available_strategies:
            if strategy_id in self.strategies:
                strategy = self.strategies[strategy_id]
                perf = strategy.get('performance', {})

                # Calculate weight based on win rate and profit factor
                win_rate = perf.get('win_rate', 0)
                profit_factor = perf.get('profit_factor', 1)

                # Risk-adjusted weight
                weight = (win_rate * profit_factor) / (1 + perf.get('max_drawdown', 0))

                strategy_weights[strategy_id] = max(weight, 0.05)  # Minimum weight
                total_weight += strategy_weights[strategy_id]

        # Normalize weights
        if total_weight > 0:
            strategy_weights = {k: v/total_weight for k, v in strategy_weights.items()}

        return {
            'portfolio_allocation': strategy_weights,
            'total_strategies': len(available_strategies),
            'optimization_method': 'risk_adjusted_performance'
        }


class ReinforcementLearningTrader:
    """Reinforcement learning agent for trading decisions"""

    def __init__(self, state_space: int = 10, action_space: int = 3):
        self.state_space = state_space  # Number of state features
        self.action_space = action_space  # Actions: buy, sell, hold

        # Q-learning parameters
        self.q_table = np.zeros((state_space, action_space))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.exploration_rate = 1.0
        self.exploration_decay = 0.995
        self.min_exploration_rate = 0.01

        # Experience replay
        self.memory = deque(maxlen=10000)
        self.batch_size = 64

    def get_state(self, market_data: pd.DataFrame, position: Dict) -> int:
        """Convert market data and position to discrete state"""
        # Simple state discretization - would be more sophisticated in practice
        recent_return = market_data['close'].pct_change(5).iloc[-1]
        volatility = market_data['close'].pct_change().rolling(10).std().iloc[-1]
        volume_trend = market_data['volume'].pct_change(5).iloc[-1] if 'volume' in market_data else 0

        # Discretize features
        return_bins = [-float('inf'), -0.02, -0.005, 0.005, 0.02, float('inf')]
        vol_bins = [0, 0.01, 0.02, 0.05, float('inf')]
        volume_bins = [-float('inf'), -0.1, 0.1, float('inf')]

        return_state = np.digitize(recent_return, return_bins) - 1
        vol_state = np.digitize(volatility, vol_bins) - 1
        volume_state = np.digitize(volume_trend, volume_bins) - 1

        # Combine into single state (simplified)
        state = (return_state * 5 * 4) + (vol_state * 5) + volume_state
        return min(state, self.state_space - 1)

    def choose_action(self, state: int) -> int:
        """Choose action using epsilon-greedy policy"""
        if random.random() < self.exploration_rate:
            return random.randint(0, self.action_space - 1)
        else:
            return np.argmax(self.q_table[state])

    def learn(self, state: int, action: int, reward: float, next_state: int):
        """Update Q-table using Q-learning"""
        # Q-learning update
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state, best_next_action]
        td_error = td_target - self.q_table[state, action]

        self.q_table[state, action] += self.learning_rate * td_error

        # Decay exploration rate
        self.exploration_rate = max(self.min_exploration_rate,
                                  self.exploration_rate * self.exploration_decay)

    def get_action_name(self, action: int) -> str:
        """Convert action number to name"""
        actions = ['hold', 'buy', 'sell']
        return actions[action] if action < len(actions) else 'hold'

    def get_q_values(self, state: int) -> Dict:
        """Get Q-values for all actions in current state"""
        return {
            'hold': float(self.q_table[state, 0]),
            'buy': float(self.q_table[state, 1]),
            'sell': float(self.q_table[state, 2])
        }


if __name__ == "__main__":
    # Example usage
    manager = AdaptiveStrategyManager()
    rl_trader = ReinforcementLearningTrader()

    print("AI Adaptive Strategies initialized!")
    print("Ready for market-adaptive trading and reinforcement learning")
