"use client"

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { 
  PerformanceConfig, 
  getPerformanceConfig, 
  detectOptimalProfile,
  performanceProfiles 
} from '@/lib/performance-config'

interface PerformanceContextValue {
  config: PerformanceConfig
  profile: keyof typeof performanceProfiles
  setProfile: (profile: keyof typeof performanceProfiles) => void
  updateConfig: (updates: Partial<PerformanceConfig>) => void
  resetToDefaults: () => void
}

const PerformanceContext = createContext<PerformanceContextValue | null>(null)

export function usePerformance() {
  const context = useContext(PerformanceContext)
  if (!context) {
    throw new Error('usePerformance must be used within PerformanceProvider')
  }
  return context
}

interface PerformanceProviderProps {
  children: React.ReactNode
  initialProfile?: keyof typeof performanceProfiles
}

export function PerformanceProvider({ 
  children, 
  initialProfile 
}: PerformanceProviderProps) {
  const [profile, setProfile] = useState<keyof typeof performanceProfiles>(
    initialProfile || detectOptimalProfile()
  )
  const [config, setConfig] = useState<PerformanceConfig>(
    getPerformanceConfig(profile)
  )

  // Update config when profile changes
  useEffect(() => {
    setConfig(getPerformanceConfig(profile))
  }, [profile])

  // Update individual config settings
  const updateConfig = useCallback((updates: Partial<PerformanceConfig>) => {
    setConfig(current => getPerformanceConfig({ ...current, ...updates }))
  }, [])

  // Reset to defaults for current profile
  const resetToDefaults = useCallback(() => {
    setConfig(getPerformanceConfig(profile))
  }, [profile])

  // Apply performance optimizations on mount
  useEffect(() => {
    // Enable GPU acceleration if configured
    if (config.animation.useGPUAcceleration) {
      document.body.style.transform = 'translateZ(0)'
    }

    // Set up aggressive garbage collection if enabled
    if (config.memory.enableAggressiveGC && 'gc' in window) {
      const gcInterval = setInterval(() => {
        (window as any).gc()
      }, 60000) // Run every minute

      return () => clearInterval(gcInterval)
    }
  }, [config])

  return (
    <PerformanceContext.Provider
      value={{
        config,
        profile,
        setProfile,
        updateConfig,
        resetToDefaults,
      }}
    >
      {children}
    </PerformanceContext.Provider>
  )
}