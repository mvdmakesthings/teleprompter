import { ipcMain, dialog, BrowserWindow } from 'electron'
import { IpcChannels, FileDialogResult } from '@cuebird/ipc'
import { WindowManager } from './windowManager'
import { PythonManager } from './pythonManager'
//import { SettingsManager } from './settingsManager'
import { ShortcutManager } from './shortcutManager'
import { SUPPORTED_EXTENSIONS } from '@cuebird/shared'

export class IpcHandlers {
  static initialize(
    windowManager: WindowManager,
    pythonManager: PythonManager,
    //settingsManager: SettingsManager,
    shortcutManager: ShortcutManager
  ) {
    // Window management handlers
    ipcMain.handle(IpcChannels.WINDOW_MINIMIZE, () => {
      windowManager.minimizeWindow()
    })

    ipcMain.handle(IpcChannels.WINDOW_MAXIMIZE, () => {
      windowManager.maximizeWindow()
    })

    ipcMain.handle(IpcChannels.WINDOW_CLOSE, () => {
      windowManager.closeWindow()
    })

    ipcMain.handle(IpcChannels.WINDOW_FULLSCREEN, () => {
      windowManager.toggleFullscreen()
    })

    // Backend status handlers
    ipcMain.handle(IpcChannels.BACKEND_STATUS, () => {
      return pythonManager.getStatus()
    })

    ipcMain.handle(IpcChannels.BACKEND_PORT, () => {
      return pythonManager.getApiUrl()
    })

    // File dialog handler
    ipcMain.handle(IpcChannels.FILE_OPEN_DIALOG, async (): Promise<FileDialogResult> => {
      const mainWindow = windowManager.getMainWindow()
      if (!mainWindow) {
        return { canceled: true }
      }

      const result = await dialog.showOpenDialog(mainWindow, {
        title: 'Open Teleprompter File',
        filters: [
          {
            name: 'Supported Files',
            extensions: SUPPORTED_EXTENSIONS.map(ext => ext.substring(1))
          },
          { name: 'Markdown', extensions: ['md', 'markdown'] },
          { name: 'Text', extensions: ['txt'] },
          { name: 'All Files', extensions: ['*'] }
        ],
        properties: ['openFile']
      })

      if (result.canceled || !result.filePaths.length) {
        return { canceled: true }
      }

      return {
        canceled: false,
        filePath: result.filePaths[0]
      }
    })

    // Settings handlers - temporarily disabled
    /*ipcMain.handle(IpcChannels.SETTINGS_GET, () => {
      return settingsManager.getAll()
    })

    ipcMain.handle(IpcChannels.SETTINGS_SET, (_, settings) => {
      settingsManager.setAll(settings)
    })*/

    // Dev tools toggle
    ipcMain.handle(IpcChannels.DEV_TOOLS_TOGGLE, () => {
      const mainWindow = windowManager.getMainWindow()
      if (mainWindow) {
        if (mainWindow.webContents.isDevToolsOpened()) {
          mainWindow.webContents.closeDevTools()
        } else {
          mainWindow.webContents.openDevTools()
        }
      }
    })

    // Keyboard shortcut handlers
    ipcMain.handle(IpcChannels.SHORTCUTS_GET_ALL, () => {
      return shortcutManager.getLocalShortcuts()
    })

    ipcMain.handle(IpcChannels.SHORTCUTS_REGISTER, (_, shortcut) => {
      return shortcutManager.register(shortcut)
    })

    ipcMain.handle(IpcChannels.SHORTCUTS_UNREGISTER, (_, accelerator) => {
      return shortcutManager.unregister(accelerator)
    })

    // Settings change listener - temporarily disabled
    /*settingsManager.onDidAnyChange((newSettings) => {
      const mainWindow = windowManager.getMainWindow()
      if (mainWindow) {
        mainWindow.webContents.send(IpcChannels.SETTINGS_CHANGED, newSettings)
      }
    })*/

    // Backend error forwarding
    const checkBackendStatus = setInterval(() => {
      const status = pythonManager.getStatus()
      if (!status.running && status.error) {
        const mainWindow = windowManager.getMainWindow()
        if (mainWindow) {
          mainWindow.webContents.send(IpcChannels.BACKEND_ERROR, status.error)
        }
      }
    }, 1000)

    // Cleanup on app quit
    ipcMain.once('before-quit', () => {
      clearInterval(checkBackendStatus)
    })
  }
}