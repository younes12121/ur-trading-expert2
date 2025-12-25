import React from 'react';
import { View, TouchableOpacity, StyleSheet, Text } from 'react-native';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { theme } from '../styles/theme';

const TabBar: React.FC<BottomTabBarProps> = ({ state, descriptors, navigation }) => {
  const tabIcons = {
    Dashboard: 'view-dashboard',
    Signals: 'lightning-bolt',
    Portfolio: 'briefcase',
    Markets: 'globe-model',
    Profile: 'account',
  };

  return (
    <View style={styles.container}>
      {state.routes.map((route, index) => {
        const { options } = descriptors[route.key];
        const label = options.tabBarLabel || route.name;
        const isFocused = state.index === index;
        const iconName = tabIcons[route.name as keyof typeof tabIcons] || 'circle';

        const onPress = () => {
          const event = navigation.emit({
            type: 'tabPress',
            target: route.key,
            canPreventDefault: true,
          });

          if (!isFocused && !event.defaultPrevented) {
            navigation.navigate(route.name);
          }
        };

        const onLongPress = () => {
          navigation.emit({
            type: 'tabLongPress',
            target: route.key,
          });
        };

        return (
          <TouchableOpacity
            key={route.key}
            accessibilityRole="button"
            accessibilityState={isFocused ? { selected: true } : {}}
            accessibilityLabel={options.tabBarAccessibilityLabel}
            testID={options.tabBarTestID}
            onPress={onPress}
            onLongPress={onLongPress}
            style={styles.tabButton}
          >
            <View style={[styles.tabContent, isFocused && styles.activeTab]}>
              <Icon
                name={iconName}
                size={24}
                color={isFocused ? theme.colors.primary : theme.colors.onSurfaceVariant}
              />
              <Text
                style={[
                  styles.tabLabel,
                  {
                    color: isFocused ? theme.colors.primary : theme.colors.onSurfaceVariant,
                  },
                ]}
              >
                {label}
              </Text>
            </View>
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: theme.colors.surface,
    borderTopWidth: 1,
    borderTopColor: theme.colors.outline,
    paddingBottom: 8,
    paddingTop: 8,
    paddingHorizontal: 4,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
  },
  tabContent: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 12,
    minWidth: 60,
  },
  activeTab: {
    backgroundColor: theme.colors.primaryContainer,
  },
  tabLabel: {
    fontSize: 12,
    fontWeight: '500',
    marginTop: 2,
  },
});

export default TabBar;
