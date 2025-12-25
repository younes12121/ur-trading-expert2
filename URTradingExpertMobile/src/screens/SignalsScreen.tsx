import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  FlatList,
} from 'react-native';
import {
  Text,
  Card,
  Title,
  Button,
  Chip,
  Searchbar,
  FAB,
  Menu,
  Divider,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { theme, spacing, borderRadius, typography, shadows } from '../styles/theme';
import { TradingSignal } from '../types';
import apiService from '../services/api';

const SignalsScreen: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [filteredSignals, setFilteredSignals] = useState<TradingSignal[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'buy' | 'sell' | 'high-confidence'>('all');
  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    loadSignals();

    // Set up real-time signal updates
    const unsubscribeSignals = apiService.subscribeToSignals((signal) => {
      setSignals(prev => [signal, ...prev]);
    });

    return () => {
      unsubscribeSignals();
    };
  }, []);

  useEffect(() => {
    filterSignals();
  }, [signals, searchQuery, selectedFilter]);

  const loadSignals = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await apiService.getLiveSignals();
      if (result.success) {
        setSignals(result.data || []);
      } else {
        Alert.alert('Error', result.error || 'Failed to load signals');
      }
    } catch (error) {
      console.error('Failed to load signals:', error);
      Alert.alert('Error', 'Failed to load signals');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const onRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await loadSignals();
    setIsRefreshing(false);
  }, [loadSignals]);

  const filterSignals = useCallback(() => {
    let filtered = signals;

    // Apply search filter
    if (searchQuery.trim()) {
      filtered = filtered.filter(signal =>
        signal.asset.toLowerCase().includes(searchQuery.toLowerCase()) ||
        signal.analysis.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply category filter
    switch (selectedFilter) {
      case 'buy':
        filtered = filtered.filter(signal => signal.direction === 'BUY');
        break;
      case 'sell':
        filtered = filtered.filter(signal => signal.direction === 'SELL');
        break;
      case 'high-confidence':
        filtered = filtered.filter(signal => signal.confidence >= 80);
        break;
    }

    // Sort by confidence (highest first) and then by timestamp (newest first)
    filtered.sort((a, b) => {
      if (b.confidence !== a.confidence) {
        return b.confidence - a.confidence;
      }
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });

    setFilteredSignals(filtered);
  }, [signals, searchQuery, selectedFilter]);

  const getSignalColor = (direction: string) => {
    switch (direction) {
      case 'BUY': return theme.colors.buy;
      case 'SELL': return theme.colors.sell;
      case 'HOLD': return theme.colors.hold;
      default: return theme.colors.neutral;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'asian': return theme.colors.asian;
      case 'major': return theme.colors.major;
      case 'emerging': return theme.colors.emerging;
      case 'crypto': return theme.colors.crypto;
      default: return theme.colors.neutral;
    }
  };

  const formatPrice = (price: number, asset: string) => {
    if (asset.includes('JPY')) {
      return price.toFixed(2);
    } else if (asset.includes('BTC') || asset.includes('ETH')) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(price);
    } else {
      return price.toFixed(5);
    }
  };

  const renderSignalItem = ({ item }: { item: TradingSignal }) => (
    <Card style={[styles.signalCard, shadows.md]}>
      <Card.Content style={styles.signalCardContent}>
        <View style={styles.signalHeader}>
          <View style={styles.signalTitleSection}>
            <Text style={styles.signalAsset}>{item.asset}</Text>
            <View style={styles.signalBadges}>
              <Chip
                style={[
                  styles.signalDirectionChip,
                  { backgroundColor: getSignalColor(item.direction) }
                ]}
                textStyle={styles.signalDirectionText}
              >
                {item.direction}
              </Chip>
              <Chip
                style={[
                  styles.signalCategoryChip,
                  { backgroundColor: getCategoryColor(item.category) }
                ]}
                textStyle={styles.signalCategoryText}
              >
                {item.category.charAt(0).toUpperCase() + item.category.slice(1)}
              </Chip>
            </View>
          </View>
          <View style={styles.signalConfidence}>
            <Text style={styles.confidenceValue}>{item.confidence}%</Text>
            <Text style={styles.confidenceLabel}>Confidence</Text>
          </View>
        </View>

        <View style={styles.signalDetails}>
          <View style={styles.priceSection}>
            <View style={styles.priceRow}>
              <Text style={styles.priceLabel}>Entry:</Text>
              <Text style={styles.priceValue}>
                {formatPrice(item.entry, item.asset)}
              </Text>
            </View>
            <View style={styles.priceRow}>
              <Text style={[styles.priceLabel, { color: theme.colors.sell }]}>Stop Loss:</Text>
              <Text style={[styles.priceValue, { color: theme.colors.sell }]}>
                {formatPrice(item.stopLoss, item.asset)}
              </Text>
            </View>
            <View style={styles.priceRow}>
              <Text style={[styles.priceLabel, { color: theme.colors.buy }]}>Take Profit:</Text>
              <Text style={[styles.priceValue, { color: theme.colors.buy }]}>
                {formatPrice(item.takeProfit1 || item.entry * 1.02, item.asset)}
              </Text>
            </View>
            {item.takeProfit2 && (
              <View style={styles.priceRow}>
                <Text style={[styles.priceLabel, { color: theme.colors.buy }]}>TP2:</Text>
                <Text style={[styles.priceValue, { color: theme.colors.buy }]}>
                  {formatPrice(item.takeProfit2, item.asset)}
                </Text>
              </View>
            )}
          </View>
        </View>

        <Text style={styles.signalAnalysis} numberOfLines={3}>
          {item.analysis}
        </Text>

        <View style={styles.signalFooter}>
          <Text style={styles.signalTimestamp}>
            {new Date(item.timestamp).toLocaleString()}
          </Text>
          <Button
            mode="outlined"
            onPress={() => {/* Navigate to signal detail */}}
            style={styles.viewDetailsButton}
            labelStyle={styles.viewDetailsButtonText}
          >
            View Details
          </Button>
        </View>
      </Card.Content>
    </Card>
  );

  const filterOptions = [
    { label: 'All Signals', value: 'all' },
    { label: 'Buy Only', value: 'buy' },
    { label: 'Sell Only', value: 'sell' },
    { label: 'High Confidence (80%+)', value: 'high-confidence' },
  ];

  return (
    <LinearGradient
      colors={[theme.colors.background, theme.colors.surface]}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        {/* Header */}
        <View style={styles.header}>
          <Title style={styles.headerTitle}>Trading Signals</Title>
          <Menu
            visible={menuVisible}
            onDismiss={() => setMenuVisible(false)}
            anchor={
              <Button
                mode="outlined"
                onPress={() => setMenuVisible(true)}
                style={styles.filterButton}
                contentStyle={styles.filterButtonContent}
              >
                <Icon name="filter-variant" size={16} color={theme.colors.primary} />
                <Text style={styles.filterButtonText}>
                  {filterOptions.find(opt => opt.value === selectedFilter)?.label}
                </Text>
              </Button>
            }
          >
            {filterOptions.map((option) => (
              <Menu.Item
                key={option.value}
                onPress={() => {
                  setSelectedFilter(option.value as any);
                  setMenuVisible(false);
                }}
                title={option.label}
                style={selectedFilter === option.value ? styles.selectedMenuItem : {}}
              />
            ))}
          </Menu>
        </View>

        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <Searchbar
            placeholder="Search signals..."
            onChangeText={setSearchQuery}
            value={searchQuery}
            style={styles.searchBar}
            inputStyle={styles.searchInput}
            iconColor={theme.colors.onSurfaceVariant}
            placeholderTextColor={theme.colors.onSurfaceVariant}
          />
        </View>

        {/* Signals List */}
        <FlatList
          data={filteredSignals}
          keyExtractor={(item) => item.id || `${item.asset}-${item.timestamp}`}
          renderItem={renderSignalItem}
          contentContainerStyle={styles.signalsList}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={isRefreshing}
              onRefresh={onRefresh}
              colors={[theme.colors.primary]}
              tintColor={theme.colors.primary}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Icon name="lightning-bolt-outline" size={64} color={theme.colors.onSurfaceVariant} />
              <Text style={styles.emptyTitle}>No Signals Found</Text>
              <Text style={styles.emptySubtitle}>
                {searchQuery || selectedFilter !== 'all'
                  ? 'Try adjusting your search or filter criteria'
                  : 'Live signals will appear here when available'
                }
              </Text>
              <Button
                mode="contained"
                onPress={onRefresh}
                style={styles.refreshEmptyButton}
              >
                Refresh
              </Button>
            </View>
          }
          ListHeaderComponent={
            filteredSignals.length > 0 ? (
              <View style={styles.listHeader}>
                <Text style={styles.resultsCount}>
                  {filteredSignals.length} signal{filteredSignals.length !== 1 ? 's' : ''} found
                </Text>
              </View>
            ) : null
          }
        />

        {/* FAB for quick actions */}
        <FAB
          icon="telegram"
          onPress={() => {/* Open Telegram bot */}}
          style={styles.fab}
          color={theme.colors.onPrimary}
        />
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.outline,
  },
  headerTitle: {
    ...typography.h3,
    color: theme.colors.onSurface,
  },
  filterButton: {
    borderColor: theme.colors.outline,
  },
  filterButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterButtonText: {
    color: theme.colors.primary,
    fontSize: 14,
    marginLeft: spacing.xs,
  },
  selectedMenuItem: {
    backgroundColor: theme.colors.primaryContainer,
  },
  searchContainer: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.md,
  },
  searchBar: {
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.lg,
    elevation: 2,
  },
  searchInput: {
    color: theme.colors.onSurface,
  },
  signalsList: {
    padding: spacing.lg,
    paddingTop: 0,
  },
  listHeader: {
    marginBottom: spacing.md,
  },
  resultsCount: {
    ...typography.body2,
    color: theme.colors.onSurfaceVariant,
  },
  signalCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
    backgroundColor: theme.colors.surface,
  },
  signalCardContent: {
    padding: spacing.lg,
  },
  signalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  signalTitleSection: {
    flex: 1,
  },
  signalAsset: {
    ...typography.h4,
    color: theme.colors.onSurface,
    fontWeight: 'bold',
    marginBottom: spacing.sm,
  },
  signalBadges: {
    flexDirection: 'row',
    gap: spacing.xs,
  },
  signalDirectionChip: {
    height: 24,
  },
  signalDirectionText: {
    color: 'white',
    fontSize: 11,
    fontWeight: 'bold',
  },
  signalCategoryChip: {
    height: 24,
  },
  signalCategoryText: {
    color: 'white',
    fontSize: 10,
    fontWeight: '600',
  },
  signalConfidence: {
    alignItems: 'flex-end',
  },
  confidenceValue: {
    ...typography.h4,
    color: theme.colors.primary,
    fontWeight: 'bold',
  },
  confidenceLabel: {
    fontSize: 10,
    color: theme.colors.onSurfaceVariant,
    textTransform: 'uppercase',
    fontWeight: '600',
  },
  signalDetails: {
    marginBottom: spacing.md,
  },
  priceSection: {
    backgroundColor: theme.colors.surfaceVariant,
    borderRadius: borderRadius.md,
    padding: spacing.md,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  priceLabel: {
    ...typography.body2,
    color: theme.colors.onSurfaceVariant,
    fontWeight: '600',
  },
  priceValue: {
    ...typography.body2,
    color: theme.colors.onSurface,
    fontWeight: 'bold',
    fontFamily: 'monospace',
  },
  signalAnalysis: {
    ...typography.body1,
    color: theme.colors.onSurfaceVariant,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  signalFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  signalTimestamp: {
    ...typography.caption,
    color: theme.colors.onSurfaceVariant,
  },
  viewDetailsButton: {
    borderColor: theme.colors.primary,
  },
  viewDetailsButtonText: {
    color: theme.colors.primary,
    fontSize: 12,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.xxl,
  },
  emptyTitle: {
    ...typography.h5,
    color: theme.colors.onSurface,
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  emptySubtitle: {
    ...typography.body2,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
    marginBottom: spacing.lg,
    maxWidth: 300,
  },
  refreshEmptyButton: {
    borderRadius: borderRadius.md,
  },
  fab: {
    position: 'absolute',
    margin: spacing.lg,
    right: 0,
    bottom: 0,
    backgroundColor: theme.colors.primary,
  },
});

export default SignalsScreen;
