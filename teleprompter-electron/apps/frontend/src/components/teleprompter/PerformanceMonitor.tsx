"use client"

import React from 'react'
import { usePerformanceMonitor } from '@/hooks/usePerformanceMonitor'
import { cn } from '@/lib/utils'

interface PerformanceMonitorProps {
  className?: string
  showInProduction?: boolean
}

export const PerformanceMonitor = React.memo(function PerformanceMonitor({
  className,
  showInProduction = false,
}: PerformanceMonitorProps) {
  const { metrics, isPerformanceOptimal } = usePerformanceMonitor({
    enabled: showInProduction || process.env.NODE_ENV === 'development',
  })

  // Don't show in production unless explicitly enabled
  if (!showInProduction && process.env.NODE_ENV === 'production') {
    return null
  }

  const getFpsColor = (fps: number) => {
    if (fps >= 55) return 'text-green-500'
    if (fps >= 45) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getMemoryColor = (memory: number) => {
    if (memory < 100) return 'text-green-500'
    if (memory < 200) return 'text-yellow-500'
    return 'text-red-500'
  }

  return (
    <div
      className={cn(
        "fixed bottom-4 right-4 bg-black/80 text-white p-3 rounded-lg text-xs font-mono backdrop-blur-sm",
        "transition-opacity duration-200",
        isPerformanceOptimal ? "opacity-50 hover:opacity-100" : "opacity-100",
        className
      )}
    >
      <div className="space-y-1">
        <div className="flex items-center justify-between space-x-4">
          <span>FPS:</span>
          <span className={cn("font-bold", getFpsColor(metrics.fps))}>
            {metrics.fps}
          </span>
        </div>
        
        <div className="flex items-center justify-between space-x-4">
          <span>Frame Drops:</span>
          <span className={metrics.frameDrops > 10 ? "text-yellow-500" : ""}>
            {metrics.frameDrops}
          </span>
        </div>
        
        {metrics.memoryUsage > 0 && (
          <div className="flex items-center justify-between space-x-4">
            <span>Memory:</span>
            <span className={getMemoryColor(metrics.memoryUsage)}>
              {metrics.memoryUsage.toFixed(1)} MB
            </span>
          </div>
        )}
        
        {metrics.renderTime > 0 && (
          <div className="flex items-center justify-between space-x-4">
            <span>Render:</span>
            <span>{metrics.renderTime.toFixed(0)} ms</span>
          </div>
        )}
        
        <div className="border-t border-gray-600 pt-1 mt-1">
          <div className="flex items-center space-x-2">
            <div className={cn(
              "w-2 h-2 rounded-full",
              isPerformanceOptimal ? "bg-green-500" : "bg-yellow-500"
            )} />
            <span className="text-xs">
              {isPerformanceOptimal ? "Optimal" : "Degraded"}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
})