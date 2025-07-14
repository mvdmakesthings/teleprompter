/**
 * Shared constants
 */

export const APP_NAME = 'CueBird'
export const APP_ID = 'com.cuebird.teleprompter'

// Default settings
export const DEFAULT_SETTINGS = {
  fontSize: 48,
  scrollSpeed: 1.0,
  voiceEnabled: false,
  voiceSensitivity: 1,
  voiceThreshold: -40,
  autoReload: true,
  autoSave: true,
  cursorAutoHide: true,
  progressBarEnabled: true,
  theme: 'dark' as const,
} as const

// Speed limits
export const SPEED_MIN = 0.05
export const SPEED_MAX = 5.0
export const SPEED_STEP = 0.05

// Font size limits
export const FONT_SIZE_MIN = 16
export const FONT_SIZE_MAX = 120
export const FONT_SIZE_STEP = 4

// Voice sensitivity levels
export const VOICE_SENSITIVITY_LEVELS = [0, 1, 2, 3] as const

// File extensions
export const SUPPORTED_EXTENSIONS = ['.md', '.markdown', '.txt'] as const

// WebSocket reconnect settings
export const WS_RECONNECT_DELAY = 1000
export const WS_MAX_RECONNECT_ATTEMPTS = 10

// Reading speed calculations
export const DEFAULT_WORDS_PER_MINUTE = 160
export const WORDS_PER_MINUTE_MIN = 50
export const WORDS_PER_MINUTE_MAX = 500