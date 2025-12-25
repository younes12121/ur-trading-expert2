import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, Card, Title, Button, Chip } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { theme, spacing, borderRadius, typography, shadows } from '../styles/theme';
import { MarketData } from '../types';
import apiService from '../services/api';

const MarketsScreen: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadMarketData();
  }, []);

  const loadMarketData = async () => {
    try {
      const result = await apiService.getMarketOverview();
      if (result.success) {
        setMarketData(result.data || []);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load market data');
    } finally {
      setIsLoading(false);
    }
  };

  const getMarketStatusColor = (status: string) => {
    switch (status) {
      case 'bullish': return theme.colors.buy;
      case 'bearish': return theme.colors.sell;
      default: return theme.colors.warning;
    }
  };

  const getMarketIcon = (region: string) => {
    switch (region.toLowerCase()) {
      case 'asia': return 'sun';
      case 'europe': return 'map-marker';
      case 'americas': return 'earth';
      case 'crypto': return 'bitcoin';
      default: return 'globe-model';
    }
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading Markets...</Text>
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
            <Title style={styles.headerTitle}>Markets</Title>
            <Button
              mode="outlined"
              onPress={loadMarketData}
              style={styles.refreshButton}
            >
              <Icon name="refresh" size={16} color={theme.colors.primary} />
            </Button>
          </View>

          {/* Market Overview */}
          <Text style={styles.sectionTitle}>Global Market Overview</Text>

          {marketData.length > 0 ? (
            <View style={styles.marketsGrid}>
              {marketData.map((market) => (
                <Card key={market.region} style={[styles.marketCard, shadows.md]}>
                  <Card.Content style={styles.marketContent}>
                    <View style={styles.marketHeader}>
                      <View style={styles.marketIconContainer}>
                        <Icon
                          name={getMarketIcon(market.region)}
                          size={24}
                          color={getMarketStatusColor(market.status)}
                        />
                      </View>
                      <View style={styles.marketInfo}>
                        <Text style={styles.marketRegion}>{market.region}</Text>
                        <Chip
                          style={[
                            styles.marketStatusChip,
                            { backgroundColor: getMarketStatusColor(market.status) }
                          ]}
                          textStyle={styles.marketStatusText}
                        >
                          {market.status.charAt(0).toUpperCase() + market.status.slice(1)}
                        </Chip>
                      </View>
                    </View>

                    <View style={styles.marketChange}>
                      <Text style={[styles.changeValue, { color: market.change >= 0 ? theme.colors.buy : theme.colors.sell }]}>
                        {formatPercent(market.change)}
                      </Text>
                      <Text style={styles.changeLabel}>24h Change</Text>
                    </View>
                  </Card.Content>
                </Card>
              ))}
            </View>
          ) : (
            <Card style={[styles.emptyCard, shadows.sm]}>
              <Card.Content style={styles.emptyContent}>
                <Icon name="globe-model" size={48} color={theme.colors.onSurfaceVariant} />
                <Text style={styles.emptyText}>No market data available</Text>
              </Card.Content>
            </Card>
          )}

          {/* Trading Assets */}
          <View style={styles.assetsSection}>
            <Text style={styles.sectionTitle}>Trading Assets</Text>

            <View style={styles.assetCategories}>
              <Card style={[styles.assetCard, shadows.sm]}>
                <Card.Content>
                  <Text style={styles.assetCategoryTitle}>Crypto</Text>
                  <View style={styles.assetList}>
                    <Chip style={styles.assetChip}>BTC/USD</Chip>
                    <Chip style={styles.assetChip}>ETH/USD</Chip>
                  </View>
                </Card.Content>
              </Card>

              <Card style={[styles.assetCard, shadows.sm]}>
                <Card.Content>
                  <Text style={styles.assetCategoryTitle}>Forex</Text>
                  <View style={styles.assetList}>
                    <Chip style={styles.assetChip}>EUR/USD</Chip>
                    <Chip style={styles.assetChip}>GBP/USD</Chip>
                    <Chip style={styles.assetChip}>USD/JPY</Chip>
                  </View>
                </Card.Content>
              </Card>

              <Card style={[styles.assetCard, shadows.sm]}>
                <Card.Content>
                  <Text style={styles.assetCategoryTitle}>Commodities</Text>
                  <View style={styles.assetList}>
                    <Chip style={styles.assetChip}>XAU/USD</Chip>
                  </View>
                </Card.Content>
              </Card>

              <Card style={[styles.assetCard, shadows.sm]}>
                <Card.Content>
                  <Text style={styles.assetCategoryTitle}>Futures</Text>
                  <View style={styles.assetList}>
                    <Chip style={styles.assetChip}>ES</Chip>
                    <Chip style={styles.assetChip}>NQ</Chip>
                  </View>
                </Card.Content>
              </Card>
            </View>
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

  sectionTitle: { ...typography.h4, marginBottom: spacing.lg },

  marketsGrid: { marginBottom: spacing.xl },
  marketCard: { marginBottom: spacing.md, borderRadius: borderRadius.lg },
  marketContent: { padding: spacing.lg },
  marketHeader: { flexDirection: 'row', marginBottom: spacing.md },
  marketIconContainer: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.lg,
    backgroundColor: theme.colors.surfaceVariant,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  marketInfo: { flex: 1 },
  marketRegion: { ...typography.h5, fontWeight: 'bold', marginBottom: spacing.xs },
  marketStatusChip: { height: 24, alignSelf: 'flex-start' },
  marketStatusText: { color: 'white', fontSize: 11, fontWeight: 'bold' },
  marketChange: { alignItems: 'flex-end' },
  changeValue: { ...typography.h4, fontWeight: 'bold' },
  changeLabel: { ...typography.caption, color: theme.colors.onSurfaceVariant },

  assetsSection: { marginBottom: spacing.xl },
  assetCategories: { gap: spacing.md },
  assetCard: { borderRadius: borderRadius.lg },
  assetCategoryTitle: { ...typography.h6, fontWeight: 'bold', marginBottom: spacing.sm },
  assetList: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  assetChip: { margin: 0 },

  emptyCard: { borderRadius: borderRadius.lg },
  emptyContent: { alignItems: 'center', padding: spacing.xl },
  emptyText: { ...typography.body1, color: theme.colors.onSurfaceVariant, marginTop: spacing.md },
});

export default MarketsScreen;
