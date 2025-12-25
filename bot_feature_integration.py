"""
Advanced Feature Integration for Telegram Trading Bot
Integrates Portfolio Optimizer and Market Structure Analyzer into existing bot
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the new advanced features
try:
    from portfolio_optimizer import PortfolioOptimizer
    from market_structure_analyzer import MarketStructureAnalyzer
    print("[OK] Advanced features imported successfully")
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"[!] Advanced features not available: {e}")
    ADVANCED_FEATURES_AVAILABLE = False
    PortfolioOptimizer = None
    MarketStructureAnalyzer = None

# Import existing bot components
try:
    from user_manager import UserManager
    from trade_tracker import TradeTracker
    from paper_trading import PaperTrading
    print("[OK] Existing bot components imported")
except ImportError as e:
    print(f"[!] Some bot components not available: {e}")

# Initialize new feature instances
if ADVANCED_FEATURES_AVAILABLE:
    portfolio_optimizer = PortfolioOptimizer()
    market_analyzer = MarketStructureAnalyzer()
else:
    portfolio_optimizer = None
    market_analyzer = None


# ============================================================================
# NEW COMMAND HANDLERS FOR ADVANCED FEATURES
# ============================================================================

async def portfolio_optimize_command(update, context):
    """
    /portfolio_optimize - Analyze and optimize portfolio allocation
    Enhanced with Modern Portfolio Theory
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    try:
        # Check if advanced features are available
        if not ADVANCED_FEATURES_AVAILABLE:
            await update.message.reply_text(
                "❌ *Advanced Portfolio Features Not Available*\n\n"
                "Portfolio optimization requires additional modules.\n"
                "Contact support for assistance.",
                parse_mode='Markdown'
            )
            return
        
        # Check user tier access
        user_manager = UserManager()
        user_tier = user_manager.get_user_tier(user_id)
        
        # Portfolio optimization available for Premium+ users
        if user_tier == 'free':
            await update.message.reply_text(
                "🔒 *Premium Feature*\n\n"
                "Portfolio optimization is available for Premium and VIP subscribers.\n\n"
                "💳 `/subscribe` - Upgrade your plan\n"
                "📊 Get scientific portfolio allocation recommendations!",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text(
            "🎯 *Analyzing Your Portfolio...*\n\n"
            "⏳ Calculating correlations and optimal weights...\n"
            "📊 This may take a few moments.",
            parse_mode='Markdown'
        )
        
        # Get current user positions (mock data for demo - integrate with real positions)
        current_positions = {
            'EURUSD': 0.25,
            'GBPUSD': 0.20,
            'USDJPY': 0.15,
            'AUDUSD': 0.20,
            'GOLD': 0.15,
            'BTC': 0.05
        }
        
        # Perform portfolio optimization
        optimization_results = portfolio_optimizer.optimize_portfolio_weights(current_positions)
        
        if optimization_results.get('error'):
            await update.message.reply_text(
                f"❌ *Optimization Failed*\n\n"
                f"Error: {optimization_results['error']}\n\n"
                "Please try again later or contact support.",
                parse_mode='Markdown'
            )
            return
        
        # Format results
        if optimization_results.get('success'):
            metrics = optimization_results['portfolio_metrics']
            recommendations = optimization_results.get('recommendations', [])
            
            msg = f"""
🎯 *PORTFOLIO OPTIMIZATION RESULTS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *Portfolio Metrics:*
• Expected Return: {metrics['expected_return']:.1%}
• Volatility: {metrics['volatility']:.1%}
• Sharpe Ratio: {metrics['sharpe_ratio']:.2f}

📊 *Optimal Weights:*
"""
            
            for asset, weight in optimization_results['optimal_weights'].items():
                msg += f"• {asset}: {weight:.1%}\n"
            
            if recommendations:
                msg += f"\n🔧 *Rebalancing Recommendations:*\n"
                for rec in recommendations[:5]:  # Top 5 recommendations
                    action_emoji = "📈" if rec['action'] == 'increase' else "📉"
                    msg += f"{action_emoji} {rec['asset']}: {rec['action']} by {abs(rec['change']):.1%}\n"
            
            msg += f"""
🎲 *Diversification Score:* {optimization_results.get('diversification_score', 0)}/100

💡 *Next Steps:*
• Use `/correlation` to see asset relationships
• Use `/market_structure <pair>` for timing
• Consider `/risk` calculator for position sizing
"""
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "❌ *Optimization Incomplete*\n\n"
                "Unable to generate recommendations at this time.\n"
                "Please try again later.",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error in Portfolio Optimization*\n\n"
            f"Technical error: {str(e)[:100]}...\n\n"
            "Please try again or contact support.",
            parse_mode='Markdown'
        )


async def market_structure_command(update, context):
    """
    /market_structure <pair> - Analyze market structure for trading pair
    Advanced support/resistance and phase analysis
    """
    user_id = update.effective_user.id
    
    try:
        # Check if advanced features are available
        if not ADVANCED_FEATURES_AVAILABLE:
            await update.message.reply_text(
                "❌ *Advanced Market Structure Features Not Available*\n\n"
                "Market structure analysis requires additional modules.\n"
                "Contact support for assistance.",
                parse_mode='Markdown'
            )
            return
        
        # Check user tier access
        user_manager = UserManager()
        user_tier = user_manager.get_user_tier(user_id)
        
        # Market structure available for Premium+ users
        if user_tier == 'free':
            await update.message.reply_text(
                "🔒 *Premium Feature*\n\n"
                "Market structure analysis is available for Premium and VIP subscribers.\n\n"
                "💳 `/subscribe` - Upgrade your plan\n"
                "📊 Get professional market structure insights!",
                parse_mode='Markdown'
            )
            return
        
        # Parse symbol argument
        if context.args:
            symbol = context.args[0].upper()
            # Map common names to proper symbols
            symbol_mapping = {
                'EUR': 'EURUSD', 'EURUSD': 'EURUSD',
                'GBP': 'GBPUSD', 'GBPUSD': 'GBPUSD',
                'USD': 'USDJPY', 'USDJPY': 'USDJPY',
                'AUD': 'AUDUSD', 'AUDUSD': 'AUDUSD',
                'BTC': 'BTCUSDT', 'BTCUSDT': 'BTCUSDT',
                'GOLD': 'XAUUSD', 'XAUUSD': 'XAUUSD'
            }
            symbol = symbol_mapping.get(symbol, symbol)
        else:
            await update.message.reply_text(
                "📊 *Market Structure Analysis*\n\n"
                "*Usage:* `/market_structure <pair>`\n\n"
                "*Examples:*\n"
                "• `/market_structure EURUSD`\n"
                "• `/market_structure BTC`\n"
                "• `/market_structure GOLD`\n\n"
                "*Available Assets:*\n"
                "🪙 BTC, 🥇 GOLD\n"
                "💱 EURUSD, GBPUSD, USDJPY, AUDUSD\n"
                "📈 ES, NQ (Futures)",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text(
            f"📊 *Analyzing Market Structure...*\n\n"
            f"🔍 Asset: {symbol}\n"
            f"⏳ Identifying key levels and market phase...\n"
            f"📈 This may take a few moments.",
            parse_mode='Markdown'
        )
        
        # Generate market structure report
        report = market_analyzer.generate_structure_report(symbol)
        
        if 'error' in report:
            await update.message.reply_text(
                f"❌ *Analysis Failed*\n\n"
                f"Unable to analyze {symbol}\n"
                f"Error: {report['error']}\n\n"
                "Please try a different symbol or try again later.",
                parse_mode='Markdown'
            )
            return
        
        # Format the comprehensive report
        msg = f"""
📊 *MARKET STRUCTURE ANALYSIS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *{report['symbol']}*
💰 Current Price: {report['current_price']:.5f}
📈 Change: {report['price_change_pct']:+.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 *MARKET PHASE*
Phase: {report['market_phase']['phase'].upper()}
Confidence: {report['market_phase']['confidence']}%
"""
        
        if report['market_phase']['trend_direction'] != 'neutral':
            trend_emoji = "📈" if report['market_phase']['trend_direction'] == 'bullish' else "📉"
            msg += f"Trend: {trend_emoji} {report['market_phase']['trend_direction'].upper()}\n"
        
        # Support and Resistance levels
        structure = report['market_structure']
        
        if structure.get('nearest_resistance'):
            resistance = structure['nearest_resistance']
            distance = ((resistance['price'] - report['current_price']) / report['current_price']) * 100
            msg += f"\n🔴 *Nearest Resistance:* {resistance['price']:.5f}\n"
            msg += f"   Distance: {distance:.2f}% above\n"
            msg += f"   Strength: {resistance.get('touches', 1)} touches\n"
        
        if structure.get('nearest_support'):
            support = structure['nearest_support']
            distance = ((report['current_price'] - support['price']) / report['current_price']) * 100
            msg += f"\n🟢 *Nearest Support:* {support['price']:.5f}\n"
            msg += f"   Distance: {distance:.2f}% below\n"
            msg += f"   Strength: {support.get('touches', 1)} touches\n"
        
        # Session information
        session_info = report['session_info']
        if session_info['active_sessions']:
            msg += f"\n⏰ *Active Sessions:* {', '.join(session_info['active_sessions']).title()}\n"
            msg += f"📊 Volatility Expected: {session_info['volatility_expectation'].upper()}\n"
        
        # Trading recommendations
        if report['recommendations']:
            msg += f"\n💡 *TRADING RECOMMENDATIONS:*\n"
            for i, rec in enumerate(report['recommendations'][:3], 1):  # Top 3 recommendations
                msg += f"{i}. {rec}\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *Analysis Quality:*
• Data Points: {report['analysis_quality']['data_points']}
• Confidence: {report['analysis_quality']['phase_confidence']}%
• Pivot Points: {report['analysis_quality']['pivot_points_found']}

💡 *Combine with:*
• `/correlation` for pair analysis
• `/aipredict {symbol.lower()}` for ML insights
• `/risk` for position sizing
"""
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error in Market Structure Analysis*\n\n"
            f"Technical error: {str(e)[:100]}...\n\n"
            "Please try again or contact support.",
            parse_mode='Markdown'
        )


async def session_analysis_command(update, context):
    """
    /session_analysis - Current trading session analysis
    """
    user_id = update.effective_user.id
    
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            await update.message.reply_text(
                "❌ *Session Analysis Not Available*\n\n"
                "This feature requires advanced modules.",
                parse_mode='Markdown'
            )
            return
        
        # Get current session information
        session_info = market_analyzer.get_active_session()
        
        msg = f"""
⏰ *TRADING SESSION ANALYSIS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 *Current UTC Time:* {datetime.utcnow().strftime('%H:%M')}

🌍 *Active Sessions:*
"""
        
        if session_info['active_sessions']:
            for session in session_info['active_sessions']:
                session_emoji = {
                    'sydney': '🇦🇺',
                    'tokyo': '🇯🇵', 
                    'london': '🇬🇧',
                    'new_york': '🇺🇸'
                }
                msg += f"{session_emoji.get(session, '🌍')} {session.title()}\n"
        else:
            msg += "• No major sessions currently active\n"
        
        msg += f"""
📊 *Volatility Expectation:* {session_info['volatility_expectation'].upper()}
🔗 *Session Overlap:* {'YES' if session_info['session_overlaps'] else 'NO'}

💱 *Recommended Pairs:*
"""
        
        if session_info['recommended_pairs']:
            for pair in session_info['recommended_pairs']:
                msg += f"• {pair}\n"
        else:
            msg += "• Standard major pairs (EURUSD, GBPUSD, USDJPY)\n"
        
        # Trading tips based on session
        if session_info['volatility_expectation'] == 'high':
            msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 *HIGH VOLATILITY PERIOD*
💡 *Trading Tips:*
• Reduce position sizes by 25-50%
• Use wider stop losses
• Watch for breakouts and strong moves
• Best time for trend-following strategies
"""
        elif session_info['volatility_expectation'] == 'medium':
            msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *MODERATE VOLATILITY PERIOD*
💡 *Trading Tips:*
• Standard position sizing
• Good for scalping strategies
• Monitor key levels closely
"""
        else:
            msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

😴 *LOW VOLATILITY PERIOD*
💡 *Trading Tips:*
• Consider range-bound strategies
• Be patient for better setups
• Good time for analysis and planning
"""
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error in Session Analysis*\n\n"
            f"Technical error: {str(e)[:50]}...",
            parse_mode='Markdown'
        )


async def portfolio_risk_command(update, context):
    """
    /portfolio_risk - Analyze portfolio risk concentration
    """
    user_id = update.effective_user.id
    
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            await update.message.reply_text(
                "❌ *Portfolio Risk Analysis Not Available*\n\n"
                "This feature requires advanced modules.",
                parse_mode='Markdown'
            )
            return
        
        # Check user tier access
        user_manager = UserManager()
        user_tier = user_manager.get_user_tier(user_id)
        
        if user_tier == 'free':
            await update.message.reply_text(
                "🔒 *Premium Feature*\n\n"
                "Portfolio risk analysis is available for Premium and VIP subscribers.\n\n"
                "💳 `/subscribe` - Upgrade your plan",
                parse_mode='Markdown'
            )
            return
        
        # Mock current positions for demo
        current_positions = {
            'EURUSD': 0.30,
            'GBPUSD': 0.25,
            'USDJPY': 0.15,
            'AUDUSD': 0.15,
            'GOLD': 0.10,
            'BTC': 0.05
        }
        
        # Analyze risk concentration
        risk_analysis = portfolio_optimizer.analyze_risk_concentration(current_positions)
        
        msg = f"""
⚖️ *PORTFOLIO RISK ANALYSIS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Concentration Metrics:*
• Concentration Index: {risk_analysis['herfindahl_index']:.3f}
• Effective Assets: {risk_analysis['effective_assets']:.1f}
• Largest Position: {risk_analysis['max_weight']:.1%} ({risk_analysis['max_weight_asset']})

🔗 *Correlation Exposure:*
"""
        
        for asset, exposure in risk_analysis['correlation_exposure'].items():
            if exposure > 0.1:  # Only show significant exposures
                msg += f"• {asset}: {exposure:.1%}\n"
        
        # Risk level assessment
        if risk_analysis['herfindahl_index'] > 0.5:
            risk_level = "🔴 HIGH"
        elif risk_analysis['herfindahl_index'] > 0.3:
            risk_level = "🟡 MODERATE"
        else:
            risk_level = "🟢 LOW"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *Overall Risk Level:* {risk_level}
"""
        
        # Warnings and recommendations
        if risk_analysis['warnings']:
            msg += f"\n⚠️ *Risk Warnings:*\n"
            for warning in risk_analysis['warnings'][:3]:  # Top 3 warnings
                msg += f"• {warning}\n"
        
        msg += f"""
💡 *Recommendations:*
• Use `/portfolio_optimize` for rebalancing
• Monitor correlation with `/correlation`
• Consider diversification across asset classes
• Review position sizes regularly
"""
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error in Risk Analysis*\n\n"
            f"Technical error: {str(e)[:50]}...",
            parse_mode='Markdown'
        )


async def correlation_matrix_command(update, context):
    """
    /correlation_matrix - View enhanced asset correlation matrix
    """
    user_id = update.effective_user.id
    
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            await update.message.reply_text(
                "❌ *Enhanced Correlation Analysis Not Available*\n\n"
                "This feature requires advanced modules.\n"
                "You can still use the basic `/correlation` command.",
                parse_mode='Markdown'
            )
            return
        
        # Check user tier
        user_manager = UserManager()
        user_tier = user_manager.get_user_tier(user_id)
        
        if user_tier == 'free':
            await update.message.reply_text(
                "🔒 *Premium Feature*\n\n"
                "Enhanced correlation analysis is available for Premium and VIP subscribers.\n\n"
                "💳 `/subscribe` - Upgrade your plan\n"
                "🆓 Try basic `/correlation` for major pairs",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text(
            "🔗 *Calculating Asset Correlations...*\n\n"
            "⏳ Analyzing relationships between all trading pairs...",
            parse_mode='Markdown'
        )
        
        # Calculate correlation analysis
        correlation_results = portfolio_optimizer.calculate_asset_correlations()
        
        msg = f"""
🔗 *ASSET CORRELATION MATRIX*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *Diversification Score:* {correlation_results['diversification_score']}/100

🔴 *HIGH CORRELATION PAIRS (>70%):*
"""
        
        high_corr_pairs = correlation_results.get('high_correlation_pairs', [])
        if high_corr_pairs:
            for pair in high_corr_pairs[:5]:  # Top 5 highest correlations
                corr_emoji = "📈" if pair['relationship'] == 'positive' else "📉"
                msg += f"{corr_emoji} {pair['asset1']} - {pair['asset2']}: {pair['correlation']:.2f}\n"
        else:
            msg += "• No pairs with correlation >70%\n"
        
        # Correlation clusters
        clusters = correlation_results.get('correlation_clusters', {})
        if clusters:
            msg += f"\n🎪 *CORRELATION CLUSTERS:*\n"
            for cluster_id, cluster_info in clusters.items():
                msg += f"• Cluster {cluster_id[-1]}: {len(cluster_info['assets'])} assets\n"
                msg += f"  Average correlation: {cluster_info['avg_correlation']:.2f}\n"
        
        # Trading implications
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *TRADING IMPLICATIONS:*

🟢 *Low Risk Pairs* (correlation <30%):
• Good for diversification
• Can trade simultaneously

🟡 *Moderate Risk Pairs* (30-70%):
• Monitor for conflicts
• Reduce combined position sizes

🔴 *High Risk Pairs* (>70%):
• Avoid simultaneous trades
• Choose strongest signal only

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠️ *Related Commands:*
• `/portfolio_optimize` - Optimize allocation
• `/portfolio_risk` - Risk concentration analysis
• `/market_structure <pair>` - Individual analysis
"""
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error in Correlation Analysis*\n\n"
            f"Technical error: {str(e)[:50]}...",
            parse_mode='Markdown'
        )


# ============================================================================
# ENHANCED HELP COMMAND WITH NEW FEATURES
# ============================================================================

def get_advanced_features_help():
    """Get help text for advanced features"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return ""
    
    return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *ADVANCED ANALYTICS* ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎲 `/portfolio_optimize` → Scientific portfolio optimization
📊 `/market_structure <pair>` → Advanced market structure
⏰ `/session_analysis` → Current session analysis
⚖️ `/portfolio_risk` → Portfolio risk concentration
🔗 `/correlation_matrix` → Enhanced correlation analysis

*Available for Premium+ subscribers*
"""


# ============================================================================
# INTEGRATION HELPER FUNCTIONS
# ============================================================================

def add_advanced_command_handlers(app):
    """
    Add advanced feature command handlers to the bot application
    Call this function from telegram_bot.py main() function
    """
    if not ADVANCED_FEATURES_AVAILABLE:
        print("[!] Advanced features not available - skipping command handler registration")
        return
    
    from telegram.ext import CommandHandler
    
    # Add new command handlers
    app.add_handler(CommandHandler("portfolio_optimize", portfolio_optimize_command))
    app.add_handler(CommandHandler("market_structure", market_structure_command))
    app.add_handler(CommandHandler("session_analysis", session_analysis_command))
    app.add_handler(CommandHandler("portfolio_risk", portfolio_risk_command))
    app.add_handler(CommandHandler("correlation_matrix", correlation_matrix_command))
    
    print("[OK] Advanced feature command handlers registered")


def get_advanced_features_status():
    """Get status of advanced features for monitoring"""
    return {
        'advanced_features_available': ADVANCED_FEATURES_AVAILABLE,
        'portfolio_optimizer_ready': portfolio_optimizer is not None,
        'market_analyzer_ready': market_analyzer is not None,
        'features_count': 5 if ADVANCED_FEATURES_AVAILABLE else 0
    }


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_advanced_features():
    """Test advanced features functionality"""
    if not ADVANCED_FEATURES_AVAILABLE:
        print("❌ Advanced features not available for testing")
        return False
    
    try:
        # Test portfolio optimizer
        test_positions = {'EURUSD': 0.5, 'GBPUSD': 0.5}
        optimization_result = portfolio_optimizer.optimize_portfolio_weights(test_positions)
        
        # Test market analyzer
        test_report = market_analyzer.generate_structure_report('EURUSD')
        
        print("✅ Advanced features tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the integration
    print("=" * 50)
    print("🧪 Testing Advanced Features Integration")
    print("=" * 50)
    
    status = get_advanced_features_status()
    print(f"Advanced Features Available: {status['advanced_features_available']}")
    print(f"Portfolio Optimizer Ready: {status['portfolio_optimizer_ready']}")
    print(f"Market Analyzer Ready: {status['market_analyzer_ready']}")
    print(f"Total New Features: {status['features_count']}")
    
    if ADVANCED_FEATURES_AVAILABLE:
        print("\n🧪 Running feature tests...")
        test_success = test_advanced_features()
        print(f"Test Result: {'✅ PASSED' if test_success else '❌ FAILED'}")
    
    print("\n✅ Integration module ready for telegram_bot.py")
