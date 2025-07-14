import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { Settings } from '@cuebird/shared'

interface SettingsState extends Settings {
  // Actions
  updateSettings: (settings: Partial<Settings>) => Promise<void>
  resetToDefaults: () => void
  
  // Theme
  isDarkMode: boolean
  toggleDarkMode: () => void
}

const defaultSettings: Settings = {
  scrollSpeed: 1.0,
  fontSize: 48,
  voiceEnabled: false,
  voiceSensitivity: 1,
  voiceThreshold: -40,
  autoReload: true,
  autoSave: true,
  cursorAutoHide: true,
  progressBarEnabled: true,
  theme: 'dark',
}

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set, get) => ({
        ...defaultSettings,
        isDarkMode: true,
        
        updateSettings: async (newSettings) => {
          // Store previous state for rollback
          const previousState = get()
          
          // Optimistically update
          set(newSettings)
          
          // Sync with Electron if available
          if (window.electronAPI) {
            try {
              await window.electronAPI.setSettings(newSettings)
            } catch (error) {
              console.error('Failed to sync settings with Electron:', error)
              // Rollback on failure
              set(previousState)
              throw error // Re-throw so UI can handle it
            }
          }
        },
        
        resetToDefaults: () => {
          set({
            ...defaultSettings,
            isDarkMode: defaultSettings.theme === 'dark'
          })
        },
        
        toggleDarkMode: () => {
          const isDarkMode = !get().isDarkMode
          set({ 
            isDarkMode,
            theme: isDarkMode ? 'dark' : 'light'
          })
        },
      }),
      {
        name: 'teleprompter-settings',
        partialize: (state) => {
          // Only persist settings, not actions
          const { updateSettings, resetToDefaults, toggleDarkMode, ...settings } = state
          return settings
        },
      }
    ),
    {
      name: 'settings-store',
    }
  )
)