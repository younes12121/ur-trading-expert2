import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Card,
  Title,
  Paragraph,
  IconButton,
  Chip,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import LinearGradient from 'react-native-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme, spacing, borderRadius } from '../styles/theme';
import apiService from '../services/api';

const AuthScreen: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }

    if (!isLogin) {
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = 'Please enter a valid email';
      }
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      let result;

      if (isLogin) {
        result = await apiService.login(formData.username, formData.password);
      } else {
        result = await apiService.register({
          username: formData.username,
          email: formData.email,
          password: formData.password,
        });
      }

      if (result.success) {
        // Store user data and navigate to main app
        if (result.data) {
          await AsyncStorage.setItem('user_data', JSON.stringify(result.data.user));
        }
        // Navigation will be handled by the App component
        Alert.alert('Success', isLogin ? 'Welcome back!' : 'Account created successfully!');
      } else {
        Alert.alert('Error', result.error || 'Something went wrong');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setErrors({});
    setFormData({
      username: '',
      email: '',
      password: '',
    });
  };

  return (
    <LinearGradient
      colors={[theme.colors.background, theme.colors.surface]}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardAvoidingView}
        >
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
          >
            {/* Header */}
            <View style={styles.header}>
              <View style={styles.logoContainer}>
                <LinearGradient
                  colors={[theme.colors.primary, theme.colors.secondary]}
                  style={styles.logoBackground}
                >
                  <Text style={styles.logoIcon}>📈</Text>
                </LinearGradient>
              </View>
              <Title style={styles.title}>UR Trading Expert</Title>
              <Paragraph style={styles.subtitle}>
                Professional AI-Powered Trading Signals
              </Paragraph>
            </View>

            {/* Auth Form */}
            <Card style={styles.authCard}>
              <Card.Content style={styles.cardContent}>
                <View style={styles.tabContainer}>
                  <Chip
                    selected={isLogin}
                    onPress={() => setIsLogin(true)}
                    style={[styles.tabChip, isLogin && styles.activeTabChip]}
                    textStyle={[styles.tabText, isLogin && styles.activeTabText]}
                  >
                    Sign In
                  </Chip>
                  <Chip
                    selected={!isLogin}
                    onPress={() => setIsLogin(false)}
                    style={[styles.tabChip, !isLogin && styles.activeTabChip]}
                    textStyle={[styles.tabText, !isLogin && styles.activeTabText]}
                  >
                    Register
                  </Chip>
                </View>

                <View style={styles.form}>
                  {/* Username */}
                  <TextInput
                    label="Username"
                    value={formData.username}
                    onChangeText={(text) => {
                      setFormData({ ...formData, username: text });
                      if (errors.username) setErrors({ ...errors, username: '' });
                    }}
                    mode="outlined"
                    style={styles.input}
                    error={!!errors.username}
                    disabled={isLoading}
                    autoCapitalize="none"
                    autoCorrect={false}
                  />
                  {errors.username && (
                    <Text style={styles.errorText}>{errors.username}</Text>
                  )}

                  {/* Email (only for registration) */}
                  {!isLogin && (
                    <>
                      <TextInput
                        label="Email"
                        value={formData.email}
                        onChangeText={(text) => {
                          setFormData({ ...formData, email: text });
                          if (errors.email) setErrors({ ...errors, email: '' });
                        }}
                        mode="outlined"
                        style={styles.input}
                        error={!!errors.email}
                        disabled={isLoading}
                        keyboardType="email-address"
                        autoCapitalize="none"
                        autoCorrect={false}
                      />
                      {errors.email && (
                        <Text style={styles.errorText}>{errors.email}</Text>
                      )}
                    </>
                  )}

                  {/* Password */}
                  <TextInput
                    label="Password"
                    value={formData.password}
                    onChangeText={(text) => {
                      setFormData({ ...formData, password: text });
                      if (errors.password) setErrors({ ...errors, password: '' });
                    }}
                    mode="outlined"
                    style={styles.input}
                    error={!!errors.password}
                    disabled={isLoading}
                    secureTextEntry={!showPassword}
                    right={
                      <TextInput.Icon
                        icon={showPassword ? 'eye-off' : 'eye'}
                        onPress={() => setShowPassword(!showPassword)}
                      />
                    }
                  />
                  {errors.password && (
                    <Text style={styles.errorText}>{errors.password}</Text>
                  )}

                  {/* Submit Button */}
                  <Button
                    mode="contained"
                    onPress={handleSubmit}
                    style={styles.submitButton}
                    disabled={isLoading}
                    contentStyle={styles.submitButtonContent}
                  >
                    {isLoading ? (
                      <ActivityIndicator color={theme.colors.onPrimary} />
                    ) : (
                      <Text style={styles.submitButtonText}>
                        {isLogin ? 'Sign In' : 'Create Account'}
                      </Text>
                    )}
                  </Button>
                </View>

                {/* Demo Credentials */}
                <View style={styles.demoContainer}>
                  <Text style={styles.demoTitle}>Demo Credentials:</Text>
                  <Text style={styles.demoText}>Username: admin</Text>
                  <Text style={styles.demoText}>Password: admin</Text>
                </View>
              </Card.Content>
            </Card>

            {/* Footer */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>
                {isLogin ? "Don't have an account?" : 'Already have an account?'}
              </Text>
              <Button
                mode="text"
                onPress={toggleMode}
                labelStyle={styles.footerButtonText}
              >
                {isLogin ? 'Create Account' : 'Sign In'}
              </Button>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
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
  keyboardAvoidingView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: spacing.lg,
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing.xxl,
  },
  logoContainer: {
    marginBottom: spacing.lg,
  },
  logoBackground: {
    width: 80,
    height: 80,
    borderRadius: borderRadius.xl,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoIcon: {
    fontSize: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.colors.onSurface,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
    lineHeight: 24,
  },
  authCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.xl,
    elevation: 8,
  },
  cardContent: {
    padding: spacing.lg,
  },
  tabContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: spacing.lg,
    gap: spacing.sm,
  },
  tabChip: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: theme.colors.outline,
  },
  activeTabChip: {
    backgroundColor: theme.colors.primaryContainer,
    borderColor: theme.colors.primary,
  },
  tabText: {
    color: theme.colors.onSurfaceVariant,
  },
  activeTabText: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  form: {
    marginTop: spacing.md,
  },
  input: {
    marginBottom: spacing.sm,
    backgroundColor: theme.colors.surface,
  },
  errorText: {
    color: theme.colors.error,
    fontSize: 12,
    marginBottom: spacing.sm,
    marginLeft: spacing.sm,
  },
  submitButton: {
    marginTop: spacing.md,
    borderRadius: borderRadius.md,
  },
  submitButtonContent: {
    paddingVertical: spacing.sm,
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  demoContainer: {
    marginTop: spacing.lg,
    padding: spacing.md,
    backgroundColor: theme.colors.surfaceVariant,
    borderRadius: borderRadius.md,
  },
  demoTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.onSurfaceVariant,
    marginBottom: spacing.sm,
  },
  demoText: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    fontFamily: 'monospace',
  },
  footer: {
    alignItems: 'center',
    marginTop: spacing.xl,
  },
  footerText: {
    color: theme.colors.onSurfaceVariant,
    fontSize: 14,
  },
  footerButtonText: {
    color: theme.colors.primary,
    fontSize: 14,
    fontWeight: '600',
  },
});

export default AuthScreen;
