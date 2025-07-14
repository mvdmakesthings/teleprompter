"use client"

import { useEffect } from 'react'
import { 
  TeleprompterDisplay,
  ControlPanel,
  FileLoader,
  ProgressBar,
  VoiceIndicator,
  SettingsDialog
} from '@/components/teleprompter'
import { useTeleprompterStore } from '@/store/teleprompter'

export default function HomePage() {
  const { content } = useTeleprompterStore()

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault()
        const { isPlaying, setIsPlaying } = useTeleprompterStore.getState()
        setIsPlaying(!isPlaying)
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [])

  return (
    <main className="flex h-screen flex-col bg-teleprompter-bg">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border p-4">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-teleprompter-text">CueBird</h1>
          <VoiceIndicator />
        </div>
        <SettingsDialog />
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {content ? (
          <TeleprompterDisplay className="flex-1" />
        ) : (
          <div className="flex flex-1 items-center justify-center p-8">
            <FileLoader className="max-w-md w-full" />
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
        <ControlPanel />
      </footer>
    </main>
  )
}