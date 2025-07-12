/**
 * API request and response types
 */

import { ContentInfo, FileInfo, ReadingMetrics, ScrollState, Settings, VoiceActivity } from './domain'

// API Endpoints
export interface ApiEndpoints {
  content: {
    load: '/api/content/load'
    parse: '/api/content/parse'
    analyze: '/api/content/analyze'
  }
  reading: {
    metrics: '/api/reading/metrics'
    control: '/api/reading/control'
  }
  voice: {
    detect: '/api/voice/detect'
    config: '/api/voice/config'
  }
  settings: '/api/settings'
}

// Request types
export interface LoadContentRequest {
  filePath: string
}

export interface ParseContentRequest {
  content: string
  format: 'markdown' | 'plain'
}

export interface UpdateScrollRequest {
  position?: number
  speed?: number
  isPlaying?: boolean
}

export interface UpdateVoiceConfigRequest {
  enabled?: boolean
  sensitivity?: number
}

// Response types
export interface LoadContentResponse {
  html: string
  markdown: string
  contentInfo: ContentInfo
  fileInfo: FileInfo
}

export interface ParseContentResponse {
  html: string
  contentInfo: ContentInfo
}

export interface AnalyzeContentResponse {
  contentInfo: ContentInfo
}

export interface ReadingMetricsResponse {
  metrics: ReadingMetrics
  scrollState: ScrollState
}

export interface VoiceStatusResponse {
  activity: VoiceActivity
}

export interface SettingsResponse {
  settings: Settings
}

// Error response
export interface ApiError {
  error: string
  code: string
  details?: any
}