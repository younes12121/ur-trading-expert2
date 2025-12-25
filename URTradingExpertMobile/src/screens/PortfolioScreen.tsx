import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, Card, Title, Button, Chip } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { theme, spacing, borderRadius, typography, shadows } from '../styles/theme';
import { Position, PortfolioMetrics, TradingRecord } from '../types';
import apiService from '../services/api';

const PortfolioScreen: React.FC = () => {
  const [portfolioData, setPortfolioData] = useState<PortfolioMetrics | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [recentTrades, setRecentTrades] = useState<TradingRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadPortfolioData();
  }, []);

  const loadPortfolioData = async () => {
    try {
      const [portfolioResult, positionsResult, tradesResult] = await Promise.all([
        apiService.getPortfolio(),
        apiService.getPositions(),
        apiService.getTradingRecords(1, 5), // Get last 5 trades
      ]);

      if (portfolioResult.success) {
        setPortfolioData(portfolioResult.data);
      }
      if (positionsResult.success) {
        setPositions(positionsResult.data || []);
      }
      if (tradesResult.success) {
        setRecentTrades(tradesResult.data?.data || []);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load portfolio data');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getPositionColor = (pnl: number) => {
    return pnl >= 0 ? theme.colors.buy : theme.colors.sell;
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading Portfolio...</Text>
      </View>
    );
  }

  return (
    <LinearGradient
      colors={[theme.colors.background, theme.colors.surface]}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
          {/* Header */}
          <View style={styles.header}>
            <Title style={styles.headerTitle}>Portfolio</Title>
            <Button
              mode="outlined"
              onPress={loadPortfolioData}
              style={styles.refreshButton}
            >
              <Icon name="refresh" size={16} color={theme.colors.primary} />
            </Button>
          </View>

          {/* Portfolio Summary */}
          {portfolioData && (
            <Card style={[styles.summaryCard, shadows.lg]}>
              <Card.Content>
                <Text style={styles.summaryTitle}>Portfolio Summary</Text>
                <View style={styles.summaryGrid}>
                  <View style={styles.summaryItem}>
                    <Text style={styles.summaryValue}>
                      {formatCurrency(portfolioData.balance)}
                    </Text>
                    <Text style={styles.summaryLabel}>Total Balance</Text>
                  </View>
                  <View style={styles.summaryItem}>
                    <Text style={[styles.summaryValue, { color: getPositionColor(portfolioData.todayPnL) }]}>
                      {formatCurrency(portfolioData.todayPnL)}
                    </Text>
                    <Text style={styles.summaryLabel}>Today's P&L</Text>
                  </View>
                  <View style={styles.summaryItem}>
                    <Text style={styles.summaryValue}>
                      {portfolioData.winRate.toFixed(1)}%
                    </Text>
                    <Text style={styles.summaryLabel}>Win Rate</Text>
                  </View>
                  <View style={styles.summaryItem}>
                    <Text style={styles.summaryValue}>
                      {portfolioData.activePositions}
                    </Text>
                    <Text style={styles.summaryLabel}>Active Positions</Text>
                  </View>
                </View>
              </Card.Content>
            </Card>
          )}

          {/* Active Positions */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Active Positions</Text>
            {positions.length > 0 ? (
              positions.map((position) => (
                <Card key={position.id} style={[styles.positionCard, shadows.md]}>
                  <Card.Content>
                    <View style={styles.positionHeader}>
                      <Text style={styles.positionAsset}>{position.asset}</Text>
                      <Chip
                        style={[
                          styles.positionDirection,
                          { backgroundColor: position.direction === 'BUY' ? theme.colors.buy : theme.colors.sell }
                        ]}
                      >
                        {position.direction}
                      </Chip>
                    </View>
                    <View style={styles.positionDetails}>
                      <Text>Entry: {formatCurrency(position.entry)}</Text>
                      <Text>Current: {formatCurrency(position.current)}</Text>
                      <Text style={{ color: getPositionColor(position.pnl) }}>
                        P&L: {formatCurrency(position.pnl)}
                      </Text>
                    </View>
                  </Card.Content>
                </Card>
              ))
            ) : (
              <Card style={[styles.emptyCard, shadows.sm]}>
                <Card.Content style={styles.emptyContent}>
                  <Icon name="briefcase-outline" size={48} color={theme.colors.onSurfaceVariant} />
                  <Text style={styles.emptyText}>No active positions</Text>
                </Card.Content>
              </Card>
            )}
          </View>

          {/* Recent Trades */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Trades</Text>
            {recentTrades.length > 0 ? (
              recentTrades.map((trade) => (
                <Card key={trade.id} style={[styles.tradeCard, shadows.sm]}>
                  <Card.Content>
                    <View style={styles.tradeHeader}>
                      <Text style={styles.tradeAsset}>{trade.asset}</Text>
                      <Text style={[styles.tradePnL, { color: trade.pnl >= 0 ? theme.colors.buy : theme.colors.sell }]}>
                        {formatCurrency(trade.pnl)}
                      </Text>
                    </View>
                    <Text style={styles.tradeStrategy}>{trade.strategy}</Text>
                    <Text style={styles.tradeDate}>{trade.date}</Text>
                  </Card.Content>
                </Card>
              ))
            ) : (
              <Card style={[styles.emptyCard, shadows.sm]}>
                <Card.Content style={styles.emptyContent}>
                  <Icon name="history" size={48} color={theme.colors.onSurfaceVariant} />
                  <Text style={styles.emptyText}>No recent trades</Text>
                </Card.Content>
              </Card>
            )}
          </View>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scrollView: { flex: 1 },
  scrollContent: { padding: spacing.lg },

  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  headerTitle: { ...typography.h3, color: theme.colors.onSurface },
  refreshButton: { borderColor: theme.colors.primary },

  summaryCard: { marginBottom: spacing.xl, borderRadius: borderRadius.lg },
  summaryTitle: { ...typography.h5, marginBottom: spacing.lg },
  summaryGrid: { flexDirection: 'row', flexWrap: 'wrap' },
  summaryItem: { width: '50%', marginBottom: spacing.lg },
  summaryValue: { ...typography.h4, fontWeight: 'bold' },
  summaryLabel: { ...typography.body2, color: theme.colors.onSurfaceVariant, marginTop: 4 },

  section: { marginBottom: spacing.xl },
  sectionTitle: { ...typography.h4, marginBottom: spacing.lg },

  positionCard: { marginBottom: spacing.md, borderRadius: borderRadius.lg },
  positionHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: spacing.sm },
  positionAsset: { ...typography.h5, fontWeight: 'bold' },
  positionDirection: { height: 24 },
  positionDetails: { gap: 4 },

  tradeCard: { marginBottom: spacing.sm, borderRadius: borderRadius.lg },
  tradeHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  tradeAsset: { ...typography.body1, fontWeight: '600' },
  tradePnL: { ...typography.body1, fontWeight: 'bold' },
  tradeStrategy: { ...typography.body2, color: theme.colors.onSurfaceVariant },
  tradeDate: { ...typography.caption, color: theme.colors.onSurfaceVariant },

  emptyCard: { borderRadius: borderRadius.lg },
  emptyContent: { alignItems: 'center', padding: spacing.xl },
  emptyText: { ...typography.body1, color: theme.colors.onSurfaceVariant, marginTop: spacing.md },
});

export default PortfolioScreen;
