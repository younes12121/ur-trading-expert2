# Personal Trading Dashboard

A comprehensive personal trading dashboard that combines the best features from your Ultra Premium and International Markets dashboards, designed for personal use to track your trading performance and records.

## 🚀 Features

### 📊 Dashboard Overview
- **Real-time Portfolio Balance**: Live tracking of your account balance and daily P&L
- **Performance Metrics**: Win rate, active positions, and key trading statistics
- **Live Market Data**: Global market overview with regional performance indicators

### 📈 Trading Records & Analytics
- **Detailed Trade History**: Complete trading records with P&L, pips, duration, and strategy
- **Advanced Filtering**: Filter by wins/losses, date ranges, and trade types
- **Pagination**: Easy navigation through large datasets
- **Export Functionality**: Download trading records as CSV files
- **Performance Charts**: Visual representation of portfolio equity curve

### 🎯 Live Trading Signals
- **Real-time Signals**: Live trading signals from your bot's analysis
- **Signal Filtering**: Filter by direction (Buy/Sell) and confidence levels
- **Multi-asset Support**: Forex, Crypto, Commodities, and Indices
- **Detailed Signal Info**: Entry, stop loss, take profit levels, and AI analysis

### 💼 Position Management
- **Current Positions**: Real-time tracking of open positions
- **P&L Monitoring**: Live profit/loss calculations
- **Risk Management**: Stop loss and take profit levels
- **Position Sizing**: Lot sizes and position values

### 🤖 AI Insights
- **Market Regime Analysis**: Bull/bear market detection
- **Risk Assessment**: Portfolio risk metrics and alerts
- **Trading Opportunities**: AI-identified high-probability setups

### 🔧 Technical Features
- **Auto-refresh**: Data updates every 30 seconds
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Clock**: Live time display with timezone support
- **API Integration**: Connects to your telegram bot's data sources

## 📁 File Structure

```
personal_trading_dashboard.html  # Main dashboard interface
personal_dashboard_api.py        # Flask API server for data integration
ultra_premium_dashboard.html     # Original ultra premium dashboard
international_markets_dashboard.html  # Original international dashboard
```

## 🛠️ Setup Instructions

### Option 1: Run with Mock Data (Recommended for Testing)
1. Simply open `personal_trading_dashboard.html` in your web browser
2. The dashboard will work with sample data for demonstration
3. All features are functional with live updates and auto-refresh

### Option 2: Run with Live API Server
1. Install Flask:
   ```bash
   pip install flask flask-cors
   ```

2. Start the API server:
   ```bash
   python personal_dashboard_api.py
   ```

3. Open `personal_trading_dashboard.html` in your browser
4. The dashboard will automatically connect to the API for live data

### Option 3: Connect to Your Telegram Bot Data
1. The API server automatically reads from:
   - `signals_db.json` - Your bot's trading signals
   - `user_profiles.json` - User account data
   - `trade_history.json` - Historical trade records

2. Place these files in the same directory as the API server
3. The dashboard will display your real trading data

## 🎨 Dashboard Sections

### 1. Portfolio Overview
- Account balance and daily P&L
- Active positions count
- Win rate percentage
- Key performance indicators

### 2. Current Positions
- Open trades with real-time P&L
- Entry/exit prices and stop loss levels
- Position sizes and risk exposure
- Color-coded profit/loss indicators

### 3. Live Signals
- Real-time trading signals from your bot
- Confidence levels and market analysis
- Entry, stop loss, and take profit suggestions
- Signal categorization by market type

### 4. Trading Records
- Complete trade history with detailed metrics
- P&L analysis and performance tracking
- Strategy-based filtering
- Export capabilities for further analysis

### 5. Market Overview
- Global market performance by region
- Market regime indicators
- Session status (Asian, European, American)
- Risk metrics and alerts

### 6. AI Insights
- Market regime analysis
- Risk management recommendations
- Trading opportunity identification
- Performance optimization suggestions

## 🔄 Data Flow

```
Telegram Bot → signals_db.json → Personal Dashboard API → Dashboard UI
User Profiles → user_profiles.json → Personal Dashboard API → Dashboard UI
Trade History → trade_history.json → Personal Dashboard API → Dashboard UI
```

## 📱 Mobile Responsive

The dashboard is fully responsive and works seamlessly on:
- Desktop computers
- Tablets
- Mobile phones
- Different screen sizes and orientations

## 🔒 Security Features

- Client-side data rendering only
- No sensitive data stored in browser
- API endpoints can be secured with authentication
- Local file-based data storage for personal use

## 🚀 Future Enhancements

- User authentication and multi-user support
- Advanced charting with TradingView integration
- Real-time notifications and alerts
- Strategy backtesting integration
- Performance analytics and reporting
- Risk management tools
- Social trading features

## 📞 Support

This dashboard is designed for personal use to monitor your trading performance. It integrates seamlessly with your existing telegram bot infrastructure while providing a beautiful, comprehensive interface for tracking your trades.

The dashboard will work immediately with sample data, and can be easily connected to your real trading data by ensuring the API server has access to your bot's data files.
