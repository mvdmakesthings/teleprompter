"use client"

import React from 'react'
import { PlayIcon, PauseIcon, ResetIcon } from '@radix-ui/react-icons'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Toolbar, ToolbarGroup, ToolbarSeparator } from '@/components/ui/toolbar'
import { useTeleprompterStore } from '@/store/teleprompter'

export function ControlPanel() {
  const {
    isPlaying,
    scrollSpeed,
    fontSize,
    scrollPosition,
    contentHeight,
    viewportHeight,
    setIsPlaying,
    setScrollSpeed,
    setFontSize,
    setScrollPosition,
  } = useTeleprompterStore()

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  const handleReset = () => {
    setIsPlaying(false)
    setScrollPosition(0)
  }

  const handleSpeedChange = (value: number[]) => {
    setScrollSpeed(value[0])
  }

  const handleFontSizeChange = (value: number[]) => {
    setFontSize(value[0])
  }

  // Calculate progress percentage
  const maxScroll = Math.max(0, contentHeight - viewportHeight)
  const progress = maxScroll > 0 ? (scrollPosition / maxScroll) * 100 : 0

  return (
    <Toolbar className="w-full p-4">
      <ToolbarGroup>
        <Button
          variant="teleprompter"
          size="icon"
          onClick={handlePlayPause}
          aria-label={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <PauseIcon className="h-4 w-4" />
          ) : (
            <PlayIcon className="h-4 w-4" />
          )}
        </Button>
        
        <Button
          variant="outline"
          size="icon"
          onClick={handleReset}
          aria-label="Reset"
        >
          <ResetIcon className="h-4 w-4" />
        </Button>
      </ToolbarGroup>

      <ToolbarSeparator />

      <ToolbarGroup className="flex-1">
        <div className="flex items-center space-x-4 flex-1">
          <div className="flex items-center space-x-2 min-w-[200px]">
            <span className="text-sm text-muted-foreground whitespace-nowrap">
              Speed: {scrollSpeed.toFixed(1)}x
            </span>
            <Slider
              value={[scrollSpeed]}
              onValueChange={handleSpeedChange}
              min={0.1}
              max={5}
              step={0.1}
              className="flex-1"
            />
          </div>

          <div className="flex items-center space-x-2 min-w-[200px]">
            <span className="text-sm text-muted-foreground whitespace-nowrap">
              Font: {fontSize}px
            </span>
            <Slider
              value={[fontSize]}
              onValueChange={handleFontSizeChange}
              min={16}
              max={120}
              step={2}
              className="flex-1"
            />
          </div>
        </div>
      </ToolbarGroup>

      <ToolbarSeparator />

      <ToolbarGroup>
        <div className="text-sm text-muted-foreground">
          Progress: {progress.toFixed(0)}%
        </div>
      </ToolbarGroup>
    </Toolbar>
  )
}