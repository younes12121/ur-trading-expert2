
# Enhanced Forex Command Integration Template
async def forex_command_template(update: Update, context: ContextTypes.DEFAULT_TYPE, pair: str):
    """Template for enhanced forex commands"""
    user_id = update.effective_user.id
    
    if not check_rate_limit(user_id, f'forex_{pair.lower()}'):
        await update.message.reply_text(f"⏱️ Please wait before requesting another {pair} analysis")
        return
    
    pair_display = f"{pair[:3]}/{pair[3:]}"
    status_msg = await update.message.reply_text(
        f"🔄 *Analyzing {pair_display} Market...*\n\n"
        "⏳ Applying enhanced 20-criteria filter\n"
        "📊 Fetching live forex data\n"
        "🎯 Calculating elite signals"
    )
    
    try:
        from enhanced_forex_signal_generator import EnhancedForexSignalGenerator
        
        generator = EnhancedForexSignalGenerator(pair)
        signal = generator.generate_signal()
        
        if signal and signal.get('direction') != 'HOLD':
            # Elite signal found
            msg = f"💱 **{pair_display} ELITE {signal['grade']} SIGNAL**\n\n"
            msg += f"📊 *Direction:* **{signal['direction']}**\n"
            msg += f"💰 *Entry:* {signal['entry']:.5f}\n"
            msg += f"🛑 *Stop Loss:* {signal['stop_loss']:.5f}\n"
            msg += f"🎯 *Take Profit 1:* {signal['take_profit_1']:.5f}\n"
            msg += f"🎯 *Take Profit 2:* {signal['take_profit_2']:.5f}\n\n"
            
            msg += f"📈 *Risk/Reward:* {signal['risk_reward_1']:.1f}:1 / {signal['risk_reward_2']:.1f}:1\n"
            msg += f"🎯 *Risk:* {signal['risk_pips']:.1f} pips\n"
            msg += f"💎 *Confidence:* {signal['confidence']:.1f}%\n"
            msg += f"🏆 *Score:* {signal['score']} ({signal['grade']})\n"
            msg += f"⏰ *Session:* {signal['session_info']['description']}\n\n"
            
            msg += f"✅ **Top Confirmations:**\n"
            for i, confirmation in enumerate(signal['analysis']['passed_criteria'][:5]):
                msg += f"   {i+1}. {confirmation}\n"
            
            msg += f"\n🚀 *This is an ELITE {pair_display} signal with {signal['criteria_met']}/20 criteria!*"
            
        else:
            # No elite signal
            msg = f"💱 **{pair_display} ANALYSIS**\n\n"
            msg += f"💰 *Current Price:* {signal['current_price']:.5f}\n"
            msg += f"📊 *Signal Status:* No elite signal\n"
            msg += f"🏆 *Score:* {signal['criteria_met']}/20 ({signal['confidence']:.1f}%)\n"
            msg += f"⏰ *Session:* {signal['session_info']['description']}\n\n"
            
            msg += f"❌ **Key Missing Criteria:**\n"
            for i, failure in enumerate(signal['failed_criteria'][:3]):
                msg += f"   {i+1}. {failure}\n"
            
            msg += f"\n⏳ *Waiting for stronger {pair_display} setup (need 17+/20 criteria)*"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        error_msg = f"❌ Error analyzing {pair_display}: {get_user_friendly_error(e)}"
        await status_msg.edit_text(error_msg)
        if logger:
            logger.log_error(e, {'user_id': user_id, 'command': f'forex_{pair.lower()}'})

# Specific forex command implementations
async def eurusd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await forex_command_template(update, context, 'EURUSD')

async def gbpusd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await forex_command_template(update, context, 'GBPUSD')
    
# Add more forex pairs as needed...
