import { app, BrowserWindow, ipcMain, dialog, session } from 'electron'
import * as path from 'path'
import { IpcChannels } from '@cuebird/ipc'
import { WindowManager } from './windowManager'
import { PythonManager } from './pythonManager'
//import { SettingsManager } from './settingsManager'
import { IpcHandlers } from './ipcHandlers'
import { ShortcutManager } from './shortcutManager'

// Handle creating/removing shortcuts on Windows when installing/uninstalling
// @ts-ignore - electron-squirrel-startup might not be installed in dev
if (process.platform === 'win32') {
  try {
    if (require('electron-squirrel-startup')) {
      app.quit()
    }
  } catch (e) {
    // Ignore in development
  }
}

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock()
if (!gotTheLock) {
  app.quit()
} else {
  app.on('second-instance', () => {
    // Someone tried to run a second instance, focus our window instead
    const mainWindow = WindowManager.getInstance().getMainWindow()
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  })
}

// Initialize managers
const windowManager = WindowManager.getInstance()
const pythonManager = PythonManager.getInstance()
//const settingsManager = SettingsManager.getInstance()
const shortcutManager = ShortcutManager.getInstance()

// Main app initialization
async function createApp() {
  try {
    // Start Python backend
    await pythonManager.start()

    // Create main window
    const mainWindow = windowManager.createMainWindow()

    // Initialize shortcut manager with main window
    shortcutManager.setMainWindow(mainWindow)
    shortcutManager.registerDefaultShortcuts()

    // Initialize IPC handlers
    //IpcHandlers.initialize(windowManager, pythonManager, shortcutManager)

    // Load frontend
    if (app.isPackaged) {
      // Production: Load from static files
      const frontendPath = path.join(process.resourcesPath, 'frontend', 'index.html')
      await mainWindow.loadFile(frontendPath)
    } else {
      // Development: Load from Next.js dev server
      await mainWindow.loadURL('http://localhost:3001')
      mainWindow.webContents.openDevTools()

      // Suppress harmless DevTools console errors
      mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
        // Filter out known harmless DevTools errors
        if (message.includes('Autofill.enable failed') ||
          message.includes('Autofill.setAddresses failed') ||
          message.includes('Request Autofill') ||
          message.includes("wasn't found")) {
          return // Suppress these specific errors
        }
        // Log other console messages normally
        console.log(`[Renderer ${level}]:`, message)
      })
    }

    // Notify renderer that app is ready
    mainWindow.webContents.on('did-finish-load', () => {
      mainWindow.webContents.send(IpcChannels.APP_READY, {
        backendUrl: pythonManager.getApiUrl(),
        settings: {} // settingsManager.getAll()
      })
    })

  } catch (error) {
    console.error('Failed to initialize app:', error)
    dialog.showErrorBox('Initialization Error',
      `Failed to start CueBird: ${(error as Error).message}`)
    app.quit()
  }
}

// Configure Content Security Policy for enhanced security
app.whenReady().then(() => {
  // Set up CSP headers for localhost development
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    // Only apply CSP to localhost development server
    if (details.url.startsWith('http://localhost:3001')) {
      callback({
        responseHeaders: {
          ...details.responseHeaders,
          'Content-Security-Policy': [
            // More restrictive CSP for production-like security in development
            "default-src 'self' http://localhost:* ws://localhost:* wss://localhost:*; " +
            "script-src 'self' 'unsafe-inline' http://localhost:* blob:; " +
            "style-src 'self' 'unsafe-inline' http://localhost:*; " +
            "img-src 'self' data: blob: http://localhost:*; " +
            "font-src 'self' data: http://localhost:*; " +
            "connect-src 'self' http://localhost:* ws://localhost:* wss://localhost:*; " +
            "media-src 'self' blob: data:; " +
            "object-src 'none'; " +
            "base-uri 'self'"
          ]
        }
      })
    } else {
      callback({ responseHeaders: details.responseHeaders })
    }
  })
})

// App event handlers
app.whenReady().then(async () => {
  // Handle microphone permissions
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    if (permission === 'media') {
      // Always grant microphone access for the app
      callback(true)
    } else {
      callback(false)
    }
  })

  // Set permission check handler for better UX
  session.defaultSession.setPermissionCheckHandler((webContents, permission, requestingOrigin) => {
    if (permission === 'media') {
      return true
    }
    return false
  })

  await createApp()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createApp()
  }
})

app.on('before-quit', async () => {
  // Clean shutdown
  shortcutManager.unregisterAll()
  await pythonManager.stop()
})

// Handle unhandled errors
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error)
  dialog.showErrorBox('Unexpected Error', error.message)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason)
})