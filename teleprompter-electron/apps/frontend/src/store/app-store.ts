import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Settings, DEFAULT_SETTINGS } from '@cuebird/shared'
import { apiClient } from '@/lib/api-client'

interface AppState {
  // Connection state
  backendUrl: string
  isConnected: boolean
  connectionError: string | null
  
  // Settings
  settings: Settings
  
  // Actions
  initialize: (backendUrl: string, settings: Settings) => Promise<void>
  updateSettings: (settings: Partial<Settings>) => Promise<void>
  checkConnection: () => Promise<void>
}

export const useAppStore = create<AppState>()(
  devtools(
    (set, get) => ({
      // Initial state
      backendUrl: '',
      isConnected: false,
      connectionError: null,
      settings: DEFAULT_SETTINGS,

      // Initialize app with backend URL and settings
      initialize: async (backendUrl: string, settings: Settings) => {
        apiClient.setBaseUrl(backendUrl)
        
        set({
          backendUrl,
          settings,
          isConnected: false,
          connectionError: null,
        })

        // Check connection
        await get().checkConnection()
      },

      // Update settings
      updateSettings: async (newSettings: Partial<Settings>) => {
        const { settings } = get()
        const updatedSettings = { ...settings, ...newSettings }
        
        try {
          // Update backend
          await apiClient.updateSettings(newSettings)
          
          // Update local state
          set({ settings: updatedSettings })
          
          // Update Electron store if available
          if (window.electronAPI) {
            await window.electronAPI.setSettings(newSettings)
          }
        } catch (error) {
          console.error('Failed to update settings:', error)
          throw error
        }
      },

      // Check backend connection
      checkConnection: async () => {
        try {
          const health = await apiClient.checkHealth()
          set({ 
            isConnected: health.status === 'healthy', 
            connectionError: null 
          })
        } catch (error) {
          set({ 
            isConnected: false, 
            connectionError: error.message 
          })
        }
      },
    }),
    {
      name: 'cuebird-app-store',
    }
  )
)