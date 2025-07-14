"use client"

import React, { useCallback, useEffect, useRef, useState, useMemo } from 'react'
import { cn } from '@/lib/utils'

interface VirtualScrollerProps {
  content: string
  fontSize: number
  lineHeight: number
  className?: string
  onScroll?: (position: number) => void
  scrollPosition?: number
  isPlaying?: boolean
  scrollSpeed?: number
}

interface Chunk {
  id: number
  content: string
  height: number
  offset: number
}

const CHUNK_SIZE = 1000 // Characters per chunk
const OVERSCAN = 3 // Number of chunks to render outside viewport

export const VirtualScroller = React.memo(function VirtualScroller({
  content,
  fontSize,
  lineHeight,
  className,
  onScroll,
  scrollPosition = 0,
  isPlaying = false,
  scrollSpeed = 1,
}: VirtualScrollerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const measureRef = useRef<HTMLDivElement>(null)
  const animationRef = useRef<number>()
  
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 10 })
  const [containerHeight, setContainerHeight] = useState(0)

  // Split content into chunks
  const chunks = useMemo(() => {
    const result: Chunk[] = []
    let offset = 0
    
    for (let i = 0; i < content.length; i += CHUNK_SIZE) {
      const chunkContent = content.slice(i, Math.min(i + CHUNK_SIZE, content.length))
      const estimatedHeight = estimateHeight(chunkContent, fontSize, lineHeight)
      
      result.push({
        id: i / CHUNK_SIZE,
        content: chunkContent,
        height: estimatedHeight,
        offset,
      })
      
      offset += estimatedHeight
    }
    
    return result
  }, [content, fontSize, lineHeight])

  const totalHeight = useMemo(() => {
    return chunks.reduce((sum, chunk) => sum + chunk.height, 0)
  }, [chunks])

  // Estimate height based on content
  function estimateHeight(text: string, fontSize: number, lineHeight: number): number {
    // Rough estimation: assume average of 50 characters per line
    const lines = Math.ceil(text.length / 50)
    return lines * fontSize * lineHeight
  }

  // Update visible range based on scroll position
  const updateVisibleRange = useCallback(() => {
    if (!containerRef.current) return

    const scrollTop = scrollPosition
    const viewportHeight = containerHeight
    
    // Find chunks that are visible
    let startIdx = 0
    let endIdx = chunks.length - 1
    
    for (let i = 0; i < chunks.length; i++) {
      if (chunks[i].offset + chunks[i].height >= scrollTop) {
        startIdx = Math.max(0, i - OVERSCAN)
        break
      }
    }
    
    for (let i = startIdx; i < chunks.length; i++) {
      if (chunks[i].offset > scrollTop + viewportHeight) {
        endIdx = Math.min(chunks.length - 1, i + OVERSCAN)
        break
      }
    }
    
    setVisibleRange({ start: startIdx, end: endIdx })
  }, [chunks, scrollPosition, containerHeight])

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        setContainerHeight(containerRef.current.clientHeight)
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Update visible range when dependencies change
  useEffect(() => {
    updateVisibleRange()
  }, [updateVisibleRange])

  // Handle scrolling animation
  useEffect(() => {
    if (!scrollRef.current || !isPlaying) return

    const animate = () => {
      if (!scrollRef.current || !isPlaying) return

      const maxScroll = totalHeight - containerHeight
      const currentScroll = scrollPosition
      
      if (currentScroll < maxScroll) {
        const newPosition = Math.min(currentScroll + scrollSpeed, maxScroll)
        scrollRef.current.scrollTop = newPosition
        if (onScroll) onScroll(newPosition)
        animationRef.current = requestAnimationFrame(animate)
      }
    }

    animationRef.current = requestAnimationFrame(animate)

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isPlaying, scrollSpeed, scrollPosition, totalHeight, containerHeight, onScroll])

  // Handle manual scroll
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const scrollTop = e.currentTarget.scrollTop
    if (onScroll) onScroll(scrollTop)
    updateVisibleRange()
  }, [onScroll, updateVisibleRange])

  // Set scroll position
  useEffect(() => {
    if (scrollRef.current && !isPlaying) {
      scrollRef.current.scrollTop = scrollPosition
    }
  }, [scrollPosition, isPlaying])

  // Render only visible chunks
  const visibleChunks = chunks.slice(visibleRange.start, visibleRange.end + 1)

  return (
    <div
      ref={containerRef}
      className={cn("relative h-full w-full overflow-hidden", className)}
    >
      <div
        ref={scrollRef}
        className="h-full w-full overflow-y-auto"
        onScroll={handleScroll}
      >
        {/* Total height spacer */}
        <div style={{ height: totalHeight, position: 'relative' }}>
          {/* Render only visible chunks */}
          {visibleChunks.map((chunk) => (
            <div
              key={chunk.id}
              style={{
                position: 'absolute',
                top: chunk.offset,
                left: 0,
                right: 0,
                height: chunk.height,
                fontSize: `${fontSize}px`,
                lineHeight,
              }}
              className="px-8"
            >
              <div dangerouslySetInnerHTML={{ __html: chunk.content }} />
            </div>
          ))}
        </div>
      </div>
      
      {/* Hidden measurement div for accurate height calculation */}
      <div
        ref={measureRef}
        style={{
          position: 'absolute',
          visibility: 'hidden',
          fontSize: `${fontSize}px`,
          lineHeight,
        }}
        className="px-8"
      />
    </div>
  )
})