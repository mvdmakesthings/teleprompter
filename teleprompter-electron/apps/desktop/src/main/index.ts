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