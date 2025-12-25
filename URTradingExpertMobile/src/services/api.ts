import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { io, Socket } from 'socket.io-client';
import {
  TradingSignal,
  Position,
  PortfolioMetrics,
  MarketData,
  AIInsight,
  TradingRecord,
  ApiResponse,
  PaginatedResponse,
  User,
  Notification,
  ChartData,
  RiskMetrics
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private socket: Socket | null = null;
  private baseURL: string;

  constructor() {
    // Use your Railway deployment URL or localhost for development
    this.baseURL = __DEV__
      ? 'http://localhost:5001' // Flask dev server
      : 'https://your-app.railway.app'; // Replace with actual Railway URL

    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.setupSocket();
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.api.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          await AsyncStorage.removeItem('auth_token');
          // You might want to navigate to login screen here
        }
        return Promise.reject(error);
      }
    );
  }

  private setupSocket() {
    this.socket = io(this.baseURL, {
      transports: ['websocket'],
      upgrade: true,
    });

    this.socket.on('connect', () => {
      console.log('Connected to WebSocket');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
    });

    this.socket.on('signal_update', (data) => {
      // Handle real-time signal updates
      console.log('New signal:', data);
    });

    this.socket.on('price_update', (data) => {
      // Handle real-time price updates
      console.log('Price update:', data);
    });
  }

  // Authentication
  async login(username: string, password: string): Promise<ApiResponse<{ token: string; user: User }>> {
    try {
      const response: AxiosResponse = await this.api.post('/api/auth/login', {
        username,
        password,
      });

      const { token, user } = response.data;
      await AsyncStorage.setItem('auth_token', token);

      return {
        success: true,
        data: { token, user },
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async register(userData: { username: string; email: string; password: string }): Promise<ApiResponse<User>> {
    try {
      const response: AxiosResponse = await this.api.post('/api/auth/register', userData);
      return {
        success: true,
        data: response.data.user,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Registration failed',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async logout(): Promise<void> {
    await AsyncStorage.removeItem('auth_token');
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  // Signals
  async getLiveSignals(): Promise<ApiResponse<TradingSignal[]>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/signals/live');
      return {
        success: true,
        data: response.data.signals,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch signals',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async getSignalHistory(page: number = 1, limit: number = 20): Promise<ApiResponse<PaginatedResponse<TradingSignal>>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/signals/history', {
        params: { page, limit },
      });
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch signal history',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Portfolio
  async getPortfolio(): Promise<ApiResponse<PortfolioMetrics>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/portfolio');
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch portfolio',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async getPositions(): Promise<ApiResponse<Position[]>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/positions');
      return {
        success: true,
        data: response.data.positions,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch positions',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Trading Records
  async getTradingRecords(
    page: number = 1,
    limit: number = 20,
    filter?: string
  ): Promise<ApiResponse<PaginatedResponse<TradingRecord>>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/records', {
        params: { page, limit, filter },
      });
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch trading records',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Market Data
  async getMarketOverview(): Promise<ApiResponse<MarketData[]>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/market-overview');
      return {
        success: true,
        data: response.data.marketData,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch market data',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // AI Insights
  async getAIInsights(): Promise<ApiResponse<AIInsight[]>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/ai-insights');
      return {
        success: true,
        data: response.data.insights,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch AI insights',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Chart Data
  async getChartData(symbol: string, timeframe: string): Promise<ApiResponse<ChartData>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/chart', {
        params: { symbol, timeframe },
      });
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch chart data',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Risk Management
  async getRiskMetrics(): Promise<ApiResponse<RiskMetrics>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/risk');
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch risk metrics',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // User Profile
  async getUserProfile(): Promise<ApiResponse<User>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/user/profile');
      return {
        success: true,
        data: response.data.user,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch user profile',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async updateUserPreferences(preferences: Partial<User['preferences']>): Promise<ApiResponse<User>> {
    try {
      const response: AxiosResponse = await this.api.put('/api/user/preferences', { preferences });
      return {
        success: true,
        data: response.data.user,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to update preferences',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Notifications
  async getNotifications(): Promise<ApiResponse<Notification[]>> {
    try {
      const response: AxiosResponse = await this.api.get('/api/notifications');
      return {
        success: true,
        data: response.data.notifications,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch notifications',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async markNotificationRead(notificationId: string): Promise<ApiResponse<void>> {
    try {
      await this.api.put(`/api/notifications/${notificationId}/read`);
      return {
        success: true,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to mark notification as read',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // Telegram Bot Integration (for sending commands)
  async sendTelegramCommand(command: string, params?: any): Promise<ApiResponse<any>> {
    try {
      const response: AxiosResponse = await this.api.post('/api/telegram/command', {
        command,
        params,
      });
      return {
        success: true,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to send command',
        timestamp: new Date().toISOString(),
      };
    }
  }

  // WebSocket methods
  subscribeToSignals(callback: (signal: TradingSignal) => void) {
    if (this.socket) {
      this.socket.on('signal_update', callback);
    }
  }

  subscribeToPrices(symbols: string[], callback: (data: any) => void) {
    if (this.socket) {
      this.socket.emit('subscribe_prices', symbols);
      this.socket.on('price_update', callback);
    }
  }

  unsubscribeFromPrices(symbols: string[]) {
    if (this.socket) {
      this.socket.emit('unsubscribe_prices', symbols);
    }
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.api.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  }
}

// Create singleton instance
export const apiService = new ApiService();
export default apiService;
