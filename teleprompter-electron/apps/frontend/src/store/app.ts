import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import axios, { AxiosInstance } from 'axios'

interface AppState {
  // Backend connection
  backendUrl: string | null
  isConnected: boolean
  apiClient: AxiosInstance | null
  
  // App settings
  settings: any | null
  
  // Actions
  setBackendUrl: (url: string) => void
  setIsConnected: (connected: boolean) => void
  setSettings: (settings: any) => void
  initializeApi: (url: string) => void
}

export const useAppStore = create<AppState>()(
  devtools(
    (set, get) => ({
      backendUrl: null,
      isConnected: false,
      apiClient: null,
      settings: null,
      
      setBackendUrl: (backendUrl) => set({ backendUrl }),
      setIsConnected: (isConnected) => set({ isConnected }),
      setSettings: (settings) => set({ settings }),
      
      initializeApi: (url) => {
        const apiClient = axios.create({
          baseURL: url,
          headers: {
            'Content-Type': 'application/json',
          },
        })
        
        set({ 
          apiClient, 
          backendUrl: url,
          isConnected: true 
        })
      },
    }),
    {
      name: 'app-store',
    }
  )
)