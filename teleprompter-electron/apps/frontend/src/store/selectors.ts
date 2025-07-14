import { useTeleprompterStore } from './teleprompter'
import { useSettingsStore } from './settings'

// Teleprompter selectors
export const useIsPlaying = () => useTeleprompterStore(state => state.isPlaying)
export const useContent = () => useTeleprompterStore(state => state.content)
export const useCurrentFile = () => useTeleprompterStore(state => state.currentFile)
export const useProgress = () => useTeleprompterStore(state => state.progress())
export const useRemainingTime = () => useTeleprompterStore(state => state.remainingTime())
export const useCurrentSection = () => useTeleprompterStore(state => state.currentSection())
export const useCanScroll = () => useTeleprompterStore(state => state.canScroll())
export const useIsAtEnd = () => useTeleprompterStore(state => state.isAtEnd())

// Combined selectors for complex state
export const usePlaybackState = () => useTeleprompterStore(state => ({
  isPlaying: state.isPlaying,
  scrollSpeed: state.scrollSpeed,
  scrollPosition: state.scrollPosition,
  progress: state.progress(),
  isAtEnd: state.isAtEnd(),
}))

export const useContentInfo = () => useTeleprompterStore(state => ({
  content: state.content,
  wordCount: state.wordCount,
  sections: state.sections,
  currentSection: state.currentSection(),
}))

export const useDisplaySettings = () => useTeleprompterStore(state => ({
  fontSize: state.fontSize,
  contentHeight: state.contentHeight,
  viewportHeight: state.viewportHeight,
}))

// Settings selectors
export const useVoiceSettings = () => useSettingsStore(state => ({
  voiceEnabled: state.voiceEnabled,
  voiceSensitivity: state.voiceSensitivity,
  voiceThreshold: state.voiceThreshold,
}))

export const useTheme = () => useSettingsStore(state => ({
  theme: state.theme,
  isDarkMode: state.isDarkMode,
}))

// Voice activity from teleprompter store
export const useVoiceActivity = () => useTeleprompterStore(state => ({
  isVoiceActive: state.isVoiceActive,
  voiceEnabled: state.voiceEnabled,
}))