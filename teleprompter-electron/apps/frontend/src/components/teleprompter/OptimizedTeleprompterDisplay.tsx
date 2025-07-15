"use client"

import React, { useEffect, useRef, useState, useCallback, useMemo, useDeferredValue, useTransition } from 'react'
import { cn } from '@/lib/utils'
import { useTeleprompterStore } from '@/store/teleprompter'
import { VirtualScroller } from './VirtualScroller'
import { usePerformanceMonitor } from '@/hooks/usePerformanceMonitor'
import { useThrottle } from '@/hooks/useThrottle'
import { usePerformance } from '@/components/providers/performance-provider'

interface OptimizedTeleprompterDisplayProps {
  className?: string
}

export const OptimizedTeleprompterDisplay = React.memo(function OptimizedTeleprompterDisplay({
  className,
}: OptimizedTeleprompterDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  const [isScrolling, setIsScrolling] = useState(false)
  const animationRef = useRef<number>()
  const lastFrameTime = useRef(0)
  const [isPending, startTransition] = useTransition()

  const {
    content,
    isPlaying,
    scrollSpeed,
    fontSize,
    scrollPosition,
    setScrollPosition,
    setContentHeight,
    setViewportHeight,
    wordCount,
  } = useTeleprompterStore()

  // Get performance configuration
  const { config: perfConfig } = usePerformance()

  // Defer non-critical updates
  const deferredContent = useDeferredValue(content)
  const deferredFontSize = useDeferredValue(fontSize)

  // Performance monitoring
  const { metrics, isPerformanceOptimal } = usePerformanceMonitor({
    enabled: perfConfig.monitoring.enabled,
    sampleInterval: perfConfig.monitoring.sampleInterval,
    warningThreshold: perfConfig.monitoring.warningThresholds.fps,
  })

  // Determine if virtual scrolling should be used
  const shouldUseVirtualScrolling = useMemo(() => {
    return perfConfig.virtualScrolling.enabled && wordCount > perfConfig.virtualScrolling.wordThreshold
  }, [perfConfig.virtualScrolling, wordCount])

  // Throttled scroll position update - use stable reference
  const throttledSetScrollPosition = useMemo(() => {
    // Create a throttled version that doesn't recreate on every render
    let lastRun = 0
    let timeout: NodeJS.Timeout | null = null

    return (position: number) => {
      const now = Date.now()
      const timeSinceLastRun = now - lastRun
      const delay = perfConfig.animation.scrollThrottleMs

      if (timeSinceLastRun >= delay) {
        lastRun = now
        setScrollPosition(position)
      } else {
        if (timeout) clearTimeout(timeout)
        timeout = setTimeout(() => {
          lastRun = Date.now()
          setScrollPosition(position)
        }, delay - timeSinceLastRun)
      }
    }
  }, [perfConfig.animation.scrollThrottleMs])

  // Update dimensions with transition for non-critical updates
  const updateDimensions = useCallback(() => {
    startTransition(() => {
      if (containerRef.current && contentRef.current) {
        setViewportHeight(containerRef.current.clientHeight)
        setContentHeight(contentRef.current.scrollHeight)
      }
    })
  }, [setContentHeight, setViewportHeight])

  useEffect(() => {
    updateDimensions()
    window.addEventListener('resize', updateDimensions)

    return () => window.removeEventListener('resize', updateDimensions)
  }, [deferredContent])

  // Optimized scrolling animation with frame time tracking
  const scroll = useCallback(() => {
    if (!isPlaying || !containerRef.current) return

    const currentTime = performance.now()
    const deltaTime = currentTime - lastFrameTime.current

    // Skip frame if running too fast (prevent unnecessary updates)
    const targetFrameTime = 1000 / perfConfig.animation.targetFPS
    if (deltaTime < targetFrameTime) {
      animationRef.current = requestAnimationFrame(scroll)
      return
    }

    lastFrameTime.current = currentTime

    const container = containerRef.current
    const maxScroll = container.scrollHeight - container.clientHeight
    const currentScroll = container.scrollTop

    if (currentScroll < maxScroll) {
      // Adjust scroll speed based on actual frame time for consistent speed
      const frameAdjustedSpeed = scrollSpeed * (deltaTime / 16.67)
      const newPosition = Math.min(currentScroll + frameAdjustedSpeed, maxScroll)

      container.scrollTop = newPosition
      throttledSetScrollPosition(newPosition)
      setIsScrolling(true)
      animationRef.current = requestAnimationFrame(scroll)
    } else {
      setIsScrolling(false)
      useTeleprompterStore.setState({ isPlaying: false })
      animationRef.current = undefined
    }
  }, [isPlaying, scrollSpeed, throttledSetScrollPosition, perfConfig.animation.targetFPS])

  // Handle scrolling animation
  useEffect(() => {
    if (!containerRef.current || !contentRef.current) return

    // Always cancel any existing animation frame before starting a new one
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = undefined
    }

    if (isPlaying) {
      setIsScrolling(true)
      lastFrameTime.current = performance.now()
      animationRef.current = requestAnimationFrame(scroll)
    } else {
      setIsScrolling(false)
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
        animationRef.current = undefined
      }
      setIsScrolling(false)
    }
  }, [isPlaying, scroll])

  // Handle manual scrolling with throttling
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    if (!isScrolling && containerRef.current) {
      throttledSetScrollPosition(containerRef.current.scrollTop)
    }
  }, [isScrolling, throttledSetScrollPosition])

  // Handle mouse wheel
  const handleWheel = useCallback((e: React.WheelEvent<HTMLDivElement>) => {
    if (isPlaying) {
      useTeleprompterStore.setState({ isPlaying: false })
    }
  }, [isPlaying])

  // Set scroll position - only update when position changes and not scrolling
  useEffect(() => {
    if (containerRef.current && !isScrolling) {
      const currentScrollTop = containerRef.current.scrollTop
      // Only update if position is different to prevent infinite loops
      if (Math.abs(currentScrollTop - scrollPosition) > 1) {
        containerRef.current.scrollTop = scrollPosition
      }
    }
  }, [scrollPosition, isScrolling])

  // Handle virtual scroller scroll
  const handleVirtualScroll = useCallback((position: number) => {
    throttledSetScrollPosition(position)
  }, [throttledSetScrollPosition])

  // Performance warning
  useEffect(() => {
    if (perfConfig.monitoring.logWarnings && !isPerformanceOptimal) {
      console.warn('Performance degradation detected:', metrics)
    }
  }, [perfConfig.monitoring.logWarnings, isPerformanceOptimal, metrics])

  // Use virtual scrolling for large texts
  if (shouldUseVirtualScrolling) {
    return (
      <VirtualScroller
        content={deferredContent}
        fontSize={deferredFontSize}
        lineHeight={1.6}
        className={cn(
          "teleprompter-display",
          "bg-teleprompter-bg text-teleprompter-text",
          className
        )}
        onScroll={handleVirtualScroll}
        scrollPosition={scrollPosition}
        isPlaying={isPlaying}
        scrollSpeed={scrollSpeed}
      />
    )
  }

  // Regular scrolling for smaller texts
  return (
    <div
      ref={containerRef}
      className={cn(
        "teleprompter-display relative h-full w-full overflow-y-auto",
        "bg-teleprompter-bg text-teleprompter-text",
        className
      )}
      onScroll={handleScroll}
      onWheel={handleWheel}
    >
      <div
        ref={contentRef}
        className="px-8 py-16"
        style={{
          fontSize: `${deferredFontSize}px`,
          lineHeight: 1.6,
          willChange: isScrolling ? 'transform' : 'auto',
          transform: perfConfig.animation.useGPUAcceleration ? 'translateZ(0)' : undefined,
        }}
      >
        {deferredContent ? (
          <div dangerouslySetInnerHTML={{ __html: deferredContent }} />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-500">
            <p>Load a file to begin</p>
          </div>
        )}
      </div>
    </div>
  )
})