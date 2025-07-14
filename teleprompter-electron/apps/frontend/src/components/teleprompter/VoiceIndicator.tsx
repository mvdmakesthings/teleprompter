"use client"

import React from 'react'
import { cn } from '@/lib/utils'
import { useTeleprompterStore } from '@/store/teleprompter'

interface VoiceIndicatorProps {
  className?: string
}

export function VoiceIndicator({ className }: VoiceIndicatorProps) {
  const { voiceEnabled, isVoiceActive } = useTeleprompterStore()

  if (!voiceEnabled) {
    return null
  }

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <div className="flex items-center space-x-1">
        <div
          className={cn(
            "h-2 w-2 rounded-full transition-colors",
            isVoiceActive ? "bg-green-500" : "bg-gray-500"
          )}
        />
        <span className="text-xs text-muted-foreground">
          {isVoiceActive ? 'Speaking' : 'Silent'}
        </span>
      </div>
      
      <div className="flex space-x-0.5">
        {[1, 2, 3, 4, 5].map((bar) => (
          <div
            key={bar}
            className={cn(
              "w-1 bg-gray-600 rounded-full transition-all duration-150",
              isVoiceActive && "bg-green-500"
            )}
            style={{
              height: isVoiceActive 
                ? `${Math.random() * 12 + 4}px`
                : '4px',
              animationDelay: `${bar * 50}ms`
            }}
          />
        ))}
      </div>
    </div>
  )
}