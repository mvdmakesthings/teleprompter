"use client"

import React, { useCallback, useState } from 'react'
import { FileIcon, UploadIcon } from '@radix-ui/react-icons'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useAppStore } from '@/store/app'

interface FileLoaderProps {
  className?: string
}

export function FileLoader({ className }: FileLoaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { currentFile } = useTeleprompterStore()
  const { apiClient } = useAppStore()

  const handleFileSelect = useCallback(async () => {
    if (!window.electronAPI) {
      console.error('Electron API not available')
      return
    }

    try {
      const result = await window.electronAPI.showOpenDialog({
        properties: ['openFile'],
        filters: [
          { name: 'Markdown', extensions: ['md', 'markdown'] },
          { name: 'Text', extensions: ['txt'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      })

      if (!result.canceled && result.filePaths.length > 0) {
        await loadFile(result.filePaths[0])
      }
    } catch (error) {
      console.error('Failed to open file dialog:', error)
    }
  }, [])

  const loadFile = useCallback(async (filePath: string) => {
    if (!apiClient) {
      setError('Application not ready. Please try again.')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await apiClient.post('/api/content/load', {
        file_path: filePath
      })

      if (response.data.success) {
        const { content, parsed_content, word_count, sections } = response.data
        
        useTeleprompterStore.setState({
          content: parsed_content,
          rawContent: content,
          currentFile: filePath,
          wordCount: word_count,
          sections: sections,
          scrollPosition: 0,
          isPlaying: false,
        })
      } else {
        setError(response.data.error || 'Failed to load file')
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load file'
      setError(message)
      console.error('Failed to load file:', error)
    } finally {
      setIsLoading(false)
    }
  }, [apiClient])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    const markdownFile = files.find(file => 
      file.name.endsWith('.md') || 
      file.name.endsWith('.markdown') || 
      file.name.endsWith('.txt')
    )

    if (markdownFile && window.electronAPI) {
      // Note: In a real implementation, we'd need to handle file paths differently
      // as browser File objects don't have full paths. This would need Electron IPC.
      console.log('Dropped file:', markdownFile.name)
    }
  }, [])

  return (
    <div
      className={cn(
        "relative rounded-lg border-2 border-dashed p-8 transition-colors",
        isDragging ? "border-primary bg-primary/10" : "border-muted-foreground/25",
        currentFile && "border-solid border-primary/50 bg-primary/5",
        className
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="flex flex-col items-center justify-center space-y-4">
        {currentFile ? (
          <>
            <FileIcon className="h-12 w-12 text-primary" />
            <div className="text-center">
              <p className="text-sm font-medium">{currentFile.split('/').pop()}</p>
              <p className="text-xs text-muted-foreground">
                {useTeleprompterStore.getState().wordCount} words
              </p>
            </div>
            <Button variant="outline" size="sm" onClick={handleFileSelect}>
              Load Different File
            </Button>
          </>
        ) : (
          <>
            <UploadIcon className="h-12 w-12 text-muted-foreground" />
            <div className="text-center">
              <p className="text-sm font-medium">Drop a file here or click to browse</p>
              <p className="text-xs text-muted-foreground">
                Supports .md, .markdown, and .txt files
              </p>
            </div>
            <Button 
              variant="teleprompter" 
              onClick={handleFileSelect}
              disabled={isLoading}
            >
              {isLoading ? 'Loading...' : 'Select File'}
            </Button>
          </>
        )}
        
        {error && (
          <div className="mt-4 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
            {error}
          </div>
        )}
      </div>
    </div>
  )
}