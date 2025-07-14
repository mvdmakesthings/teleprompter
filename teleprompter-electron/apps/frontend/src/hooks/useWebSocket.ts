'use client'

import { useEffect, useRef, useState } from 'react'
import { getWebSocketClient, destroyWebSocketClient, WebSocketClient, WebSocketEvent } from '@/services/websocket'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useAppStore } from '@/store/app'

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const wsRef = useRef<WebSocketClient | null>(null)
  
  const { backendUrl } = useAppStore()
  const { 
    setIsVoiceActive,
    currentFile,
    loadContent,
  } = useTeleprompterStore()

  // Create stable callbacks
  const setIsVoiceActiveStable = useRef(setIsVoiceActive)
  const loadContentStable = useRef(loadContent)
  
  useEffect(() => {
    setIsVoiceActiveStable.current = setIsVoiceActive
    loadContentStable.current = loadContent
  }, [setIsVoiceActive, loadContent])

  useEffect(() => {
    if (!backendUrl) return

    let isMounted = true
    
    // Convert HTTP URL to WebSocket URL
    const wsUrl = backendUrl.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws'
    
    try {
      const ws = getWebSocketClient(wsUrl)
      wsRef.current = ws
      
      // Connection handlers
      const handleConnected = () => {
        if (isMounted) {
          setIsConnected(true)
          setConnectionError(null)
          console.log('WebSocket connected')
        }
      }
      
      const handleDisconnected = () => {
        if (isMounted) {
          setIsConnected(false)
          console.log('WebSocket disconnected')
        }
      }
      
      const handleError = (error: any) => {
        if (isMounted) {
          console.error('WebSocket error:', error)
          setConnectionError('WebSocket connection error')
        }
      }
      
      const handleVoiceActivity = (data: { is_active: boolean; level: number }) => {
        if (isMounted) {
          setIsVoiceActiveStable.current(data.is_active)
        }
      }
      
      const handleFileChanged = async (data: { file_path: string; change_type: string }) => {
        if (!isMounted) return
        
        const currentFileSnapshot = useTeleprompterStore.getState().currentFile
        if (data.file_path === currentFileSnapshot && data.change_type === 'modified') {
          // Reload the file
          try {
            const apiClient = useAppStore.getState().apiClient
            if (apiClient && isMounted) {
              const response = await apiClient.post('/api/content/load', {
                file_path: data.file_path
              })
              
              if (response.data.success && isMounted) {
                loadContentStable.current({
                  content: response.data.parsed_content,
                  rawContent: response.data.content,
                  filePath: data.file_path,
                  wordCount: response.data.word_count,
                  sections: response.data.sections,
                })
                
                // Show notification
                console.log('File reloaded due to changes')
              }
            }
          } catch (error) {
            console.error('Failed to reload file:', error)
          }
        }
      }
      
      const handleReadingMetrics = (data: { words_per_minute: number; estimated_time: number }) => {
        if (isMounted) {
          // Could update a metrics store here if needed
          console.log('Reading metrics:', data)
        }
      }
      
      // Add event listeners
      ws.on('connected', handleConnected)
      ws.on('disconnected', handleDisconnected)
      ws.on('error', handleError)
      ws.on('voice_activity', handleVoiceActivity)
      ws.on('file_changed', handleFileChanged)
      ws.on('reading_metrics', handleReadingMetrics)
      
      // Connect
      ws.connect()
      
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error)
      if (isMounted) {
        setConnectionError('Failed to initialize WebSocket')
      }
    }
    
    return () => {
      isMounted = false
      
      if (wsRef.current) {
        wsRef.current.disconnect()
        wsRef.current.removeAllListeners()
      }
      destroyWebSocketClient()
    }
  }, [backendUrl]) // Only depend on backendUrl

  const sendMessage = (event: WebSocketEvent) => {
    if (wsRef.current?.isConnected) {
      wsRef.current.send(event)
    } else {
      console.warn('Cannot send message: WebSocket not connected')
    }
  }

  return {
    isConnected,
    connectionError,
    sendMessage,
  }
}