
# Enhanced Futures Command Integration
async def es_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced ES futures command"""
    user_id = update.effective_user.id
    
    if not check_rate_limit(user_id, 'es'):
        await update.message.reply_text("⏱️ Please wait before requesting another ES analysis")
        return
    
    status_msg = await update.message.reply_text(
        "🔄 *Analyzing E-mini S&P 500 (ES)...*\n\n"
        "⏳ Applying enhanced 20-criteria filter\n"
        "📊 Fetching live futures data\n"
        "🎯 Calculating elite signals"
    )
    
    try:
        from enhanced_futures_signal_generator import EnhancedFuturesSignalGenerator
        
        generator = EnhancedFuturesSignalGenerator('ES')
        signal = generator.generate_signal()
        
        if signal and signal.get('direction') != 'HOLD':
            # Elite signal found
            msg = f"📊 **ES ELITE {signal['grade']} SIGNAL**\n\n"
            msg += f"📊 *Direction:* **{signal['direction']}**\n"
            msg += f"💰 *Entry:* {signal['entry']:,.2f}\n"
            msg += f"🛑 *Stop Loss:* {signal['stop_loss']:,.2f}\n"
            msg += f"🎯 *Take Profit 1:* {signal['take_profit_1']:,.2f}\n"
            msg += f"🎯 *Take Profit 2:* {signal['take_profit_2']:,.2f}\n\n"
            
            msg += f"📈 *Risk/Reward:* {signal['risk_reward_1']:.1f}:1 / {signal['risk_reward_2']:.1f}:1\n"
            msg += f"🎯 *Risk:* {signal['risk_points']:.1f} pts (${signal['risk_dollars']:,.0f})\n"
            msg += f"💰 *Point Value:* ${signal['point_value']}/point\n"
            msg += f"💎 *Confidence:* {signal['confidence']:.1f}%\n"
            msg += f"🏆 *Score:* {signal['score']} ({signal['grade']})\n"
            msg += f"⏰ *Session:* {signal['market_session']}\n\n"
            
            msg += f"✅ **Top Confirmations:**\n"
            for i, confirmation in enumerate(signal['analysis']['passed_criteria'][:5]):
                msg += f"   {i+1}. {confirmation}\n"
            
            msg += f"\n🚀 *This is an ELITE ES signal with {signal['criteria_met']}/20 criteria!*"
            
        else:
            # No elite signal
            msg = f"📊 **E-MINI S&P 500 (ES) ANALYSIS**\n\n"
            msg += f"💰 *Current Price:* {signal['current_price']:,.2f}\n"
            msg += f"📊 *Signal Status:* No elite signal\n"
            msg += f"🏆 *Score:* {signal['criteria_met']}/20 ({signal['confidence']:.1f}%)\n"
            msg += f"⏰ *Session:* {signal['market_session']}\n\n"
            
            msg += f"❌ **Key Missing Criteria:**\n"
            for i, failure in enumerate(signal['failed_criteria'][:3]):
                msg += f"   {i+1}. {failure}\n"
            
            msg += f"\n⏳ *The enhanced 20-criteria filter is very strict.*\n"
            msg += f"*Waiting for optimal ES conditions...*"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        error_msg = f"❌ Error analyzing ES: {get_user_friendly_error(e)}"
        await status_msg.edit_text(error_msg)
        if logger:
            logger.log_error(e, {'user_id': user_id, 'command': 'es'})

async def nq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced NQ futures command (similar structure to ES)"""
    # Similar implementation for NQ...
    pass
