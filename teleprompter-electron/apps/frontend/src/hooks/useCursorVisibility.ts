"use client"

import { useEffect } from 'react'
import { useSettingsStore } from '@/store/settings'

export function useCursorVisibility() {
  const { cursorHidden, cursorAutoHide } = useSettingsStore()

  useEffect(() => {
    // Apply cursor visibility
    if (cursorHidden) {
      document.body.style.cursor = 'none'
    } else {
      document.body.style.cursor = 'auto'
    }

    return () => {
      document.body.style.cursor = 'auto'
    }
  }, [cursorHidden])

  // Auto-hide cursor when inactive
  useEffect(() => {
    if (!cursorAutoHide) return

    let timeout: NodeJS.Timeout

    const showCursor = () => {
      if (!cursorHidden) {
        document.body.style.cursor = 'auto'
      }
      clearTimeout(timeout)
      timeout = setTimeout(() => {
        if (!cursorHidden) {
          document.body.style.cursor = 'none'
        }
      }, 3000) // Hide after 3 seconds of inactivity
    }

    const handleMouseMove = () => showCursor()
    const handleMouseLeave = () => {
      if (!cursorHidden) {
        document.body.style.cursor = 'none'
      }
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      clearTimeout(timeout)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseleave', handleMouseLeave)
      document.body.style.cursor = 'auto'
    }
  }, [cursorAutoHide, cursorHidden])
}