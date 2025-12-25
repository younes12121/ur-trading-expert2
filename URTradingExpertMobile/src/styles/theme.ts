import { MD3LightTheme, MD3DarkTheme, configureFonts } from 'react-native-paper';

// Professional Trading Theme - Dark Mode with Cyan Accents
const fontConfig = {
  displayLarge: {
    fontFamily: 'System',
    fontSize: 57,
    fontWeight: '400',
    lineHeight: 64,
    letterSpacing: 0,
  },
  displayMedium: {
    fontFamily: 'System',
    fontSize: 45,
    fontWeight: '400',
    lineHeight: 52,
    letterSpacing: 0,
  },
  displaySmall: {
    fontFamily: 'System',
    fontSize: 36,
    fontWeight: '400',
    lineHeight: 44,
    letterSpacing: 0,
  },
  headlineLarge: {
    fontFamily: 'System',
    fontSize: 32,
    fontWeight: '400',
    lineHeight: 40,
    letterSpacing: 0,
  },
  headlineMedium: {
    fontFamily: 'System',
    fontSize: 28,
    fontWeight: '400',
    lineHeight: 36,
    letterSpacing: 0,
  },
  headlineSmall: {
    fontFamily: 'System',
    fontSize: 24,
    fontWeight: '400',
    lineHeight: 32,
    letterSpacing: 0,
  },
  titleLarge: {
    fontFamily: 'System',
    fontSize: 22,
    fontWeight: '500',
    lineHeight: 28,
    letterSpacing: 0,
  },
  titleMedium: {
    fontFamily: 'System',
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 24,
    letterSpacing: 0.15,
  },
  titleSmall: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '500',
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  labelLarge: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '500',
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  labelMedium: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    lineHeight: 16,
    letterSpacing: 0.5,
  },
  labelSmall: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    lineHeight: 16,
    letterSpacing: 0.5,
  },
  bodyLarge: {
    fontFamily: 'System',
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
    letterSpacing: 0.15,
  },
  bodyMedium: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
    letterSpacing: 0.25,
  },
  bodySmall: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 16,
    letterSpacing: 0.4,
  },
};

export const theme = {
  ...MD3DarkTheme,
  colors: {
    // Primary Colors - Professional Cyan/Teal
    primary: '#00D9FF',
    onPrimary: '#000000',
    primaryContainer: '#004D5A',
    onPrimaryContainer: '#B8EAFF',

    // Secondary Colors
    secondary: '#B8EAFF',
    onSecondary: '#001F28',
    secondaryContainer: '#004D5A',
    onSecondaryContainer: '#B8EAFF',

    // Tertiary Colors
    tertiary: '#8BCEFF',
    onTertiary: '#001F2A',
    tertiaryContainer: '#004D5A',
    onTertiaryContainer: '#B8EAFF',

    // Error Colors
    error: '#FFB4AB',
    onError: '#690005',
    errorContainer: '#93000A',
    onErrorContainer: '#FFDAD6',

    // Status Colors
    success: '#34D399',
    onSuccess: '#003912',
    warning: '#FBBF24',
    onWarning: '#4D2A00',
    info: '#60A5FA',
    onInfo: '#001B3D',

    // Surface Colors - Dark Theme
    background: '#0F172A',
    onBackground: '#E2E8F0',
    surface: '#1E293B',
    onSurface: '#F1F5F9',
    surfaceVariant: '#334155',
    onSurfaceVariant: '#CBD5E1',
    surfaceDisabled: '#475569',
    onSurfaceDisabled: '#94A3B8',

    // Outline Colors
    outline: '#64748B',
    outlineVariant: '#475569',

    // Elevation Colors
    elevation: {
      level0: 'transparent',
      level1: '#1E293B',
      level2: '#25303D',
      level3: '#2A3441',
      level4: '#2E3846',
      level5: '#333F4F',
    },

    // Custom Trading Colors
    buy: '#34D399',
    sell: '#F87171',
    hold: '#FBBF24',
    profit: '#34D399',
    loss: '#F87171',
    neutral: '#64748B',

    // Market Category Colors
    asian: '#F59E0B',
    major: '#3B82F6',
    emerging: '#F97316',
    crypto: '#8B5CF6',

    // Risk Level Colors
    lowRisk: '#34D399',
    mediumRisk: '#FBBF24',
    highRisk: '#F87171',
  },
  fonts: configureFonts({ config: fontConfig }),
};

// Light theme for future use
export const lightTheme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#006684',
    secondary: '#4D6268',
    background: '#FBFCFE',
    surface: '#FBFCFE',
    onSurface: '#1A1C1E',
  },
  fonts: configureFonts({ config: fontConfig }),
};

// Spacing system
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
};

// Border radius system
export const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  xxl: 24,
  full: 9999,
};

// Shadow system
export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.30,
    shadowRadius: 4.65,
    elevation: 8,
  },
  xl: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.44,
    shadowRadius: 10.32,
    elevation: 16,
  },
};

// Animation durations
export const animations = {
  fast: 200,
  normal: 300,
  slow: 500,
};

// Typography scale
export const typography = {
  h1: {
    fontSize: 32,
    fontWeight: 'bold' as const,
    lineHeight: 40,
  },
  h2: {
    fontSize: 28,
    fontWeight: 'bold' as const,
    lineHeight: 36,
  },
  h3: {
    fontSize: 24,
    fontWeight: '600' as const,
    lineHeight: 32,
  },
  h4: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 28,
  },
  body1: {
    fontSize: 16,
    fontWeight: 'normal' as const,
    lineHeight: 24,
  },
  body2: {
    fontSize: 14,
    fontWeight: 'normal' as const,
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: 'normal' as const,
    lineHeight: 16,
  },
  button: {
    fontSize: 14,
    fontWeight: '600' as const,
    lineHeight: 20,
  },
};
