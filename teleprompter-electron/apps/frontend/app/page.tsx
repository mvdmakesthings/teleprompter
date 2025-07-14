"use client"

import { useEffect } from 'react'
import { 
  OptimizedTeleprompterDisplay,
  OptimizedControlPanel,
  OptimizedFileLoader,
  ProgressBar,
  VoiceIndicator,
  SettingsDialog,
  KeyboardHelp,
  PerformanceMonitor
} from '@/components/teleprompter'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useKeyboard } from '@/hooks/useKeyboard'
import { useCursorVisibility } from '@/hooks/useCursorVisibility'

export default function HomePage() {
  const { content } = useTeleprompterStore()
  
  // Initialize keyboard shortcuts
  useKeyboard()
  
  // Initialize cursor visibility management
  useCursorVisibility()

  return (
    <main className="flex h-screen flex-col bg-teleprompter-bg">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border p-4">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-teleprompter-text">CueBird</h1>
          <VoiceIndicator />
        </div>
        <div className="flex items-center space-x-2">
          <KeyboardHelp />
          <SettingsDialog />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {content ? (
          <OptimizedTeleprompterDisplay className="flex-1" />
        ) : (
          <div className="flex flex-1 items-center justify-center p-8">
            <OptimizedFileLoader className="max-w-md w-full" />
          </div>
        )}
      </div>

      {/* Footer Controls */}
      <footer className="border-t border-border">
        {content && (
          <div className="p-4">
            <ProgressBar className="mb-4" />
          </div>
        )}
        <OptimizedControlPanel />
      </footer>

      {/* Performance Monitor (only in development) */}
      <PerformanceMonitor />
    </main>
  )
}