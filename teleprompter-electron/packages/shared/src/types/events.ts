/**
 * WebSocket event types for real-time communication
 */

import { ContentInfo, FileInfo, ScrollState, VoiceActivity } from './domain'

export type WebSocketEvent =
  | FileChangeEvent
  | VoiceActivityEvent
  | ScrollUpdateEvent
  | ContentUpdateEvent
  | ErrorEvent

export interface FileChangeEvent {
  type: 'file:changed'
  data: {
    filePath: string
    changeType: 'modified' | 'deleted' | 'created'
    timestamp: Date
  }
}

export interface VoiceActivityEvent {
  type: 'voice:activity'
  data: VoiceActivity
}

export interface ScrollUpdateEvent {
  type: 'scroll:update'
  data: ScrollState
}

export interface ContentUpdateEvent {
  type: 'content:update'
  data: {
    contentInfo: ContentInfo
    fileInfo?: FileInfo
  }
}

export interface ErrorEvent {
  type: 'error'
  data: {
    code: string
    message: string
    details?: any
  }
}