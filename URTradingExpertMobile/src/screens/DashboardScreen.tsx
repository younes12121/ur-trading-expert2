import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  Dimensions,
} from 'react-native';
import {
  Text,
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  Avatar,
  ActivityIndicator,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import LinearGradient from 'react-native-linear-gradient';
import { LineChart, BarChart } from 'react-native-chart-kit';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { theme, spacing, borderRadius, typography, shadows } from '../styles/theme';
import { PortfolioMetrics, TradingSignal, MarketData, AIInsight } from '../types';
import apiService from '../services/api';

const { width: screenWidth } = Dimensions.get('window');

const DashboardScreen: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [portfolioData, setPortfolioData] = useState<PortfolioMetrics | null>(null);
  const [liveSignals, setLiveSignals] = useState<TradingSignal[]>([]);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    loadDashboardData();

    // Set up real-time updates
    const unsubscribeSignals = apiService.subscribeToSignals((signal) => {
      setLiveSignals(prev => [signal, ...prev.slice(0, 4)]); // Keep only latest 5
    });

    return () => {
      unsubscribeSignals();
    };
  }, []);

  const loadDashboardData = useCallback(async () => {
    try {
      const [portfolioResult, signalsResult, marketResult, insightsResult] = await Promise.all([
        apiService.getPortfolio(),
        apiService.getLiveSignals(),
        apiService.getMarketOverview(),
        apiService.getAIInsights(),
      ]);

      if (portfolioResult.success) {
        setPortfolioData(portfolioResult.data);
      }

      if (signalsResult.success) {
        setLiveSignals(signalsResult.data?.slice(0, 5) || []);
      }

      if (marketResult.success) {
        setMarketData(marketResult.data || []);
      }

      if (insightsResult.success) {
        setAiInsights(insightsResult.data?.slice(0, 3) || []);
      }

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      Alert.alert('Error', 'Failed to load dashboard data');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  const onRefresh = useCallback(() => {
    setIsRefreshing(true);
    loadDashboardData();
  }, [loadDashboardData]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getSignalColor = (direction: string) => {
    switch (direction) {
      case 'BUY': return theme.colors.buy;
      case 'SELL': return theme.colors.sell;
      case 'HOLD': return theme.colors.hold;
      default: return theme.colors.neutral;
    }
  };

  const getMarketStatusColor = (status: string) => {
    switch (status) {
      case 'bullish': return theme.colors.buy;
      case 'bearish': return theme.colors.sell;
      default: return theme.colors.warning;
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Loading Dashboard...</Text>
      </View>
    );
  }

  // Mock chart data (replace with real data from API)
  const chartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    datasets: [{
      data: [25400, 25350, 25500, 25430, 25475],
      color: (opacity = 1) => `rgba(0, 217, 255, ${opacity})`,
      strokeWidth: 2,
    }],
  };

  const chartConfig = {
    backgroundColor: theme.colors.surface,
    backgroundGradientFrom: theme.colors.surface,
    backgroundGradientTo: theme.colors.surface,
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(0, 217, 255, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
      stroke: theme.colors.primary,
    },
  };

  return (
    <LinearGradient
      colors={[theme.colors.background, theme.colors.surface]}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Title style={styles.headerTitle}>Dashboard</Title>
            <Text style={styles.lastUpdate}>
              Updated {lastUpdate.toLocaleTimeString()}
            </Text>
          </View>
          <Button
            mode="contained"
            onPress={onRefresh}
            loading={isRefreshing}
            style={styles.refreshButton}
            contentStyle={styles.refreshButtonContent}
          >
            <Icon name="refresh" size={16} color={theme.colors.onPrimary} />
          </Button>
        </View>

        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          refreshControl={
            <RefreshControl
              refreshing={isRefreshing}
              onRefresh={onRefresh}
              colors={[theme.colors.primary]}
              tintColor={theme.colors.primary}
            />
          }
          showsVerticalScrollIndicator={false}
        >
          {/* Portfolio Metrics */}
          {portfolioData && (
            <View style={styles.metricsSection}>
              <Text style={styles.sectionTitle}>Portfolio Overview</Text>
              <View style={styles.metricsGrid}>
                <Card style={[styles.metricCard, shadows.md]}>
                  <LinearGradient
                    colors={[theme.colors.primary, theme.colors.primaryContainer]}
                    style={styles.metricCardGradient}
                  >
                    <Card.Content style={styles.metricCardContent}>
                      <View style={styles.metricHeader}>
                        <Avatar.Icon
                          size={40}
                          icon="wallet"
                          style={styles.metricIcon}
                          color={theme.colors.onPrimary}
                        />
                        <View>
                          <Text style={styles.metricValue}>
                            {formatCurrency(portfolioData.balance)}
                          </Text>
                          <Text style={styles.metricLabel}>Portfolio Balance</Text>
                        </View>
                      </View>
                      <Text style={[
                        styles.metricChange,
                        { color: portfolioData.change >= 0 ? theme.colors.buy : theme.colors.sell }
                      ]}>
                        {formatPercent(portfolioData.change)}
                      </Text>
                    </Card.Content>
                  </LinearGradient>
                </Card>

                <Card style={[styles.metricCard, shadows.md]}>
                  <Card.Content style={styles.metricCardContent}>
                    <View style={styles.metricHeader}>
                      <Avatar.Icon
                        size={40}
                        icon="trending-up"
                        style={styles.metricIcon}
                        color={theme.colors.buy}
                      />
                      <View>
                        <Text style={styles.metricValue}>
                          {formatCurrency(portfolioData.todayPnL)}
                        </Text>
                        <Text style={styles.metricLabel}>Today's P&L</Text>
                      </View>
                    </View>
                    <Text style={styles.metricSubtext}>
                      {portfolioData.todayPnL >= 0 ? '+' : ''}
                      {((portfolioData.todayPnL / portfolioData.balance) * 100).toFixed(2)}%
                    </Text>
                  </Card.Content>
                </Card>

                <Card style={[styles.metricCard, shadows.md]}>
                  <Card.Content style={styles.metricCardContent}>
                    <View style={styles.metricHeader}>
                      <Avatar.Icon
                        size={40}
                        icon="target"
                        style={styles.metricIcon}
                        color={theme.colors.warning}
                      />
                      <View>
                        <Text style={styles.metricValue}>
                          {portfolioData.winRate.toFixed(1)}%
                        </Text>
                        <Text style={styles.metricLabel}>Win Rate</Text>
                      </View>
                    </View>
                    <Text style={styles.metricSubtext}>
                      {portfolioData.totalTrades} total trades
                    </Text>
                  </Card.Content>
                </Card>

                <Card style={[styles.metricCard, shadows.md]}>
                  <Card.Content style={styles.metricCardContent}>
                    <View style={styles.metricHeader}>
                      <Avatar.Icon
                        size={40}
                        icon="activity"
                        style={styles.metricIcon}
                        color={theme.colors.info}
                      />
                      <View>
                        <Text style={styles.metricValue}>
                          {portfolioData.activePositions}
                        </Text>
                        <Text style={styles.metricLabel}>Active Positions</Text>
                      </View>
                    </View>
                    <Text style={styles.metricSubtext}>
                      Monitor your trades
                    </Text>
                  </Card.Content>
                </Card>
              </View>
            </View>
          )}

          {/* Performance Chart */}
          <Card style={[styles.chartCard, shadows.lg]}>
            <Card.Content>
              <Title style={styles.chartTitle}>Portfolio Performance</Title>
              <LineChart
                data={chartData}
                width={screenWidth - 64}
                height={200}
                chartConfig={chartConfig}
                bezier
                style={styles.chart}
              />
            </Card.Content>
          </Card>

          {/* Live Signals */}
          <View style={styles.signalsSection}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Live Trading Signals</Text>
              <Button mode="text" onPress={() => {/* Navigate to signals screen */}}>
                View All
              </Button>
            </View>

            {liveSignals.length > 0 ? (
              liveSignals.slice(0, 3).map((signal, index) => (
                <Card key={signal.id || index} style={[styles.signalCard, shadows.sm]}>
                  <Card.Content style={styles.signalCardContent}>
                    <View style={styles.signalHeader}>
                      <Text style={styles.signalAsset}>{signal.asset}</Text>
                      <Chip
                        style={[
                          styles.signalDirectionChip,
                          { backgroundColor: getSignalColor(signal.direction) }
                        ]}
                        textStyle={styles.signalDirectionText}
                      >
                        {signal.direction}
                      </Chip>
                    </View>

                    <View style={styles.signalDetails}>
                      <View style={styles.signalDetail}>
                        <Text style={styles.signalDetailLabel}>Entry:</Text>
                        <Text style={styles.signalDetailValue}>
                          {signal.entry.toFixed(signal.asset.includes('JPY') ? 2 : 5)}
                        </Text>
                      </View>
                      <View style={styles.signalDetail}>
                        <Text style={styles.signalDetailLabel}>Stop Loss:</Text>
                        <Text style={[styles.signalDetailValue, { color: theme.colors.sell }]}>
                          {signal.stopLoss.toFixed(signal.asset.includes('JPY') ? 2 : 5)}
                        </Text>
                      </View>
                      <View style={styles.signalDetail}>
                        <Text style={styles.signalDetailLabel}>Take Profit:</Text>
                        <Text style={[styles.signalDetailValue, { color: theme.colors.buy }]}>
                          {signal.takeProfit1?.toFixed(signal.asset.includes('JPY') ? 2 : 5)}
                        </Text>
                      </View>
                    </View>

                    <Text style={styles.signalAnalysis} numberOfLines={2}>
                      {signal.analysis}
                    </Text>
                  </Card.Content>
                </Card>
              ))
            ) : (
              <Card style={[styles.emptyCard, shadows.sm]}>
                <Card.Content style={styles.emptyCardContent}>
                  <Icon name="lightning-bolt-outline" size={48} color={theme.colors.onSurfaceVariant} />
                  <Text style={styles.emptyCardText}>No live signals at the moment</Text>
                  <Text style={styles.emptyCardSubtext}>Signals will appear here when available</Text>
                </Card.Content>
              </Card>
            )}
          </View>

          {/* Market Overview */}
          {marketData.length > 0 && (
            <View style={styles.marketSection}>
              <Text style={styles.sectionTitle}>Market Overview</Text>
              <View style={styles.marketGrid}>
                {marketData.slice(0, 4).map((market, index) => (
                  <Card key={index} style={[styles.marketCard, shadows.sm]}>
                    <Card.Content style={styles.marketCardContent}>
                      <View style={styles.marketHeader}>
                        <Text style={styles.marketRegion}>{market.region}</Text>
                        <View style={[
                          styles.marketStatusIndicator,
                          { backgroundColor: getMarketStatusColor(market.status) }
                        ]} />
                      </View>
                      <Text style={styles.marketStatus} numberOfLines={1}>
                        {market.status.charAt(0).toUpperCase() + market.status.slice(1)} Market
                      </Text>
                      <Text style={[
                        styles.marketChange,
                        { color: market.change >= 0 ? theme.colors.buy : theme.colors.sell }
                      ]}>
                        {formatPercent(market.change)}
                      </Text>
                    </Card.Content>
                  </Card>
                ))}
              </View>
            </View>
          )}

          {/* AI Insights */}
          {aiInsights.length > 0 && (
            <View style={styles.insightsSection}>
              <Text style={styles.sectionTitle}>AI Insights</Text>
              {aiInsights.map((insight, index) => (
                <Card key={index} style={[styles.insightCard, shadows.sm]}>
                  <Card.Content style={styles.insightCardContent}>
                    <View style={styles.insightHeader}>
                      <Icon
                        name={
                          insight.type === 'market_regime' ? 'radar' :
                          insight.type === 'risk' ? 'shield-check' :
                          'lightbulb'
                        }
                        size={24}
                        color={
                          insight.priority === 'high' ? theme.colors.warning :
                          insight.priority === 'medium' ? theme.colors.info :
                          theme.colors.success
                        }
                      />
                      <Text style={styles.insightPriority}>
                        {insight.priority.charAt(0).toUpperCase() + insight.priority.slice(1)} Priority
                      </Text>
                    </View>
                    <Text style={styles.insightMessage}>{insight.message}</Text>
                  </Card.Content>
                </Card>
              ))}
            </View>
          )}
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  loadingText: {
    marginTop: spacing.md,
    color: theme.colors.onSurface,
    fontSize: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.outline,
  },
  headerLeft: {
    flex: 1,
  },
  headerTitle: {
    ...typography.h3,
    color: theme.colors.onSurface,
    marginBottom: 2,
  },
  lastUpdate: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
  },
  refreshButton: {
    borderRadius: borderRadius.md,
  },
  refreshButtonContent: {
    paddingHorizontal: spacing.sm,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.lg,
  },
  metricsSection: {
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    ...typography.h4,
    color: theme.colors.onSurface,
    marginBottom: spacing.lg,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  metricCard: {
    flex: 1,
    minWidth: (screenWidth - spacing.lg * 2 - spacing.md) / 2,
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
  },
  metricCardGradient: {
    flex: 1,
  },
  metricCardContent: {
    padding: spacing.md,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  metricIcon: {
    backgroundColor: 'transparent',
    marginRight: spacing.md,
  },
  metricValue: {
    ...typography.h4,
    color: theme.colors.onPrimary,
    fontWeight: 'bold',
  },
  metricLabel: {
    fontSize: 12,
    color: theme.colors.onPrimary,
    opacity: 0.8,
  },
  metricChange: {
    fontSize: 14,
    fontWeight: '600',
  },
  metricSubtext: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginTop: 2,
  },
  chartCard: {
    marginBottom: spacing.xl,
    borderRadius: borderRadius.lg,
    backgroundColor: theme.colors.surface,
  },
  chartTitle: {
    ...typography.h5,
    color: theme.colors.onSurface,
    marginBottom: spacing.md,
  },
  chart: {
    borderRadius: borderRadius.md,
    marginVertical: spacing.sm,
  },
  signalsSection: {
    marginBottom: spacing.xl,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  signalCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
    backgroundColor: theme.colors.surface,
  },
  signalCardContent: {
    padding: spacing.md,
  },
  signalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  signalAsset: {
    ...typography.h5,
    color: theme.colors.onSurface,
    fontWeight: 'bold',
  },
  signalDirectionChip: {
    height: 28,
  },
  signalDirectionText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  signalDetails: {
    marginBottom: spacing.sm,
  },
  signalDetail: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  signalDetailLabel: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
  },
  signalDetailValue: {
    fontSize: 14,
    color: theme.colors.onSurface,
    fontWeight: '600',
    fontFamily: 'monospace',
  },
  signalAnalysis: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
    lineHeight: 20,
  },
  emptyCard: {
    borderRadius: borderRadius.lg,
    backgroundColor: theme.colors.surface,
  },
  emptyCardContent: {
    padding: spacing.xl,
    alignItems: 'center',
  },
  emptyCardText: {
    ...typography.body1,
    color: theme.colors.onSurface,
    marginTop: spacing.md,
    textAlign: 'center',
  },
  emptyCardSubtext: {
    ...typography.body2,
    color: theme.colors.onSurfaceVariant,
    marginTop: spacing.sm,
    textAlign: 'center',
  },
  marketSection: {
    marginBottom: spacing.xl,
  },
  marketGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  marketCard: {
    flex: 1,
    minWidth: (screenWidth - spacing.lg * 2 - spacing.md) / 2,
    borderRadius: borderRadius.lg,
    backgroundColor: theme.colors.surface,
  },
  marketCardContent: {
    padding: spacing.md,
  },
  marketHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  marketRegion: {
    ...typography.h6,
    color: theme.colors.onSurface,
    fontWeight: 'bold',
  },
  marketStatusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  marketStatus: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginBottom: spacing.xs,
  },
  marketChange: {
    ...typography.body2,
    fontWeight: 'bold',
  },
  insightsSection: {
    marginBottom: spacing.xl,
  },
  insightCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
    backgroundColor: theme.colors.surface,
  },
  insightCardContent: {
    padding: spacing.md,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  insightPriority: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginLeft: spacing.sm,
    textTransform: 'uppercase',
    fontWeight: '600',
  },
  insightMessage: {
    ...typography.body1,
    color: theme.colors.onSurface,
    lineHeight: 20,
  },
});

export default DashboardScreen;
