import { globalShortcut, BrowserWindow } from 'electron'
import { IpcChannels, ShortcutDefinition } from '@cuebird/ipc'

export class ShortcutManager {
  private static instance: ShortcutManager
  private shortcuts: Map<string, ShortcutDefinition> = new Map()
  private mainWindow: BrowserWindow | null = null

  private constructor() {}

  static getInstance(): ShortcutManager {
    if (!ShortcutManager.instance) {
      ShortcutManager.instance = new ShortcutManager()
    }
    return ShortcutManager.instance
  }

  setMainWindow(window: BrowserWindow) {
    this.mainWindow = window
  }

  /**
   * Register default shortcuts based on the PyQt6 implementation
   */
  registerDefaultShortcuts() {
    const defaultShortcuts: ShortcutDefinition[] = [
      // Playback controls
      { accelerator: 'Space', action: 'playPause', description: 'Toggle play/pause' },
      { accelerator: 'R', action: 'reset', description: 'Reset to beginning' },
      { accelerator: 'Escape', action: 'escape', description: 'Exit fullscreen or stop scrolling' },
      
      // Speed controls
      { accelerator: 'Plus', action: 'increaseSpeed', description: 'Increase speed' },
      { accelerator: '=', action: 'increaseSpeed', description: 'Increase speed' },
      { accelerator: '-', action: 'decreaseSpeed', description: 'Decrease speed' },
      { accelerator: 'Up', action: 'increaseSpeed', description: 'Increase speed' },
      { accelerator: 'Down', action: 'decreaseSpeed', description: 'Decrease speed' },
      
      // Navigation
      { accelerator: 'Right', action: 'nextSection', description: 'Go to next section' },
      { accelerator: 'Left', action: 'previousSection', description: 'Go to previous section' },
      { accelerator: 'PageUp', action: 'previousSection', description: 'Go to previous section' },
      { accelerator: 'PageDown', action: 'nextSection', description: 'Go to next section' },
      
      // Feature toggles
      { accelerator: 'V', action: 'toggleVoiceControl', description: 'Toggle voice control' },
      { accelerator: 'C', action: 'toggleCursor', description: 'Toggle cursor visibility' },
      
      // Global shortcuts (work even when window is not focused)
      { accelerator: 'CommandOrControl+Space', action: 'playPause', description: 'Toggle play/pause (global)', isGlobal: true },
      { accelerator: 'CommandOrControl+R', action: 'reset', description: 'Reset to beginning (global)', isGlobal: true },
    ]

    defaultShortcuts.forEach(shortcut => this.register(shortcut))
  }

  /**
   * Register a keyboard shortcut
   */
  register(shortcut: ShortcutDefinition): boolean {
    try {
      const { accelerator, action, isGlobal } = shortcut
      
      if (isGlobal) {
        // Register global shortcut
        const success = globalShortcut.register(accelerator, () => {
          this.triggerAction(action)
        })
        
        if (success) {
          this.shortcuts.set(accelerator, shortcut)
        }
        
        return success
      } else {
        // Store local shortcut (will be handled by renderer process)
        this.shortcuts.set(accelerator, shortcut)
        return true
      }
    } catch (error) {
      console.error(`Failed to register shortcut ${shortcut.accelerator}:`, error)
      return false
    }
  }

  /**
   * Unregister a keyboard shortcut
   */
  unregister(accelerator: string): boolean {
    const shortcut = this.shortcuts.get(accelerator)
    if (!shortcut) return false

    if (shortcut.isGlobal) {
      globalShortcut.unregister(accelerator)
    }

    this.shortcuts.delete(accelerator)
    return true
  }

  /**
   * Unregister all shortcuts
   */
  unregisterAll() {
    // Unregister all global shortcuts
    globalShortcut.unregisterAll()
    this.shortcuts.clear()
  }

  /**
   * Get all registered shortcuts
   */
  getAll(): ShortcutDefinition[] {
    return Array.from(this.shortcuts.values())
  }

  /**
   * Get local shortcuts (non-global)
   */
  getLocalShortcuts(): ShortcutDefinition[] {
    return Array.from(this.shortcuts.values()).filter(s => !s.isGlobal)
  }

  /**
   * Trigger an action
   */
  private triggerAction(action: string) {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send(IpcChannels.SHORTCUTS_TRIGGERED, { action })
    }
  }

  /**
   * Check if a shortcut is registered
   */
  isRegistered(accelerator: string): boolean {
    return this.shortcuts.has(accelerator) || globalShortcut.isRegistered(accelerator)
  }
}