import Store from 'electron-store'
import { Settings, DEFAULT_SETTINGS } from '@cuebird/shared'

export class SettingsManager {
  private static instance: SettingsManager
  private store: Store<Settings>

  private constructor() {
    this.store = new Store<Settings>({
      name: 'cuebird-settings',
      defaults: DEFAULT_SETTINGS,
      schema: {
        fontSize: {
          type: 'number',
          minimum: 16,
          maximum: 120
        },
        scrollSpeed: {
          type: 'number',
          minimum: 0.05,
          maximum: 5.0
        },
        voiceEnabled: {
          type: 'boolean'
        },
        voiceSensitivity: {
          type: 'number',
          minimum: 0,
          maximum: 3
        },
        autoReload: {
          type: 'boolean'
        },
        cursorAutoHide: {
          type: 'boolean'
        },
        progressBarEnabled: {
          type: 'boolean'
        }
      }
    })
  }

  static getInstance(): SettingsManager {
    if (!SettingsManager.instance) {
      SettingsManager.instance = new SettingsManager()
    }
    return SettingsManager.instance
  }

  get<K extends keyof Settings>(key: K): Settings[K] {
    return this.store.get(key)
  }

  set<K extends keyof Settings>(key: K, value: Settings[K]): void {
    this.store.set(key, value)
  }

  getAll(): Settings {
    return this.store.store
  }

  setAll(settings: Partial<Settings>): void {
    Object.entries(settings).forEach(([key, value]) => {
      if (value !== undefined) {
        this.store.set(key as keyof Settings, value)
      }
    })
  }

  reset(): void {
    this.store.clear()
  }

  onDidChange<K extends keyof Settings>(
    key: K,
    callback: (newValue: Settings[K], oldValue: Settings[K]) => void
  ): () => void {
    return this.store.onDidChange(key, callback)
  }

  onDidAnyChange(callback: (newValue: Settings, oldValue: Settings) => void): () => void {
    return this.store.onDidAnyChange(callback)
  }
}