"""
Quick Implementation Example for Scalping Commands
Add these functions to your telegram_bot.py file
"""

import importlib.util
import os
from telegram import Update
from telegram.ext import ContextTypes

# ============================================================================
# SCALPING COMMANDS - Add these to telegram_bot.py
# ============================================================================

async def scalp_btc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick BTC scalping signal - Fast analysis, lower threshold"""
    await update.message.reply_text("⚡ Generating quick BTC scalping signal...")
    
    try:
        # Import scalping analyzer
        spec = importlib.util.spec_from_file_location(
            "btc_scalp", 
            os.path.join(os.path.dirname(__file__), 'btc_scalping_analyzer.py')
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        analyzer = module.BTCScalpingAnalyzer()
        signal = analyzer.generate_trading_signal()
        
        if signal and signal.get('direction') != 'HOLD':
            msg = f"⚡ *BTC SCALPING SIGNAL*\n\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"📈 Direction: *{signal['direction']}*\n"
            msg += f"💰 Entry: ${signal.get('entry_price', 'N/A'):,.2f}\n"
            msg += f"🛑 Stop Loss: ${signal.get('stop_loss', 'N/A'):,.2f}\n"
            msg += f"🎯 Take Profit: ${signal.get('take_profit', 'N/A'):,.2f}\n"
            msg += f"📊 Confidence: {signal.get('confidence', 'N/A')}%\n"
            
            # Add risk/reward if available
            if 'risk_reward' in signal:
                msg += f"⚖️ R:R Ratio: {signal['risk_reward']:.2f}\n"
            
            msg += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"⏱️ Valid for: 5-15 minutes\n"
            msg += f"💡 Use /btc for full analysis\n"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "⏳ No scalping signal at this time.\n"
                "💡 Try /btc for full analysis or wait a few minutes."
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating signal: {str(e)}")


async def scalp_gold_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick Gold scalping signal"""
    await update.message.reply_text("⚡ Generating quick Gold scalping signal...")
    
    try:
        spec = importlib.util.spec_from_file_location(
            "gold_scalp",
            os.path.join(os.path.dirname(__file__), 'Gold expert', 'gold_analyzer.py')
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        analyzer = module.GoldScalpingAnalyzer()
        signal = analyzer.generate_trading_signal()
        
        if signal and signal.get('direction') != 'HOLD':
            msg = f"⚡ *GOLD SCALPING SIGNAL*\n\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"📈 Direction: *{signal['direction']}*\n"
            msg += f"💰 Entry: ${signal.get('entry_price', 'N/A'):,.2f}\n"
            msg += f"🛑 Stop Loss: ${signal.get('stop_loss', 'N/A'):,.2f}\n"
            msg += f"🎯 Take Profit: ${signal.get('take_profit', 'N/A'):,.2f}\n"
            msg += f"📊 Confidence: {signal.get('confidence', 'N/A')}%\n"
            msg += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"⏱️ Valid for: 5-15 minutes\n"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text("⏳ No scalping signal. Try /gold for full analysis.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def scalp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick scalping signal for any asset"""
    asset = context.args[0].upper() if context.args else 'BTC'
    
    asset_map = {
        'BTC': ('btc_scalping_analyzer.py', 'BTCScalpingAnalyzer', 'BTC'),
        'GOLD': ('Gold expert/gold_analyzer.py', 'GoldScalpingAnalyzer', 'GOLD'),
        'XAUUSD': ('Gold expert/gold_analyzer.py', 'GoldScalpingAnalyzer', 'GOLD'),
    }
    
    if asset not in asset_map:
        await update.message.reply_text(
            f"❌ Asset '{asset}' not supported for scalping.\n"
            f"✅ Supported: BTC, GOLD, XAUUSD"
        )
        return
    
    await update.message.reply_text(f"⚡ Generating {asset} scalping signal...")
    
    try:
        file_path, class_name, display_name = asset_map[asset]
        spec = importlib.util.spec_from_file_location(
            f"scalp_{asset.lower()}",
            os.path.join(os.path.dirname(__file__), file_path)
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        analyzer_class = getattr(module, class_name)
        analyzer = analyzer_class()
        signal = analyzer.generate_trading_signal()
        
        if signal and signal.get('direction') != 'HOLD':
            msg = f"⚡ *{display_name} SCALPING SIGNAL*\n\n"
            msg += f"📈 {signal['direction']} | Confidence: {signal.get('confidence', 'N/A')}%\n"
            msg += f"💰 Entry: ${signal.get('entry_price', 'N/A'):,.2f}\n"
            msg += f"🛑 SL: ${signal.get('stop_loss', 'N/A'):,.2f}\n"
            msg += f"🎯 TP: ${signal.get('take_profit', 'N/A'):,.2f}\n"
            msg += f"\n⏱️ Quick scalp - Valid 5-15 min"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"⏳ No {display_name} scalping signal. Try /{asset.lower()} for full analysis.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def orderflow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Order flow analysis for quick scalping entries"""
    asset = context.args[0].upper() if context.args else 'BTC'
    
    await update.message.reply_text(f"📊 Analyzing {asset} order flow...")
    
    try:
        # Import order flow analyzer
        from order_flow import OrderFlowAnalyzer
        from volume_profile import VolumeProfileAnalyzer
        from orderbook_analyzer import OrderBookAnalyzer
        
        # Initialize analyzers
        of_analyzer = OrderFlowAnalyzer()
        vp_analyzer = VolumeProfileAnalyzer()
        ob_analyzer = OrderBookAnalyzer()
        
        # Get order flow data
        of_signal = of_analyzer.analyze_order_flow(asset)
        vp_levels = vp_analyzer.identify_hvn_lvn(asset)
        ob_data = ob_analyzer.get_orderbook_imbalance(asset)
        
        msg = f"📊 *{asset} ORDER FLOW ANALYSIS*\n\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Order flow
        if of_signal:
            msg += f"🌊 Order Flow: {of_signal.get('direction', 'N/A')}\n"
            msg += f"   Pressure: {of_signal.get('pressure', 'N/A')}\n"
        
        # Volume profile
        if vp_levels and vp_levels.get('hvn'):
            hvn = vp_levels['hvn'][0] if vp_levels['hvn'] else None
            if hvn:
                msg += f"📈 High Volume Node: ${hvn['price']:,.2f}\n"
        
        # Order book
        if ob_data:
            msg += f"⚖️ Order Book: {ob_data.get('imbalance', 'N/A')}%\n"
            msg += f"   Bias: {ob_data.get('bias', 'N/A')}\n"
        
        msg += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"💡 Use this for quick entry timing"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except ImportError:
        await update.message.reply_text(
            "❌ Order flow modules not available.\n"
            "💡 Install required dependencies or check file paths."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def quick_scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick multi-timeframe scan for scalping opportunities"""
    asset = context.args[0].upper() if context.args else 'BTC'
    
    await update.message.reply_text(f"🔍 Quick scanning {asset} across timeframes...")
    
    try:
        from multi_timeframe_analyzer import MultiTimeframeAnalyzer
        
        analyzer = MultiTimeframeAnalyzer()
        analysis = analyzer.analyze_all_timeframes(asset)
        
        msg = f"🔍 *{asset} QUICK SCAN*\n\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        timeframes = ['1m', '5m', '15m', '1h']
        signals = []
        
        for tf in timeframes:
            if tf in analysis:
                tf_data = analysis[tf]
                direction = tf_data.get('direction', 'N/A')
                signals.append((tf, direction))
                msg += f"{tf:>4}: {direction}\n"
        
        # Check for confluence
        buy_count = sum(1 for _, d in signals if d == 'BUY')
        sell_count = sum(1 for _, d in signals if d == 'SELL')
        
        msg += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if buy_count >= 3:
            msg += f"✅ *BUY CONFLUENCE* ({buy_count}/4 timeframes)\n"
            msg += f"💡 Strong buy opportunity"
        elif sell_count >= 3:
            msg += f"✅ *SELL CONFLUENCE* ({sell_count}/4 timeframes)\n"
            msg += f"💡 Strong sell opportunity"
        else:
            msg += f"⚠️ Mixed signals - Wait for confluence"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except ImportError:
        await update.message.reply_text("❌ Multi-timeframe analyzer not available.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ============================================================================
# REGISTER COMMANDS - Add these to main() function in telegram_bot.py
# ============================================================================

"""
In your main() function, add these lines:

app.add_handler(CommandHandler("scalp", scalp_command))
app.add_handler(CommandHandler("scalp_btc", scalp_btc_command))
app.add_handler(CommandHandler("scalp_gold", scalp_gold_command))
app.add_handler(CommandHandler("orderflow", orderflow_command))
app.add_handler(CommandHandler("quick_scan", quick_scan_command))
"""

# ============================================================================
# FAST AUTO-ALERT SYSTEM - Add this function
# ============================================================================

async def check_scalp_signals_and_alert(application):
    """Fast background task for scalping signals (checks every 2 minutes)"""
    global last_btc_scalp_signal, last_gold_scalp_signal
    
    if not ALERT_ENABLED or len(subscribed_users) == 0:
        return
    
    try:
        # Quick BTC scalping check
        spec_btc = importlib.util.spec_from_file_location(
            "btc_scalp",
            os.path.join(os.path.dirname(__file__), 'btc_scalping_analyzer.py')
        )
        module_btc = importlib.util.module_from_spec(spec_btc)
        spec_btc.loader.exec_module(module_btc)
        
        btc_analyzer = module_btc.BTCScalpingAnalyzer()
        btc_signal = btc_analyzer.generate_trading_signal()
        
        btc_has_signal = (btc_signal and 
                         btc_signal.get('direction') != 'HOLD' and
                         btc_signal.get('confidence', 0) >= 60)
        
        # Check for NEW BTC scalping signal
        if btc_has_signal and not last_btc_scalp_signal:
            msg = "⚡ *NEW BTC SCALPING SIGNAL!* ⚡\n\n"
            msg += f"Direction: {btc_signal['direction']}\n"
            msg += f"Entry: ${btc_signal.get('entry_price', 'N/A'):,.2f}\n"
            msg += f"SL: ${btc_signal.get('stop_loss', 'N/A'):,.2f}\n"
            msg += f"TP: ${btc_signal.get('take_profit', 'N/A'):,.2f}\n"
            msg += f"Confidence: {btc_signal.get('confidence', 'N/A')}%\n"
            msg += f"\n⏱️ Quick scalp - Act fast!"
            
            for chat_id in subscribed_users:
                try:
                    await application.bot.send_message(
                        chat_id=chat_id,
                        text=msg,
                        parse_mode='Markdown'
                    )
                except:
                    pass
        
        last_btc_scalp_signal = btc_has_signal
        
        # Similar for Gold...
        
    except Exception as e:
        print(f"Scalp alert error: {e}")


async def auto_scalp_alert_loop(application):
    """Fast alert loop for scalping (every 2 minutes)"""
    while True:
        await check_scalp_signals_and_alert(application)
        await asyncio.sleep(120)  # 2 minutes


# ============================================================================
# ADD TO POST_INIT - Start fast alert loop
# ============================================================================

"""
In your post_init function, add:

# Start fast scalping alert loop
asyncio.create_task(auto_scalp_alert_loop(application))
"""

