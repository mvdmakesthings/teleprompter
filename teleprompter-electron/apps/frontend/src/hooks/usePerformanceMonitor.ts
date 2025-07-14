import { useEffect, useRef, useState, useCallback } from 'react'

interface PerformanceMetrics {
  fps: number
  renderTime: number
  frameDrops: number
  memoryUsage: number
  timestamp: number
}

interface PerformanceMonitorOptions {
  enabled?: boolean
  sampleInterval?: number
  warningThreshold?: number
}

export function usePerformanceMonitor(options: PerformanceMonitorOptions = {}) {
  const {
    enabled = true,
    sampleInterval = 1000,
    warningThreshold = 50, // FPS warning threshold
  } = options

  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 60,
    renderTime: 0,
    frameDrops: 0,
    memoryUsage: 0,
    timestamp: Date.now(),
  })

  const frameCountRef = useRef(0)
  const lastTimeRef = useRef(performance.now())
  const frameDropsRef = useRef(0)
  const rafIdRef = useRef<number>()

  const measureFrame = useCallback(() => {
    if (!enabled) return

    const currentTime = performance.now()
    const deltaTime = currentTime - lastTimeRef.current

    // Detect frame drops (frame took longer than 16.67ms for 60fps)
    if (deltaTime > 16.67) {
      frameDropsRef.current++
    }

    frameCountRef.current++
    lastTimeRef.current = currentTime

    rafIdRef.current = requestAnimationFrame(measureFrame)
  }, [enabled])

  useEffect(() => {
    if (!enabled) return

    const intervalId = setInterval(() => {
      const now = performance.now()
      const elapsedSeconds = (now - metrics.timestamp) / 1000
      const fps = Math.round(frameCountRef.current / elapsedSeconds)

      // Get memory usage if available
      let memoryUsage = 0
      if ('memory' in performance) {
        const memory = (performance as any).memory
        memoryUsage = memory.usedJSHeapSize / (1024 * 1024) // Convert to MB
      }

      // Get render time from performance entries
      const navigationEntries = performance.getEntriesByType('navigation')
      const renderTime = navigationEntries.length > 0
        ? (navigationEntries[0] as PerformanceNavigationTiming).loadEventEnd -
          (navigationEntries[0] as PerformanceNavigationTiming).fetchStart
        : 0

      setMetrics({
        fps: Math.min(fps, 60), // Cap at 60 FPS
        renderTime,
        frameDrops: frameDropsRef.current,
        memoryUsage,
        timestamp: now,
      })

      // Reset counters
      frameCountRef.current = 0
      frameDropsRef.current = 0

      // Log warning if FPS drops below threshold
      if (fps < warningThreshold) {
        console.warn(`Performance warning: FPS dropped to ${fps}`)
      }
    }, sampleInterval)

    // Start measuring frames
    rafIdRef.current = requestAnimationFrame(measureFrame)

    return () => {
      clearInterval(intervalId)
      if (rafIdRef.current) {
        cancelAnimationFrame(rafIdRef.current)
      }
    }
  }, [enabled, sampleInterval, warningThreshold, measureFrame, metrics.timestamp])

  const reset = useCallback(() => {
    frameCountRef.current = 0
    frameDropsRef.current = 0
    lastTimeRef.current = performance.now()
    setMetrics({
      fps: 60,
      renderTime: 0,
      frameDrops: 0,
      memoryUsage: 0,
      timestamp: Date.now(),
    })
  }, [])

  return {
    metrics,
    reset,
    isPerformanceOptimal: metrics.fps >= 55, // Consider 55+ FPS as optimal
  }
}