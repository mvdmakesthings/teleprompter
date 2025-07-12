/**
 * IPC channel names for communication between main and renderer processes
 */

export const IpcChannels = {
  // Window management
  WINDOW_MINIMIZE: 'window:minimize',
  WINDOW_MAXIMIZE: 'window:maximize',
  WINDOW_CLOSE: 'window:close',
  WINDOW_FULLSCREEN: 'window:fullscreen',
  
  // Python backend
  BACKEND_START: 'backend:start',
  BACKEND_STOP: 'backend:stop',
  BACKEND_STATUS: 'backend:status',
  BACKEND_PORT: 'backend:port',
  BACKEND_ERROR: 'backend:error',
  
  // File operations
  FILE_OPEN_DIALOG: 'file:open-dialog',
  FILE_SELECTED: 'file:selected',
  FILE_DROPPED: 'file:dropped',
  
  // Settings
  SETTINGS_GET: 'settings:get',
  SETTINGS_SET: 'settings:set',
  SETTINGS_CHANGED: 'settings:changed',
  
  // App lifecycle
  APP_READY: 'app:ready',
  APP_ERROR: 'app:error',
  APP_QUIT: 'app:quit',
  
  // Dev tools
  DEV_TOOLS_TOGGLE: 'dev:tools-toggle',
} as const

export type IpcChannel = typeof IpcChannels[keyof typeof IpcChannels]