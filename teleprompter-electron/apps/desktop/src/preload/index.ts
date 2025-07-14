import { contextBridge, ipcRenderer } from 'electron'
import { IpcChannels, IpcApi } from '@cuebird/ipc'

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
const electronAPI: IpcApi = {
  // Window management
  minimizeWindow: () => ipcRenderer.invoke(IpcChannels.WINDOW_MINIMIZE),
  maximizeWindow: () => ipcRenderer.invoke(IpcChannels.WINDOW_MAXIMIZE),
  closeWindow: () => ipcRenderer.invoke(IpcChannels.WINDOW_CLOSE),
  toggleFullscreen: () => ipcRenderer.invoke(IpcChannels.WINDOW_FULLSCREEN),

  // Backend management
  getBackendStatus: () => ipcRenderer.invoke(IpcChannels.BACKEND_STATUS),
  getBackendUrl: () => ipcRenderer.invoke(IpcChannels.BACKEND_PORT),

  // File operations
  openFileDialog: () => ipcRenderer.invoke(IpcChannels.FILE_OPEN_DIALOG),

  // Settings
  getSettings: () => ipcRenderer.invoke(IpcChannels.SETTINGS_GET),
  setSettings: (settings) => ipcRenderer.invoke(IpcChannels.SETTINGS_SET, settings),

  // Event listeners with cleanup
  onBackendError: (callback) => {
    const subscription = (_event: any, error: string) => callback(error)
    ipcRenderer.on(IpcChannels.BACKEND_ERROR, subscription)
    return () => {
      ipcRenderer.removeListener(IpcChannels.BACKEND_ERROR, subscription)
    }
  },

  onFileDropped: (callback) => {
    const subscription = (_event: any, filePath: string) => callback(filePath)
    ipcRenderer.on(IpcChannels.FILE_DROPPED, subscription)
    return () => {
      ipcRenderer.removeListener(IpcChannels.FILE_DROPPED, subscription)
    }
  },

  onSettingsChanged: (callback) => {
    const subscription = (_event: any, settings: any) => callback(settings)
    ipcRenderer.on(IpcChannels.SETTINGS_CHANGED, subscription)
    return () => {
      ipcRenderer.removeListener(IpcChannels.SETTINGS_CHANGED, subscription)
    }
  },

  // Keyboard shortcuts
  getShortcuts: () => ipcRenderer.invoke(IpcChannels.SHORTCUTS_GET_ALL),
  registerShortcut: (shortcut) => ipcRenderer.invoke(IpcChannels.SHORTCUTS_REGISTER, shortcut),
  unregisterShortcut: (accelerator) => ipcRenderer.invoke(IpcChannels.SHORTCUTS_UNREGISTER, accelerator),

  onShortcutTriggered: (callback) => {
    const subscription = (_event: any, data: { action: string }) => callback(data)
    ipcRenderer.on(IpcChannels.SHORTCUTS_TRIGGERED, subscription)
    return () => {
      ipcRenderer.removeListener(IpcChannels.SHORTCUTS_TRIGGERED, subscription)
    }
  }
}

// Expose the API to the renderer process
contextBridge.exposeInMainWorld('electronAPI', electronAPI)

// Handle file drop events
window.addEventListener('dragover', (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
})

window.addEventListener('drop', (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()

  const files = Array.from(e.dataTransfer?.files || [])
  if (files.length > 0) {
    // Send the first file path to main process
    ipcRenderer.send(IpcChannels.FILE_DROPPED, (files[0] as any).path)
  }
})

// Listen for app ready event
ipcRenderer.once(IpcChannels.APP_READY, (_event, data) => {
  // Store backend URL and initial settings in window object
  // This will be available when the renderer loads
  ; (window as any).__CUEBIRD_INIT__ = data
})