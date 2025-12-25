import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, Card, Title, Button, Avatar, Switch, List } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { theme, spacing, borderRadius, typography, shadows } from '../styles/theme';
import { User } from '../types';
import apiService from '../services/api';

const ProfileScreen: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notifications, setNotifications] = useState({
    signals: true,
    priceAlerts: true,
    news: true,
    sessionAlerts: true,
  });

  useEffect(() => {
    loadUserProfile();
    loadNotificationSettings();
  }, []);

  const loadUserProfile = async () => {
    try {
      const result = await apiService.getUserProfile();
      if (result.success) {
        setUser(result.data);
      }
    } catch (error) {
      console.error('Failed to load user profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadNotificationSettings = async () => {
    try {
      const settings = await AsyncStorage.getItem('notification_settings');
      if (settings) {
        setNotifications(JSON.parse(settings));
      }
    } catch (error) {
      console.error('Failed to load notification settings:', error);
    }
  };

  const saveNotificationSettings = async (newSettings: typeof notifications) => {
    try {
      await AsyncStorage.setItem('notification_settings', JSON.stringify(newSettings));
      setNotifications(newSettings);
    } catch (error) {
      console.error('Failed to save notification settings:', error);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              await apiService.logout();
              // Navigation will be handled by the app
            } catch (error) {
              Alert.alert('Error', 'Failed to logout');
            }
          },
        },
      ]
    );
  };

  const getSubscriptionColor = (subscription: string) => {
    switch (subscription) {
      case 'vip': return theme.colors.warning;
      case 'premium': return theme.colors.primary;
      default: return theme.colors.onSurfaceVariant;
    }
  };

  const getSubscriptionIcon = (subscription: string) => {
    switch (subscription) {
      case 'vip': return 'crown';
      case 'premium': return 'star';
      default: return 'account';
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading Profile...</Text>
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
            <Title style={styles.headerTitle}>Profile</Title>
          </View>

          {/* User Info */}
          {user && (
            <Card style={[styles.userCard, shadows.lg]}>
              <Card.Content style={styles.userContent}>
                <View style={styles.userHeader}>
                  <Avatar.Text
                    size={80}
                    label={user.username.charAt(0).toUpperCase()}
                    style={[styles.avatar, { backgroundColor: getSubscriptionColor(user.subscription) }]}
                  />
                  <View style={styles.userInfo}>
                    <Text style={styles.username}>{user.username}</Text>
                    <Text style={styles.email}>{user.email}</Text>
                    <View style={styles.subscriptionBadge}>
                      <Icon
                        name={getSubscriptionIcon(user.subscription)}
                        size={16}
                        color={getSubscriptionColor(user.subscription)}
                      />
                      <Text style={[styles.subscriptionText, { color: getSubscriptionColor(user.subscription) }]}>
                        {user.subscription.charAt(0).toUpperCase() + user.subscription.slice(1)}
                      </Text>
                    </View>
                  </View>
                </View>
              </Card.Content>
            </Card>
          )}

          {/* Subscription Info */}
          <Card style={[styles.subscriptionCard, shadows.md]}>
            <Card.Content>
              <Text style={styles.cardTitle}>Subscription</Text>
              <View style={styles.subscriptionInfo}>
                <Text style={styles.subscriptionPlan}>
                  {user?.subscription.charAt(0).toUpperCase() + user?.subscription.slice(1)} Plan
                </Text>
                <Text style={styles.subscriptionFeatures}>
                  {user?.subscription === 'vip'
                    ? 'All Premium features + Broker integration + 1-on-1 calls'
                    : user?.subscription === 'premium'
                    ? 'All features + AI insights + Quantum signals'
                    : 'Basic signals for 2 pairs'
                  }
                </Text>
                <Button
                  mode="outlined"
                  onPress={() => {/* Navigate to upgrade */}}
                  style={styles.upgradeButton}
                >
                  {user?.subscription === 'free' ? 'Upgrade' : 'Manage'}
                </Button>
              </View>
            </Card.Content>
          </Card>

          {/* Notification Settings */}
          <Card style={[styles.settingsCard, shadows.md]}>
            <Card.Content>
              <Text style={styles.cardTitle}>Notifications</Text>

              <List.Section>
                <List.Item
                  title="Trading Signals"
                  description="Get notified of new trading signals"
                  left={() => <List.Icon icon="lightning-bolt" />}
                  right={() => (
                    <Switch
                      value={notifications.signals}
                      onValueChange={(value) =>
                        saveNotificationSettings({ ...notifications, signals: value })
                      }
                    />
                  )}
                />

                <List.Item
                  title="Price Alerts"
                  description="Alerts when price levels are reached"
                  left={() => <List.Icon icon="bell" />}
                  right={() => (
                    <Switch
                      value={notifications.priceAlerts}
                      onValueChange={(value) =>
                        saveNotificationSettings({ ...notifications, priceAlerts: value })
                      }
                    />
                  )}
                />

                <List.Item
                  title="Market News"
                  description="Latest market news and updates"
                  left={() => <List.Icon icon="newspaper" />}
                  right={() => (
                    <Switch
                      value={notifications.news}
                      onValueChange={(value) =>
                        saveNotificationSettings({ ...notifications, news: value })
                      }
                    />
                  )}
                />

                <List.Item
                  title="Session Alerts"
                  description="Trading session start/end reminders"
                  left={() => <List.Icon icon="clock" />}
                  right={() => (
                    <Switch
                      value={notifications.sessionAlerts}
                      onValueChange={(value) =>
                        saveNotificationSettings({ ...notifications, sessionAlerts: value })
                      }
                    />
                  )}
                />
              </List.Section>
            </Card.Content>
          </Card>

          {/* App Settings */}
          <Card style={[styles.settingsCard, shadows.md]}>
            <Card.Content>
              <Text style={styles.cardTitle}>App Settings</Text>

              <List.Section>
                <List.Item
                  title="Theme"
                  description="Dark theme (optimized for trading)"
                  left={() => <List.Icon icon="theme-light-dark" />}
                  right={() => <Text style={styles.settingValue}>Dark</Text>}
                />

                <List.Item
                  title="Language"
                  description="App language"
                  left={() => <List.Icon icon="translate" />}
                  right={() => <Text style={styles.settingValue}>English</Text>}
                />

                <List.Item
                  title="Risk Level"
                  description="Default risk tolerance"
                  left={() => <List.Icon icon="gauge" />}
                  right={() => <Text style={styles.settingValue}>Moderate</Text>}
                />
              </List.Section>
            </Card.Content>
          </Card>

          {/* Support & Help */}
          <Card style={[styles.settingsCard, shadows.md]}>
            <Card.Content>
              <Text style={styles.cardTitle}>Support & Help</Text>

              <List.Section>
                <List.Item
                  title="Help Center"
                  description="FAQs and tutorials"
                  left={() => <List.Icon icon="help-circle" />}
                  onPress={() => {/* Navigate to help */}}
                />

                <List.Item
                  title="Contact Support"
                  description="Get help from our team"
                  left={() => <List.Icon icon="email" />}
                  onPress={() => {/* Open support */}}
                />

                <List.Item
                  title="Telegram Bot"
                  description="Access your trading bot"
                  left={() => <List.Icon icon="telegram" />}
                  onPress={() => {/* Open Telegram */}}
                />

                <List.Item
                  title="Privacy Policy"
                  description="How we protect your data"
                  left={() => <List.Icon icon="shield-check" />}
                  onPress={() => {/* Show privacy policy */}}
                />
              </List.Section>
            </Card.Content>
          </Card>

          {/* Logout Button */}
          <Button
            mode="contained"
            onPress={handleLogout}
            style={styles.logoutButton}
            contentStyle={styles.logoutButtonContent}
            color={theme.colors.sell}
          >
            <Icon name="logout" size={16} color="white" />
            <Text style={styles.logoutButtonText}>Sign Out</Text>
          </Button>

          {/* App Version */}
          <Text style={styles.versionText}>UR Trading Expert v1.0.0</Text>
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

  header: { marginBottom: spacing.lg },
  headerTitle: { ...typography.h3, color: theme.colors.onSurface },

  userCard: { marginBottom: spacing.lg, borderRadius: borderRadius.lg },
  userContent: { padding: spacing.lg },
  userHeader: { flexDirection: 'row', alignItems: 'center' },
  avatar: { marginRight: spacing.lg },
  userInfo: { flex: 1 },
  username: { ...typography.h4, fontWeight: 'bold', marginBottom: 4 },
  email: { ...typography.body2, color: theme.colors.onSurfaceVariant, marginBottom: spacing.sm },
  subscriptionBadge: { flexDirection: 'row', alignItems: 'center' },
  subscriptionText: { ...typography.body2, fontWeight: '600', marginLeft: 4 },

  subscriptionCard: { marginBottom: spacing.lg, borderRadius: borderRadius.lg },
  cardTitle: { ...typography.h6, fontWeight: 'bold', marginBottom: spacing.md },
  subscriptionInfo: { alignItems: 'center' },
  subscriptionPlan: { ...typography.h5, fontWeight: 'bold', marginBottom: spacing.sm },
  subscriptionFeatures: {
    ...typography.body2,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
    marginBottom: spacing.lg,
    lineHeight: 20,
  },
  upgradeButton: { minWidth: 120 },

  settingsCard: { marginBottom: spacing.md, borderRadius: borderRadius.lg },
  settingValue: { ...typography.body2, color: theme.colors.primary },

  logoutButton: {
    marginTop: spacing.xl,
    marginBottom: spacing.lg,
    borderRadius: borderRadius.md,
  },
  logoutButtonContent: { paddingVertical: spacing.sm },
  logoutButtonText: { color: 'white', marginLeft: spacing.sm },

  versionText: {
    ...typography.caption,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
});

export default ProfileScreen;
