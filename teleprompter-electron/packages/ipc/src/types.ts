/**
 * IPC message types
 */

import { Settings } from '@cuebird/shared'

// Backend status
export interface BackendStatus {
  running: boolean
  port?: number
  pid?: number
  error?: string
}

// File dialog result
export interface FileDialogResult {
  canceled: boolean
  filePath?: string
}

// Window state
export interface WindowState {
  isMaximized: boolean
  isMinimized: boolean
  isFullScreen: boolean
  bounds: {
    x: number
    y: number
    width: number
    height: number
  }
}

// IPC API exposed to renderer
export interface IpcApi {
  // Window management
  minimizeWindow: () => Promise<void>
  maximizeWindow: () => Promise<void>
  closeWindow: () => Promise<void>
  toggleFullscreen: () => Promise<void>
  
  // Backend management
  getBackendStatus: () => Promise<BackendStatus>
  getBackendUrl: () => Promise<string>
  
  // File operations
  showOpenDialog: (options: {
    properties?: string[]
    filters?: { name: string; extensions: string[] }[]
  }) => Promise<{ canceled: boolean; filePaths: string[] }>
  
  // Settings
  getSettings: () => Promise<Settings>
  setSettings: (settings: Partial<Settings>) => Promise<void>
  
  // Event listeners
  onBackendError: (callback: (error: string) => void) => () => void
  onFileDropped: (callback: (filePath: string) => void) => () => void
  onSettingsChanged: (callback: (settings: Settings) => void) => () => void
}