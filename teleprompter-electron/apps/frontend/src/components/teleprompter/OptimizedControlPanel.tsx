"use client"

import React, { useCallback, useMemo } from 'react'
import { PlayIcon, PauseIcon, ResetIcon } from '@radix-ui/react-icons'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Toolbar, ToolbarGroup, ToolbarSeparator } from '@/components/ui/toolbar'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useDebounce } from '@/hooks/useDebounce'

// Memoized sub-components for better performance
const PlayPauseButton = React.memo(({ isPlaying, onClick }: { isPlaying: boolean; onClick: () => void }) => (
  <Button
    variant="teleprompter"
    size="icon"
    onClick={onClick}
    aria-label={isPlaying ? 'Pause' : 'Play'}
  >
    {isPlaying ? (
      <PauseIcon className="h-4 w-4" />
    ) : (
      <PlayIcon className="h-4 w-4" />
    )}
  </Button>
))
PlayPauseButton.displayName = 'PlayPauseButton'

const ResetButton = React.memo(({ onClick }: { onClick: () => void }) => (
  <Button
    variant="outline"
    size="icon"
    onClick={onClick}
    aria-label="Reset"
  >
    <ResetIcon className="h-4 w-4" />
  </Button>
))
ResetButton.displayName = 'ResetButton'

const SpeedControl = React.memo(({ 
  speed, 
  onChange 
}: { 
  speed: number; 
  onChange: (value: number[]) => void 
}) => {
  // Debounce the displayed value for smoother UI
  const debouncedSpeed = useDebounce(speed, 100)
  
  return (
    <div className="flex items-center space-x-2 min-w-[200px]">
      <span className="text-sm text-muted-foreground whitespace-nowrap">
        Speed: {debouncedSpeed.toFixed(1)}x
      </span>
      <Slider
        value={[speed]}
        onValueChange={onChange}
        min={0.1}
        max={5}
        step={0.1}
        className="flex-1"
      />
    </div>
  )
})
SpeedControl.displayName = 'SpeedControl'

const FontSizeControl = React.memo(({ 
  fontSize, 
  onChange 
}: { 
  fontSize: number; 
  onChange: (value: number[]) => void 
}) => {
  // Debounce the displayed value for smoother UI
  const debouncedFontSize = useDebounce(fontSize, 100)
  
  return (
    <div className="flex items-center space-x-2 min-w-[200px]">
      <span className="text-sm text-muted-foreground whitespace-nowrap">
        Font: {debouncedFontSize}px
      </span>
      <Slider
        value={[fontSize]}
        onValueChange={onChange}
        min={16}
        max={120}
        step={2}
        className="flex-1"
      />
    </div>
  )
})
FontSizeControl.displayName = 'FontSizeControl'

const ProgressDisplay = React.memo(({ progress }: { progress: number }) => (
  <div className="text-sm text-muted-foreground">
    Progress: {progress.toFixed(0)}%
  </div>
))
ProgressDisplay.displayName = 'ProgressDisplay'

export const OptimizedControlPanel = React.memo(function OptimizedControlPanel() {
  const {
    isPlaying,
    scrollSpeed,
    fontSize,
    progress,
    setIsPlaying,
    setScrollSpeed,
    setFontSize,
    setScrollPosition,
  } = useTeleprompterStore()

  // Memoize callbacks to prevent unnecessary re-renders
  const handlePlayPause = useCallback(() => {
    setIsPlaying(!isPlaying)
  }, [isPlaying, setIsPlaying])

  const handleReset = useCallback(() => {
    setIsPlaying(false)
    setScrollPosition(0)
  }, [setIsPlaying, setScrollPosition])

  const handleSpeedChange = useCallback((value: number[]) => {
    setScrollSpeed(value[0])
  }, [setScrollSpeed])

  const handleFontSizeChange = useCallback((value: number[]) => {
    setFontSize(value[0])
  }, [setFontSize])

  // Memoize computed values
  const currentProgress = useMemo(() => progress(), [progress])

  return (
    <Toolbar className="w-full p-4">
      <ToolbarGroup>
        <PlayPauseButton isPlaying={isPlaying} onClick={handlePlayPause} />
        <ResetButton onClick={handleReset} />
      </ToolbarGroup>

      <ToolbarSeparator />

      <ToolbarGroup className="flex-1">
        <div className="flex items-center space-x-4 flex-1">
          <SpeedControl speed={scrollSpeed} onChange={handleSpeedChange} />
          <FontSizeControl fontSize={fontSize} onChange={handleFontSizeChange} />
        </div>
      </ToolbarGroup>

      <ToolbarSeparator />

      <ToolbarGroup>
        <ProgressDisplay progress={currentProgress} />
      </ToolbarGroup>
    </Toolbar>
  )
})