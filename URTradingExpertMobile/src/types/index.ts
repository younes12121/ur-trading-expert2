// Core Trading Types
export interface TradingSignal {
  id: string;
  asset: string;
  direction: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  entry: number;
  stopLoss: number;
  takeProfit1: number;
  takeProfit2?: number;
  analysis: string;
  category: 'asian' | 'major' | 'emerging' | 'crypto';
  timestamp: string;
  price?: number;
}

export interface Position {
  id: string;
  asset: string;
  direction: 'BUY' | 'SELL';
  entry: number;
  current: number;
  pnl: number;
  pnlPercent: number;
  size: number;
  stopLoss: number;
  takeProfit: number;
  openedAt: string;
  leverage?: number;
}

export interface PortfolioMetrics {
  balance: number;
  change: number;
  changeAmount: number;
  todayPnL: number;
  activePositions: number;
  winRate: number;
  totalTrades: number;
}

export interface MarketData {
  region: string;
  change: number;
  status: 'bullish' | 'bearish' | 'volatile';
  assets: string[];
}

export interface AIInsight {
  type: 'market_regime' | 'risk' | 'opportunity' | 'warning';
  message: string;
  priority: 'high' | 'medium' | 'low';
  timestamp: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  subscription: 'free' | 'premium' | 'vip';
  preferences: UserPreferences;
}

export interface UserPreferences {
  notifications: {
    signals: boolean;
    priceAlerts: boolean;
    news: boolean;
    sessionAlerts: boolean;
  };
  riskLevel: 'conservative' | 'moderate' | 'aggressive';
  theme: 'dark' | 'light' | 'auto';
  defaultAsset: string;
  language: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Navigation Types
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  SignalDetail: { signal: TradingSignal };
  AssetDetail: { asset: string };
  Settings: undefined;
};

export type TabParamList = {
  Dashboard: undefined;
  Signals: undefined;
  Portfolio: undefined;
  Markets: undefined;
  Profile: undefined;
};

// Asset Types
export interface Asset {
  symbol: string;
  name: string;
  type: 'forex' | 'crypto' | 'futures' | 'commodity';
  category: 'asian' | 'major' | 'emerging' | 'crypto';
  pipValue: number;
  spread: number;
  session: 'london' | 'new-york' | 'tokyo' | 'sydney';
}

// Trading Record Types
export interface TradingRecord {
  id: string;
  asset: string;
  direction: 'BUY' | 'SELL';
  strategy: string;
  entry: number;
  exit: number;
  pnl: number;
  pips: number;
  duration: string;
  date: string;
  tags?: string[];
}

// Notification Types
export interface Notification {
  id: string;
  type: 'signal' | 'alert' | 'news' | 'system';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  data?: any;
}

// Chart Data Types
export interface ChartPoint {
  timestamp: number;
  price: number;
  volume?: number;
}

export interface ChartData {
  symbol: string;
  timeframe: string;
  data: ChartPoint[];
  indicators?: {
    sma20?: number[];
    sma50?: number[];
    rsi?: number[];
    macd?: { line: number[]; signal: number[]; histogram: number[] };
  };
}

// Session Types
export interface TradingSession {
  name: string;
  start: string;
  end: string;
  timezone: string;
  active: boolean;
  volatility: 'low' | 'medium' | 'high';
  pairs: string[];
}

// Risk Management Types
export interface RiskMetrics {
  maxDrawdown: number;
  sharpeRatio: number;
  var95: number;
  positionLimit: number;
  currentExposure: number;
}

export interface PositionSize {
  asset: string;
  direction: 'BUY' | 'SELL';
  entry: number;
  stopLoss: number;
  riskAmount: number;
  positionSize: number;
  leverage: number;
  potentialLoss: number;
  potentialReward: number;
  riskRewardRatio: number;
}
