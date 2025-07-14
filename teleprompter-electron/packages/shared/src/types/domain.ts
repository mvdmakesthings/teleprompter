/**
 * Domain types shared between frontend and backend
 */

export interface ScrollState {
  position: number
  speed: number
  isPlaying: boolean
  progress: number
}

export interface VoiceActivity {
  state: 'inactive' | 'listening' | 'active' | 'error'
  isSpeaking: boolean
  audioLevel: number
  sensitivity: number
  timestamp: Date
}

export interface ContentInfo {
  title: string
  wordCount: number
  sections: string[]
  estimatedReadingTime: number
  currentSection?: string
}

export interface FileInfo {
  path: string
  name: string
  size: number
  lastModified: Date
}

export interface ReadingMetrics {
  wordsPerMinute: number
  elapsedTime: number
  remainingTime: number
  totalTime: number
}

export interface Settings {
  fontSize: number
  scrollSpeed: number
  voiceEnabled: boolean
  voiceSensitivity: number
  voiceThreshold: number
  autoReload: boolean
  autoSave: boolean
  cursorAutoHide: boolean
  progressBarEnabled: boolean
  theme: 'light' | 'dark'
}