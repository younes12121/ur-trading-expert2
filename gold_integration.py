
# Enhanced Gold Command Integration  
async def gold_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced Gold command with improved 20-criteria system"""
    user_id = update.effective_user.id
    
    if not check_rate_limit(user_id, 'gold'):
        await update.message.reply_text("⏱️ Please wait before requesting another Gold analysis")
        return
    
    status_msg = await update.message.reply_text(
        "🔄 *Analyzing Gold Market (XAUUSD)...*\n\n"
        "⏳ Applying enhanced 20-criteria filter\n"
        "📊 Fetching live data\n"
        "🎯 Calculating elite signals"
    )
    
    try:
        from enhanced_gold_signal_generator import EnhancedGoldSignalGenerator
        
        generator = EnhancedGoldSignalGenerator()
        signal = generator.generate_signal()
        
        if signal and signal.get('direction') != 'HOLD':
            # Elite signal found
            msg = f"🥇 **GOLD ELITE {signal['grade']} SIGNAL**\n\n"
            msg += f"📊 *Direction:* **{signal['direction']}**\n"
            msg += f"💰 *Entry:* ${signal['entry']:,.2f}\n"
            msg += f"🛑 *Stop Loss:* ${signal['stop_loss']:,.2f}\n"
            msg += f"🎯 *Take Profit 1:* ${signal['take_profit_1']:,.2f}\n"
            msg += f"🎯 *Take Profit 2:* ${signal['take_profit_2']:,.2f}\n\n"
            
            msg += f"📈 *Risk/Reward:* {signal['risk_reward_1']:.1f}:1 / {signal['risk_reward_2']:.1f}:1\n"
            msg += f"💎 *Confidence:* {signal['confidence']:.1f}%\n"
            msg += f"🏆 *Score:* {signal['score']} ({signal['grade']})\n"
            msg += f"📊 *ATR:* ${signal['atr']:.2f}\n\n"
            
            msg += f"✅ **Top Confirmations:**\n"
            for i, confirmation in enumerate(signal['analysis']['passed_criteria'][:5]):
                msg += f"   {i+1}. {confirmation}\n"
            
            msg += f"\n🚀 *This is an ELITE Gold signal with {signal['criteria_met']}/20 criteria!*"
            
        else:
            # No elite signal
            msg = f"🥇 **GOLD ANALYSIS**\n\n"
            msg += f"💰 *Current Price:* ${signal['current_price']:,.2f}\n"
            msg += f"📊 *Signal Status:* No elite signal\n"
            msg += f"🏆 *Score:* {signal['criteria_met']}/20 ({signal['confidence']:.1f}%)\n\n"
            
            msg += f"❌ **Key Missing Criteria:**\n"
            for i, failure in enumerate(signal['failed_criteria'][:3]):
                msg += f"   {i+1}. {failure}\n"
            
            msg += f"\n⏳ *Waiting for stronger Gold setup (need 17+/20 criteria)*"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        error_msg = f"❌ Error analyzing Gold: {get_user_friendly_error(e)}"
        await status_msg.edit_text(error_msg)
        if logger:
            logger.log_error(e, {'user_id': user_id, 'command': 'gold'})
