import { BrowserWindow, screen, shell } from 'electron'
import * as path from 'path'
import { WindowState } from '@cuebird/ipc'

export class WindowManager {
  private static instance: WindowManager
  private mainWindow: BrowserWindow | null = null
  private windowState: WindowState | null = null

  private constructor() {}

  static getInstance(): WindowManager {
    if (!WindowManager.instance) {
      WindowManager.instance = new WindowManager()
    }
    return WindowManager.instance
  }

  createMainWindow(): BrowserWindow {
    // Get primary display dimensions
    const primaryDisplay = screen.getPrimaryDisplay()
    const { width, height } = primaryDisplay.workAreaSize

    // Create the browser window
    this.mainWindow = new BrowserWindow({
      width: Math.min(1200, width * 0.8),
      height: Math.min(800, height * 0.8),
      minWidth: 800,
      minHeight: 600,
      center: true,
      title: 'CueBird Teleprompter',
      icon: this.getIconPath(),
      webPreferences: {
        preload: path.join(__dirname, '../preload/index.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: true
      },
      backgroundColor: '#000000',
      show: false, // Don't show until ready
      frame: process.platform === 'darwin', // Native frame on macOS
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    })

    // Show window when ready
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show()
    })

    // Handle window events
    this.setupWindowEvents()

    return this.mainWindow
  }

  private setupWindowEvents() {
    if (!this.mainWindow) return

    // Update window state
    this.mainWindow.on('maximize', () => this.updateWindowState())
    this.mainWindow.on('unmaximize', () => this.updateWindowState())
    this.mainWindow.on('minimize', () => this.updateWindowState())
    this.mainWindow.on('restore', () => this.updateWindowState())
    this.mainWindow.on('enter-full-screen', () => this.updateWindowState())
    this.mainWindow.on('leave-full-screen', () => this.updateWindowState())
    this.mainWindow.on('move', () => this.updateWindowState())
    this.mainWindow.on('resize', () => this.updateWindowState())

    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url)
      return { action: 'deny' }
    })

    // Prevent navigation away from app
    this.mainWindow.webContents.on('will-navigate', (event, url) => {
      if (!url.startsWith('file://') && !url.startsWith('http://localhost')) {
        event.preventDefault()
        shell.openExternal(url)
      }
    })

    // Clean up on close
    this.mainWindow.on('closed', () => {
      this.mainWindow = null
      this.windowState = null
    })
  }

  private updateWindowState() {
    if (!this.mainWindow) return

    const bounds = this.mainWindow.getBounds()
    this.windowState = {
      isMaximized: this.mainWindow.isMaximized(),
      isMinimized: this.mainWindow.isMinimized(),
      isFullScreen: this.mainWindow.isFullScreen(),
      bounds
    }
  }

  private getIconPath(): string {
    if (process.platform === 'darwin') {
      return path.join(__dirname, '../../assets/icon.icns')
    } else if (process.platform === 'win32') {
      return path.join(__dirname, '../../assets/icon.ico')
    } else {
      return path.join(__dirname, '../../assets/icon.png')
    }
  }

  getMainWindow(): BrowserWindow | null {
    return this.mainWindow
  }

  getWindowState(): WindowState | null {
    return this.windowState
  }

  minimizeWindow() {
    this.mainWindow?.minimize()
  }

  maximizeWindow() {
    if (this.mainWindow?.isMaximized()) {
      this.mainWindow.unmaximize()
    } else {
      this.mainWindow?.maximize()
    }
  }

  closeWindow() {
    this.mainWindow?.close()
  }

  toggleFullscreen() {
    const isFullScreen = this.mainWindow?.isFullScreen()
    this.mainWindow?.setFullScreen(!isFullScreen)
  }
}