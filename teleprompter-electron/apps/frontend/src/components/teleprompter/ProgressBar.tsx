"use client"

import React from 'react'
import { cn } from '@/lib/utils'
import { useTeleprompterStore } from '@/store/teleprompter'

interface ProgressBarProps {
  className?: string
  showTime?: boolean
}

export function ProgressBar({ className, showTime = true }: ProgressBarProps) {
  const {
    scrollPosition,
    contentHeight,
    viewportHeight,
    scrollSpeed,
    wordCount,
  } = useTeleprompterStore()

  // Calculate progress
  const maxScroll = Math.max(0, contentHeight - viewportHeight)
  const progress = maxScroll > 0 ? (scrollPosition / maxScroll) * 100 : 0

  // Estimate remaining time (rough calculation)
  const remainingPixels = maxScroll - scrollPosition
  const remainingSeconds = scrollSpeed > 0 ? remainingPixels / (scrollSpeed * 60) : 0
  const remainingMinutes = Math.floor(remainingSeconds / 60)
  const remainingSecondsDisplay = Math.floor(remainingSeconds % 60)

  // Words per minute estimation
  const progressFraction = progress / 100
  const wordsRead = Math.floor(wordCount * progressFraction)
  const wordsRemaining = wordCount - wordsRead

  return (
    <div className={cn("w-full space-y-2", className)}>
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full bg-teleprompter-accent transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      
      {showTime && (
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>{wordsRead} / {wordCount} words</span>
          <span>
            {remainingMinutes > 0 && `${remainingMinutes}m `}
            {remainingSecondsDisplay}s remaining
          </span>
        </div>
      )}
    </div>
  )
}