"use client"

import React, { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useWebSocketContext } from '@/components/providers/websocket-provider'
import { useVoiceControl } from '@/hooks/useVoiceControl'

interface VoiceIndicatorProps {
  className?: string
}

export function VoiceIndicator({ className }: VoiceIndicatorProps) {
  const { voiceEnabled, isVoiceActive } = useTeleprompterStore()
  const { isConnected } = useWebSocketContext()
  const { audioLevel, isProcessing, error, permissionState } = useVoiceControl()
  
  // Animated bars state
  const [barHeights, setBarHeights] = useState([4, 4, 4, 4, 4])
  
  // Animate bars based on audio level and voice activity
  useEffect(() => {
    if (isVoiceActive && audioLevel > 0) {
      const interval = setInterval(() => {
        setBarHeights([
          Math.random() * audioLevel * 16 + 4,
          Math.random() * audioLevel * 16 + 4,
          Math.random() * audioLevel * 16 + 4,
          Math.random() * audioLevel * 16 + 4,
          Math.random() * audioLevel * 16 + 4,
        ])
      }, 100)
      
      return () => clearInterval(interval)
    } else {
      setBarHeights([4, 4, 4, 4, 4])
    }
  }, [isVoiceActive, audioLevel])

  if (!voiceEnabled) {
    return null
  }
  
  // Determine status text
  let statusText = 'Silent'
  if (!isConnected) {
    statusText = 'Disconnected'
  } else if (error) {
    statusText = 'Error'
  } else if (permissionState === 'denied') {
    statusText = 'Permission Denied'
  } else if (!isProcessing) {
    statusText = 'Starting...'
  } else if (isVoiceActive) {
    statusText = 'Speaking'
  }
  
  // Determine status color
  let statusColor = 'bg-gray-500'
  if (!isConnected || error || permissionState === 'denied') {
    statusColor = 'bg-red-500'
  } else if (isVoiceActive) {
    statusColor = 'bg-green-500'
  } else if (!isProcessing) {
    statusColor = 'bg-yellow-500'
  }

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <div className="flex items-center space-x-1">
        <div
          className={cn(
            "h-2 w-2 rounded-full transition-colors",
            statusColor
          )}
        />
        <span className="text-xs text-muted-foreground">
          {statusText}
        </span>
      </div>
      
      <div className="flex space-x-0.5 items-end h-4">
        {barHeights.map((height, index) => (
          <div
            key={index}
            className={cn(
              "w-1 rounded-full transition-all duration-150",
              isVoiceActive ? "bg-green-500" : "bg-gray-600"
            )}
            style={{
              height: `${height}px`,
              transform: `scaleY(${isProcessing ? 1 : 0})`,
              transition: 'height 0.1s ease-out, transform 0.3s ease-out',
            }}
          />
        ))}
      </div>
      
      {error && (
        <span className="text-xs text-red-500 ml-2" title={error}>
          ⚠️
        </span>
      )}
    </div>
  )
}