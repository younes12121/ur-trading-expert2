# 🔗 Upgrade Path Integration Guide

**How to integrate the upgrade path system into your Telegram bot**

---

## 📋 QUICK START

### 1. Import the Upgrade Path Manager

Add to `telegram_bot.py`:

```python
from upgrade_path_manager import get_upgrade_manager, TriggerType
```

### 2. Initialize in Bot Startup

```python
# In main() or startup function
upgrade_manager = get_upgrade_manager()
print("[OK] Upgrade path manager loaded")
```

### 3. Track User Commands

Add tracking to command handlers:

```python
async def btc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_tier = user_manager.get_user_tier(user_id)
    
    # Track command usage
    upgrade_manager.track_command(user_id, '/btc', user_tier)
    
    # Check if asset is restricted
    if not user_manager.has_feature_access(user_id, 'all_assets'):
        # Check for upgrade trigger
        trigger_context = {
            'restricted_asset': True,
            'asset_name': 'Bitcoin (BTC)'
        }
        trigger = upgrade_manager.check_upgrade_triggers(user_id, user_tier, trigger_context)
        
        if trigger:
            msg, keyboard = upgrade_manager.get_upgrade_message(trigger, user_id, user_tier, trigger_context)
            await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            return
    
    # Continue with normal signal generation...
```

---

## 🎯 INTEGRATION POINTS

### Point 1: Daily Limit Check

**Location:** In signal generation functions

```python
# Check daily limit
can_receive, remaining, limit = user_manager.check_daily_signal_limit(user_id)

if not can_receive:
    # Check for upgrade trigger
    trigger_context = {'daily_limit_reached': True}
    trigger = upgrade_manager.check_upgrade_triggers(user_id, user_tier, trigger_context)
    
    if trigger:
        msg, keyboard = upgrade_manager.get_upgrade_message(trigger, user_id, user_tier, trigger_context)
        await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Show limit message
    await update.message.reply_text("⏰ Daily limit reached. Upgrade to Premium for unlimited signals!")
```

### Point 2: Restricted Asset Access

**Location:** Asset-specific commands (`/btc`, `/gold`, `/es`, etc.)

```python
# Check if user has access
if not user_manager.has_feature_access(user_id, 'all_assets'):
    trigger_context = {
        'restricted_asset': True,
        'asset_name': asset_display_name
    }
    trigger = upgrade_manager.check_upgrade_triggers(user_id, user_tier, trigger_context)
    
    if trigger:
        msg, keyboard = upgrade_manager.get_upgrade_message(trigger, user_id, user_tier, trigger_context)
        await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
```

### Point 3: Advanced Features

**Location:** Premium feature commands (`/portfolio_optimize`, `/market_structure`, etc.)

```python
# Check feature access
if not user_manager.has_feature_access(user_id, 'mtf_analysis'):
    trigger_context = {
        'advanced_feature': True,
        'feature_name': 'Multi-Timeframe Analysis'
    }
    trigger = upgrade_manager.check_upgrade_triggers(user_id, user_tier, trigger_context)
    
    if trigger:
        msg, keyboard = upgrade_manager.get_upgrade_message(trigger, user_id, user_tier, trigger_context)
        await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
```

### Point 4: Analytics Requests

**Location:** `/analytics`, `/export`, `/performance` commands

```python
if not user_manager.has_feature_access(user_id, 'full_analytics'):
    trigger_context = {'analytics_request': True}
    trigger = upgrade_manager.check_upgrade_triggers(user_id, user_tier, trigger_context)
    
    if trigger:
        msg, keyboard = upgrade_manager.get_upgrade_message(trigger, user_id, user_tier, trigger_context)
        await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
```

### Point 5: High Engagement Detection

**Location:** After any command (optional, can be in background)

```python
# After command execution
upgrade_manager.track_command(user_id, command_name, user_tier)

# Check for high engagement trigger (optional, don't show immediately)
if user_tier == 'free':
    trigger_context = {}
    trigger = upgrade_manager.check_upgrade_triggers(user_id, user_tier, trigger_context)
    
    # Only show if it's a high-engagement trigger and user is very active
    if trigger in [TriggerType.HIGH_ENGAGEMENT, TriggerType.MULTIPLE_DAYS_ACTIVE]:
        # Show after a delay or in next interaction
        pass
```

---

## 🔔 CALLBACK HANDLERS

### Add Callback Handler for Upgrade Buttons

```python
async def upgrade_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle upgrade button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    upgrade_manager = get_upgrade_manager()
    
    if callback_data == 'upgrade_trial':
        # Start free trial
        if upgrade_manager.start_trial(user_id, days=7):
            # Update user tier to premium (trial)
            user_manager.update_user_tier(user_id, 'premium')
            upgrade_manager.track_conversion_event(user_id, 'trial_started')
            
            await query.edit_message_text(
                "🎉 *7-Day Free Trial Started!*\n\n"
                "You now have access to:\n"
                "✅ All 15 trading assets\n"
                "✅ Unlimited signals\n"
                "✅ AI predictions\n"
                "✅ Portfolio tools\n\n"
                "Trial expires in 7 days. Enjoy!",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ Trial already used. Upgrade to Premium: /subscribe",
                parse_mode='Markdown'
            )
    
    elif callback_data == 'upgrade_premium_info':
        # Show premium features
        await query.edit_message_text(
            "⭐ *PREMIUM FEATURES*\n\n"
            "• All 15 trading assets\n"
            "• Unlimited signals\n"
            "• AI predictions\n"
            "• Portfolio optimization\n"
            "• Market structure analysis\n"
            "• Advanced risk management\n\n"
            "💰 $39/month\n"
            "🎁 Start free trial: /trial",
            parse_mode='Markdown'
        )
    
    elif callback_data == 'upgrade_vip':
        # Show VIP upgrade flow
        await query.edit_message_text(
            "👑 *UPGRADE TO VIP*\n\n"
            "VIP includes:\n"
            "• All Premium features\n"
            "• Broker integration\n"
            "• Private community\n"
            "• Weekly live calls\n\n"
            "💰 $129/month\n"
            "🎁 Use code UPGRADE20 for 20% off first month\n\n"
            "Subscribe: /subscribe vip",
            parse_mode='Markdown'
        )
    
    elif callback_data == 'upgrade_dismiss':
        # Dismiss upgrade prompt
        await query.edit_message_text(
            "👍 No problem! You can upgrade anytime with /subscribe",
            parse_mode='Markdown'
        )
        upgrade_manager.track_conversion_event(user_id, 'upgrade_dismissed')

# Register callback handler
application.add_handler(CallbackQueryHandler(upgrade_callback_handler, pattern='^upgrade_'))
```

---

## 📊 ANALYTICS & TRACKING

### Track Conversion Events

```python
# When user clicks upgrade button
upgrade_manager.track_conversion_event(user_id, 'upgrade_button_clicked', {
    'tier': 'premium',
    'source': 'daily_limit_trigger'
})

# When user starts trial
upgrade_manager.track_conversion_event(user_id, 'trial_started', {
    'days': 7,
    'trigger': 'high_engagement'
})

# When user subscribes
upgrade_manager.track_conversion_event(user_id, 'subscription_completed', {
    'tier': 'premium',
    'price': 39.00
})
```

### Get User Stats

```python
# Get user engagement stats
stats = upgrade_manager.get_user_stats(user_id)
print(f"Engagement Score: {stats['engagement_score']}")
print(f"Commands Today: {stats['commands_today']}")
print(f"Consecutive Days: {stats['consecutive_days']}")

# Get platform stats
platform_stats = upgrade_manager.get_platform_stats()
print(f"Trial Rate: {platform_stats['trial_rate']}%")
print(f"High Engagement: {platform_stats['engagement_rate']}%")
```

---

## 🎯 EXAMPLE: Complete Integration

### Example Command Handler with Upgrade Triggers

```python
async def btc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bitcoin signal command with upgrade triggers"""
    user_id = update.effective_user.id
    user_tier = user_manager.get_user_tier(user_id)
    upgrade_manager = get_upgrade_manager()
    
    # Track command
    upgrade_manager.track_command(user_id, '/btc', user_tier)
    
    # Check access
    if not user_manager.has_feature_access(user_id, 'all_assets'):
        # Check for upgrade trigger
        trigger_context = {
            'restricted_asset': True,
            'asset_name': 'Bitcoin (BTC)'
        }
        trigger = upgrade_manager.check_upgrade_triggers(user_id, user_tier, trigger_context)
        
        if trigger:
            msg, keyboard = upgrade_manager.get_upgrade_message(trigger, user_id, user_tier, trigger_context)
            buttons = [[InlineKeyboardButton(**btn) for btn in row] for row in keyboard]
            await update.message.reply_text(
                msg,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
    
    # Check daily limit
    can_receive, remaining, limit = user_manager.check_daily_signal_limit(user_id)
    if not can_receive:
        trigger_context = {'daily_limit_reached': True}
        trigger = upgrade_manager.check_upgrade_triggers(user_id, user_tier, trigger_context)
        
        if trigger:
            msg, keyboard = upgrade_manager.get_upgrade_message(trigger, user_id, user_tier, trigger_context)
            buttons = [[InlineKeyboardButton(**btn) for btn in row] for row in keyboard]
            await update.message.reply_text(
                msg,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
    
    # Generate signal (user has access)
    signal = await generate_btc_signal()
    await update.message.reply_text(format_signal(signal), parse_mode='Markdown')
    
    # Increment signal counter
    user_manager.increment_daily_signals(user_id)
```

---

## ✅ CHECKLIST

### Phase 1: Basic Integration
- [ ] Import `upgrade_path_manager`
- [ ] Initialize in bot startup
- [ ] Add tracking to command handlers
- [ ] Add callback handler for upgrade buttons
- [ ] Test daily limit trigger
- [ ] Test restricted asset trigger

### Phase 2: Advanced Features
- [ ] Add advanced feature triggers
- [ ] Add analytics request triggers
- [ ] Add high engagement detection
- [ ] Add trial system integration
- [ ] Test all trigger types

### Phase 3: Analytics
- [ ] Track conversion events
- [ ] Set up analytics dashboard
- [ ] Monitor conversion rates
- [ ] A/B test messages
- [ ] Optimize based on data

---

## 🚀 NEXT STEPS

1. **Integrate upgrade triggers** into your command handlers
2. **Add callback handlers** for upgrade buttons
3. **Test all trigger types** to ensure they work
4. **Monitor conversion rates** and optimize
5. **Iterate based on data** to improve results

---

**Ready to maximize conversions! 🎉**
