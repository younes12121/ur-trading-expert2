# UR Trading Expert Mobile App

A professional React Native mobile application for the UR Trading Expert trading bot, providing real-time trading signals, portfolio management, and market analysis on-the-go.

## 🚀 Features

### 📊 **Dashboard**
- Real-time portfolio metrics (balance, P&L, win rate)
- Live trading signals with confidence scores
- Performance charts and analytics
- Market overview with global sentiment
- AI-powered trading insights

### ⚡ **Live Signals**
- Real-time trading signals for 15+ assets
- Advanced filtering (direction, confidence, category)
- Signal search and categorization
- Detailed signal analysis with entry/exit levels
- Push notifications for new signals

### 💼 **Portfolio Management**
- Active positions tracking
- Trading history and performance
- Risk metrics and analytics
- Position size calculators
- Portfolio optimization suggestions

### 🌍 **Global Markets**
- Real-time market overview (Asia, Europe, Americas, Crypto)
- Asset category management
- Market sentiment indicators
- Trading session information

### 👤 **Profile & Settings**
- User profile management
- Subscription management
- Notification preferences
- Risk tolerance settings
- Multi-language support

## 🛠️ Technology Stack

- **Framework**: React Native 0.72.6 with TypeScript
- **Navigation**: React Navigation v6
- **UI Library**: React Native Paper
- **Charts**: React Native Chart Kit
- **Icons**: React Native Vector Icons
- **State Management**: React Hooks + Context
- **Networking**: Axios with automatic retry
- **Real-time**: Socket.io for live updates
- **Storage**: AsyncStorage for local data
- **Push Notifications**: Firebase Cloud Messaging
- **Biometrics**: React Native Biometrics

## 📱 Supported Platforms

- **iOS**: 12.0+
- **Android**: API 21+ (Android 5.0+)

## 🏃‍♂️ Quick Start

### Prerequisites

1. **Node.js** 18+ and npm
2. **React Native CLI** or Expo CLI
3. **Android Studio** (for Android development)
4. **Xcode** (for iOS development on macOS)

### Installation

1. **Clone and install dependencies:**
```bash
cd URTradingExpertMobile
npm install
```

2. **Install iOS dependencies (macOS only):**
```bash
cd ios && pod install && cd ..
```

3. **Configure environment:**
Create a `.env` file in the root directory:
```env
API_BASE_URL=https://your-railway-app.railway.app
FIREBASE_API_KEY=your_firebase_key
FIREBASE_PROJECT_ID=your_project_id
```

### Running the App

#### Android
```bash
npm run android
# or
npx react-native run-android
```

#### iOS (macOS only)
```bash
npm run ios
# or
npx react-native run-ios
```

#### Development Server
```bash
npm start
# or
npx react-native start
```

## 🔧 Configuration

### Backend API Integration

The app connects to your existing trading bot backend. Update the API endpoints in `src/services/api.ts`:

```typescript
const API_BASE = __DEV__
  ? 'http://localhost:5001'  // Development
  : 'https://your-app.railway.app'; // Production
```

### Push Notifications Setup

1. **Firebase Configuration:**
   - Create a Firebase project
   - Enable Cloud Messaging
   - Download `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)
   - Place files in respective platform folders

2. **Update Firebase config in `android/app/google-services.json` and `ios/GoogleService-Info.plist`**

### App Icons and Splash Screen

Replace the default icons in:
- `android/app/src/main/res/mipmap-*`
- `ios/URTradingExpertMobile/Images.xcassets/AppIcon.appiconset`

## 📁 Project Structure

```
URTradingExpertMobile/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── TabBar.tsx      # Bottom navigation
│   │   └── ...
│   ├── screens/            # Main app screens
│   │   ├── AuthScreen.tsx  # Login/Register
│   │   ├── DashboardScreen.tsx
│   │   ├── SignalsScreen.tsx
│   │   ├── PortfolioScreen.tsx
│   │   ├── MarketsScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   └── ...
│   ├── services/           # API and external services
│   │   ├── api.ts         # Backend API client
│   │   └── ...
│   ├── utils/             # Helper functions
│   ├── types/             # TypeScript type definitions
│   ├── navigation/        # Navigation configuration
│   ├── styles/           # Theme and styling
│   │   └── theme.ts      # App theme configuration
│   └── assets/           # Images and static assets
├── android/               # Android native code
├── ios/                  # iOS native code
├── package.json
└── README.md
```

## 🎨 Customization

### Theme Configuration

Modify colors, typography, and spacing in `src/styles/theme.ts`:

```typescript
export const theme = {
  colors: {
    primary: '#00D9FF',        // Your brand cyan
    secondary: '#B8EAFF',
    background: '#0F172A',     // Dark theme
    // ... more colors
  },
  // ... other theme properties
};
```

### Adding New Screens

1. Create screen component in `src/screens/`
2. Add route to navigation types in `src/types/index.ts`
3. Update navigation configuration in `App.tsx`
4. Add to tab navigation if needed

## 🔒 Security Features

- **Biometric Authentication**: Fingerprint/Face ID support
- **Secure Token Storage**: Encrypted local storage for auth tokens
- **Certificate Pinning**: SSL certificate validation
- **Data Encryption**: Sensitive data encrypted at rest
- **Session Management**: Automatic logout on inactivity

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests (Detox)
```bash
npm run test:e2e
```

## 🚀 Build & Deployment

### Android APK
```bash
cd android
./gradlew assembleRelease
```

### iOS App Store
```bash
cd ios
xcodebuild -workspace URTradingExpertMobile.xcworkspace -scheme URTradingExpertMobile -configuration Release -archivePath ./build/URTradingExpertMobile.xcarchive archive
```

### CI/CD Integration

The app is configured for easy CI/CD deployment to:
- **App Center** (Microsoft)
- **Firebase App Distribution**
- **TestFlight** (iOS)
- **Google Play Beta** (Android)

## 📊 Performance Optimization

- **Code Splitting**: Route-based code splitting
- **Image Optimization**: FastImage for efficient image loading
- **List Virtualization**: FlatList with optimized rendering
- **Memory Management**: Proper cleanup of subscriptions
- **Caching**: Intelligent data caching with TTL

## 🐛 Troubleshooting

### Common Issues

1. **Metro bundler issues:**
```bash
npm start --reset-cache
```

2. **Android build fails:**
```bash
cd android && ./gradlew clean && cd ..
npm run android
```

3. **iOS pod install fails:**
```bash
cd ios && rm -rf Pods && pod install && cd ..
```

4. **Firebase connection issues:**
- Verify API keys in configuration files
- Check Firebase project settings
- Ensure Google Services files are correctly placed

## 📞 Support

For issues and questions:
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Inline code comments and this README
- **Telegram Bot**: Connect via the app's Telegram integration

## 📝 License

This project is part of the UR Trading Expert ecosystem. See main project license for details.

---

**Built with ❤️ for professional traders**

*Real-time signals. Professional analysis. Mobile-first design.*
