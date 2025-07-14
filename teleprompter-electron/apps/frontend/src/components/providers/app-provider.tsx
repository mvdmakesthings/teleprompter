'use client'

import { useEffect } from 'react'
import { useAppStore } from '@/store/app-store'
import { PerformanceProvider } from './performance-provider'

export function AppProvider({ children }: { children: React.ReactNode }) {
  const initialize = useAppStore(state => state.initialize)

  useEffect(() => {
    // Initialize app when running in Electron
    if (typeof window !== 'undefined' && window.electronAPI) {
      // Get backend URL and settings from Electron
      Promise.all([
        window.electronAPI.getBackendUrl(),
        window.electronAPI.getSettings()
      ]).then(([backendUrl, settings]) => {
        initialize(backendUrl, settings)
      }).catch(err => {
        console.error('Failed to initialize from Electron:', err)
        // Fall back to development defaults
        initialize('http://localhost:8000', {} as any)
      })

      // Listen for settings changes
      const unsubscribe = window.electronAPI.onSettingsChanged((settings) => {
        useAppStore.getState().updateSettings(settings)
      })

      return () => {
        unsubscribe()
      }
    } else {
      // Development mode - use local backend
      const initData = window.__CUEBIRD_INIT__
      if (initData) {
        initialize(initData.backendUrl, initData.settings)
      } else {
        initialize('http://localhost:8000', {} as any)
      }
    }
  }, [initialize])

  return (
    <PerformanceProvider>
      {children}
    </PerformanceProvider>
  )
}