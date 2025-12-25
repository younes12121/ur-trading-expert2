import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Title, Button, Chip, Paragraph } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { theme, spacing, borderRadius, typography, shadows } from '../styles/theme';

const SignalDetailScreen: React.FC = () => {
  // This would receive the signal as a route param
  // For now, showing a placeholder
  return (
    <LinearGradient
      colors={[theme.colors.background, theme.colors.surface]}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
          <View style={styles.header}>
            <Title style={styles.headerTitle}>Signal Details</Title>
          </View>

          <Card style={[styles.signalCard, shadows.lg]}>
            <Card.Content>
              <Text style={styles.comingSoon}>Signal details coming soon!</Text>
              <Text style={styles.description}>
                This screen will show detailed analysis of individual trading signals.
              </Text>
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
  signalCard: { borderRadius: borderRadius.lg },
  comingSoon: { ...typography.h5, textAlign: 'center', marginBottom: spacing.md },
  description: { ...typography.body1, textAlign: 'center', color: theme.colors.onSurfaceVariant },
});

export default SignalDetailScreen;
