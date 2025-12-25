import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Title, List, Switch } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import LinearGradient from 'react-native-linear-gradient';

import { theme, spacing, borderRadius, typography, shadows } from '../styles/theme';

const SettingsScreen: React.FC = () => {
  return (
    <LinearGradient
      colors={[theme.colors.background, theme.colors.surface]}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
          <View style={styles.header}>
            <Title style={styles.headerTitle}>Settings</Title>
          </View>

          <Card style={[styles.settingsCard, shadows.md]}>
            <Card.Content>
              <Text style={styles.cardTitle}>App Preferences</Text>

              <List.Section>
                <List.Item
                  title="Notifications"
                  description="Manage push notifications"
                  left={() => <List.Icon icon="bell" />}
                />

                <List.Item
                  title="Theme"
                  description="Dark theme (recommended for trading)"
                  left={() => <List.Icon icon="theme-light-dark" />}
                  right={() => <Text style={styles.settingValue}>Dark</Text>}
                />

                <List.Item
                  title="Language"
                  description="App language"
                  left={() => <List.Icon icon="translate" />}
                  right={() => <Text style={styles.settingValue}>English</Text>}
                />
              </List.Section>
            </Card.Content>
          </Card>
        </ScrollView>
      </SafeAreaView>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  scrollView: { flex: 1 },
  scrollContent: { padding: spacing.lg },
  header: { marginBottom: spacing.lg },
  headerTitle: { ...typography.h3, color: theme.colors.onSurface },
  settingsCard: { borderRadius: borderRadius.lg },
  cardTitle: { ...typography.h6, fontWeight: 'bold', marginBottom: spacing.md },
  settingValue: { ...typography.body2, color: theme.colors.primary },
});

export default SettingsScreen;
