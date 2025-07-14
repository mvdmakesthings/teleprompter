"use client"

import React, { useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/utils'
import { useTeleprompterStore } from '@/store/teleprompter'

interface TeleprompterDisplayProps {
  className?: string
}

export function TeleprompterDisplay({ className }: TeleprompterDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  const [isScrolling, setIsScrolling] = useState(false)
  const animationRef = useRef<number>()
  
  const {
    content,
    isPlaying,
    scrollSpeed,
    fontSize,
    scrollPosition,
    setScrollPosition,
    setContentHeight,
    setViewportHeight,
  } = useTeleprompterStore()

  // Update dimensions
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current && contentRef.current) {
        setViewportHeight(containerRef.current.clientHeight)
        setContentHeight(contentRef.current.scrollHeight)
      }
    }

    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    
    return () => window.removeEventListener('resize', updateDimensions)
  }, [content, setContentHeight, setViewportHeight])

  // Handle scrolling animation
  useEffect(() => {
    if (!containerRef.current || !contentRef.current) return

    // Always cancel any existing animation frame before starting a new one
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = undefined
    }

    const scroll = () => {
      if (!isPlaying || !containerRef.current) return

      const container = containerRef.current
      const maxScroll = container.scrollHeight - container.clientHeight
      const currentScroll = container.scrollTop
      
      if (currentScroll < maxScroll) {
        const newPosition = Math.min(currentScroll + scrollSpeed, maxScroll)
        container.scrollTop = newPosition
        setScrollPosition(newPosition)
        setIsScrolling(true)
        animationRef.current = requestAnimationFrame(scroll)
      } else {
        setIsScrolling(false)
        useTeleprompterStore.setState({ isPlaying: false })
        animationRef.current = undefined
      }
    }

    if (isPlaying) {
      setIsScrolling(true)
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
  }, [isPlaying, scrollSpeed, setScrollPosition])

  // Handle manual scrolling
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    if (!isScrolling && containerRef.current) {
      setScrollPosition(containerRef.current.scrollTop)
    }
  }

  // Handle mouse wheel
  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    if (isPlaying) {
      useTeleprompterStore.setState({ isPlaying: false })
    }
  }

  // Set scroll position
  useEffect(() => {
    if (containerRef.current && !isScrolling) {
      containerRef.current.scrollTop = scrollPosition
    }
  }, [scrollPosition, isScrolling])

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
        style={{ fontSize: `${fontSize}px`, lineHeight: 1.6 }}
      >
        {content ? (
          <div dangerouslySetInnerHTML={{ __html: content }} />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-500">
            <p>Load a file to begin</p>
          </div>
        )}
      </div>
    </div>
  )
}