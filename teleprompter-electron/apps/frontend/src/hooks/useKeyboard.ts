"use client"

import { useEffect, useCallback, useRef } from 'react'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useSettingsStore } from '@/store/settings'

interface KeyboardCommand {
  key: string
  modifiers?: {
    ctrl?: boolean
    cmd?: boolean
    shift?: boolean
    alt?: boolean
  }
  action: string
  description: string
}

// Map action names to functions
type ActionHandler = () => void

export function useKeyboard() {
  const actionHandlersRef = useRef<Map<string, ActionHandler>>(new Map())
  
  // Store references
  const {
    isPlaying,
    setIsPlaying,
    scrollSpeed,
    setScrollSpeed,
    setScrollPosition,
    sections,
    scrollPosition,
    contentHeight,
    viewportHeight,
  } = useTeleprompterStore()
  
  const {
    voiceControlEnabled,
    setVoiceControlEnabled,
    cursorHidden,
    setCursorHidden,
  } = useSettingsStore()

  // Define action handlers
  const setupActionHandlers = useCallback(() => {
    const handlers = new Map<string, ActionHandler>()
    
    // Playback controls
    handlers.set('playPause', () => {
      useTeleprompterStore.setState({ isPlaying: !isPlaying })
    })
    
    handlers.set('reset', () => {
      useTeleprompterStore.setState({ 
        scrollPosition: 0,
        isPlaying: false 
      })
    })
    
    handlers.set('escape', () => {
      if (document.fullscreenElement) {
        document.exitFullscreen()
      } else {
        useTeleprompterStore.setState({ isPlaying: false })
      }
    })
    
    // Speed controls
    handlers.set('increaseSpeed', () => {
      const newSpeed = Math.min(5, scrollSpeed + 0.1)
      useTeleprompterStore.setState({ scrollSpeed: newSpeed })
    })
    
    handlers.set('decreaseSpeed', () => {
      const newSpeed = Math.max(0.1, scrollSpeed - 0.1)
      useTeleprompterStore.setState({ scrollSpeed: newSpeed })
    })
    
    // Navigation
    handlers.set('nextSection', () => {
      if (!sections.length) return
      
      const currentSection = sections.find(s => s.position > scrollPosition)
      if (currentSection) {
        useTeleprompterStore.setState({ 
          scrollPosition: currentSection.position,
          isPlaying: false
        })
      }
    })
    
    handlers.set('previousSection', () => {
      if (!sections.length) return
      
      const reversedSections = [...sections].reverse()
      const currentSection = reversedSections.find(s => s.position < scrollPosition - 10)
      if (currentSection) {
        useTeleprompterStore.setState({ 
          scrollPosition: currentSection.position,
          isPlaying: false
        })
      }
    })
    
    // Feature toggles
    handlers.set('toggleVoiceControl', () => {
      useSettingsStore.setState({ voiceControlEnabled: !voiceControlEnabled })
    })
    
    handlers.set('toggleCursor', () => {
      useSettingsStore.setState({ cursorHidden: !cursorHidden })
    })
    
    actionHandlersRef.current = handlers
  }, [
    isPlaying,
    scrollSpeed,
    scrollPosition,
    sections,
    voiceControlEnabled,
    cursorHidden,
    contentHeight,
    viewportHeight
  ])

  // Setup handlers whenever dependencies change
  useEffect(() => {
    setupActionHandlers()
  }, [setupActionHandlers])

  // Listen for global shortcut triggers from main process
  useEffect(() => {
    const handleShortcutTrigger = (data: { action: string }) => {
      const handler = actionHandlersRef.current.get(data.action)
      if (handler) {
        handler()
      }
    }

    if (window.electronAPI && window.electronAPI.onShortcutTriggered) {
      const unsubscribe = window.electronAPI.onShortcutTriggered(handleShortcutTrigger)
      return unsubscribe
    }
  }, [])

  // Local keyboard event handler
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Don't handle shortcuts when typing in input fields
    const target = event.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.contentEditable === 'true') {
      return
    }

    // Map keyboard events to actions
    const keyMap: { [key: string]: string } = {
      ' ': 'playPause',
      'r': 'reset',
      'R': 'reset',
      'Escape': 'escape',
      '+': 'increaseSpeed',
      '=': 'increaseSpeed',
      '-': 'decreaseSpeed',
      'ArrowUp': 'increaseSpeed',
      'ArrowDown': 'decreaseSpeed',
      'ArrowRight': 'nextSection',
      'ArrowLeft': 'previousSection',
      'PageUp': 'previousSection',
      'PageDown': 'nextSection',
      'v': 'toggleVoiceControl',
      'V': 'toggleVoiceControl',
      'c': 'toggleCursor',
      'C': 'toggleCursor',
    }

    const action = keyMap[event.key]
    if (action) {
      event.preventDefault()
      const handler = actionHandlersRef.current.get(action)
      if (handler) {
        handler()
      }
    }
  }, [])

  // Setup local keyboard listener
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  // Return keyboard shortcuts for display
  const getShortcuts = (): KeyboardCommand[] => [
    { key: 'Space', action: 'playPause', description: 'Toggle play/pause' },
    { key: 'R', action: 'reset', description: 'Reset to beginning' },
    { key: 'Esc', action: 'escape', description: 'Exit fullscreen or stop' },
    { key: '+/-', action: 'speed', description: 'Increase/decrease speed' },
    { key: '↑/↓', action: 'speed', description: 'Increase/decrease speed' },
    { key: '←/→', action: 'navigate', description: 'Previous/next section' },
    { key: 'PgUp/PgDn', action: 'navigate', description: 'Previous/next section' },
    { key: 'V', action: 'toggleVoiceControl', description: 'Toggle voice control' },
    { key: 'C', action: 'toggleCursor', description: 'Toggle cursor' },
  ]

  return {
    getShortcuts,
  }
}