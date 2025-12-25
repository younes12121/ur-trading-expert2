import React, { useEffect, useState } from 'react';
import { StatusBar, StyleSheet, View, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Import screens
import AuthScreen from './src/screens/AuthScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import SignalsScreen from './src/screens/SignalsScreen';
import PortfolioScreen from './src/screens/PortfolioScreen';
import MarketsScreen from './src/screens/MarketsScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SignalDetailScreen from './src/screens/SignalDetailScreen';
import AssetDetailScreen from './src/screens/AssetDetailScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Import components
import TabBar from './src/components/TabBar';

// Import theme
import { theme } from './src/styles/theme';

// Import types
import { RootStackParamList, TabParamList } from './src/types';

// Import services
import apiService from './src/services/api';

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();

function TabNavigator() {
  return (
    <Tab.Navigator
      tabBar={(props) => <TabBar {...props} />}
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.outline,
          borderTopWidth: 1,
        },
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          tabBarLabel: 'Dashboard',
        }}
      />
      <Tab.Screen
        name="Signals"
        component={SignalsScreen}
        options={{
          tabBarLabel: 'Signals',
        }}
      />
      <Tab.Screen
        name="Portfolio"
        component={PortfolioScreen}
        options={{
          tabBarLabel: 'Portfolio',
        }}
      />
      <Tab.Screen
        name="Markets"
        component={MarketsScreen}
        options={{
          tabBarLabel: 'Markets',
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',
        }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthentication();
    initializeApp();
  }, []);

  const checkAuthentication = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        // Verify token with backend
        const isValid = await apiService.healthCheck();
        setIsAuthenticated(isValid);
      }
    } catch (error) {
      console.error('Authentication check failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const initializeApp = async () => {
    // Initialize push notifications
    // Initialize other services
    console.log('Initializing UR Trading Expert Mobile App');
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <StatusBar
          barStyle="light-content"
          backgroundColor={theme.colors.surface}
        />
        <NavigationContainer
          theme={{
            dark: true,
            colors: {
              primary: theme.colors.primary,
              background: theme.colors.background,
              card: theme.colors.surface,
              text: theme.colors.onSurface,
              border: theme.colors.outline,
              notification: theme.colors.error,
            },
          }}
        >
          <Stack.Navigator
            screenOptions={{
              headerStyle: {
                backgroundColor: theme.colors.surface,
              },
              headerTintColor: theme.colors.onSurface,
              headerTitleStyle: {
                fontWeight: 'bold',
              },
              animation: 'slide_from_right',
            }}
          >
            {isAuthenticated ? (
              // Authenticated user screens
              <>
                <Stack.Screen
                  name="Main"
                  component={TabNavigator}
                  options={{ headerShown: false }}
                />
                <Stack.Screen
                  name="SignalDetail"
                  component={SignalDetailScreen}
                  options={{
                    title: 'Signal Details',
                    headerBackTitleVisible: false,
                  }}
                />
                <Stack.Screen
                  name="AssetDetail"
                  component={AssetDetailScreen}
                  options={{
                    title: 'Asset Details',
                    headerBackTitleVisible: false,
                  }}
                />
                <Stack.Screen
                  name="Settings"
                  component={SettingsScreen}
                  options={{
                    title: 'Settings',
                    headerBackTitleVisible: false,
                  }}
                />
              </>
            ) : (
              // Authentication screen
              <Stack.Screen
                name="Auth"
                component={AuthScreen}
                options={{ headerShown: false }}
              />
            )}
          </Stack.Navigator>
        </NavigationContainer>
      </PaperProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
});
