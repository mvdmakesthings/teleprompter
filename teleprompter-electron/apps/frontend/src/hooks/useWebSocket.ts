'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { getWebSocketClient, destroyWebSocketClient, WebSocketClient, WebSocketEvent } from '@/services/websocket'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useAppStore } from '@/store/app'
import { useNotificationStore } from '@/store/notifications'
import { useSettingsStore } from '@/store/settings'

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const wsRef = useRef<WebSocketClient | null>(null)
  const fileReloadTimerRef = useRef<NodeJS.Timeout | null>(null)
  const lastReloadTimeRef = useRef<number>(0)

  const { backendUrl } = useAppStore()
  const {
    setIsVoiceActive,
    currentFile,
    loadContent,
    scrollPosition,
    isPlaying,
    setScrollPosition,
    setIsPlaying,
  } = useTeleprompterStore()
  const { addNotification } = useNotificationStore()
  const { autoReload, fileWatchDebounce = 500 } = useSettingsStore()

  // Create stable callbacks
  const setIsVoiceActiveStable = useRef(setIsVoiceActive)
  const loadContentStable = useRef(loadContent)
  const addNotificationStable = useRef(addNotification)
  const setScrollPositionStable = useRef(setScrollPosition)
  const setIsPlayingStable = useRef(setIsPlaying)

  useEffect(() => {
    setIsVoiceActiveStable.current = setIsVoiceActive
    loadContentStable.current = loadContent
    addNotificationStable.current = addNotification
    setScrollPositionStable.current = setScrollPosition
    setIsPlayingStable.current = setIsPlaying
  }, [setIsVoiceActive, loadContent, addNotification, setScrollPosition, setIsPlaying])

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

        const state = useTeleprompterStore.getState()
        const currentFileSnapshot = state.currentFile
        const settings = useSettingsStore.getState()

        // Check if this is the current file and if auto-reload is enabled
        if (data.file_path !== currentFileSnapshot) return

        // Clear any existing reload timer
        if (fileReloadTimerRef.current) {
          clearTimeout(fileReloadTimerRef.current)
        }

        // Check if we're within the debounce window
        const now = Date.now()
        if (now - lastReloadTimeRef.current < fileWatchDebounce) {
          // Debounce the reload
          fileReloadTimerRef.current = setTimeout(() => {
            handleFileChanged(data)
          }, fileWatchDebounce)
          return
        }

        if (data.change_type === 'modified') {
          const notificationLevel = settings.fileWatchNotifications

          if (!settings.autoReload) {
            // Show notification with reload action if notifications are enabled
            if (notificationLevel !== 'none') {
              addNotificationStable.current({
                type: 'info',
                title: 'File Changed',
                message: notificationLevel === 'verbose'
                  ? `The file "${data.file_path.split('/').pop()}" has been modified. Click reload to update.`
                  : 'The file has been modified. Click reload to update.',
                duration: undefined, // Permanent notification
                actions: [{
                  label: 'Reload',
                  action: async () => {
                    await reloadFile(data.file_path)
                  }
                }]
              })
            }
            return
          }

          // Auto-reload is enabled
          await reloadFile(data.file_path)
        } else if (data.change_type === 'deleted') {
          // File was deleted
          const notificationLevel = settings.fileWatchNotifications
          if (notificationLevel !== 'none') {
            addNotificationStable.current({
              type: 'error',
              title: 'File Deleted',
              message: notificationLevel === 'verbose'
                ? `The file "${data.file_path.split('/').pop()}" has been deleted or moved.`
                : 'The file has been deleted or moved.',
              duration: undefined,
            })
          }
        }
      }

      const reloadFile = async (filePath: string) => {
        if (!isMounted) return

        // Store current state for restoration
        const state = useTeleprompterStore.getState()
        const currentScrollPosition = state.scrollPosition
        const wasPlaying = state.isPlaying

        // Pause if playing
        if (wasPlaying) {
          setIsPlayingStable.current(false)
        }

        try {
          const apiClient = useAppStore.getState().apiClient
          if (apiClient && isMounted) {
            // First, load the file content
            const loadResponse = await apiClient.post('/api/content/load', {
              file_path: filePath
            })

            if (loadResponse.data && isMounted) {
              // Parse the content
              const parseResponse = await apiClient.post('/api/content/parse', {
                content: loadResponse.data.content
              })

              if (parseResponse.data && isMounted) {
                // Load the new content
                loadContentStable.current({
                  content: parseResponse.data.html,
                  rawContent: loadResponse.data.content,
                  filePath: filePath,
                  wordCount: parseResponse.data.word_count,
                  sections: parseResponse.data.sections,
                })

                // Restore scroll position (with a small delay to ensure content is rendered)
                setTimeout(() => {
                  if (isMounted) {
                    setScrollPositionStable.current(currentScrollPosition)

                    // Resume playing if it was playing before
                    if (wasPlaying) {
                      setIsPlayingStable.current(true)
                    }
                  }
                }, 100)

                // Update last reload time
                lastReloadTimeRef.current = Date.now()

                // Show success notification based on notification level
                const notificationLevel = useSettingsStore.getState().fileWatchNotifications
                if (notificationLevel !== 'none') {
                  addNotificationStable.current({
                    type: 'success',
                    title: 'File Reloaded',
                    message: notificationLevel === 'verbose'
                      ? `The file "${filePath.split('/').pop()}" has been updated with the latest changes.`
                      : 'The file has been updated with the latest changes.',
                    duration: 3000,
                  })
                }
              }
            }
          }
        } catch (error) {
          console.error('Failed to reload file:', error)
          const notificationLevel = useSettingsStore.getState().fileWatchNotifications
          if (notificationLevel !== 'none') {
            addNotificationStable.current({
              type: 'error',
              title: 'Reload Failed',
              message: notificationLevel === 'verbose'
                ? `Failed to reload the file "${filePath.split('/').pop()}". Error: ${error instanceof Error ? error.message : 'Unknown error'}`
                : 'Failed to reload the file. Please try again.',
            })
          }

          // Resume playing if it was playing before
          if (wasPlaying && isMounted) {
            setIsPlayingStable.current(true)
          }
        }
      }

      const handleReadingMetrics = (data: { words_per_minute: number; estimated_time: number }) => {
        if (isMounted) {
          // Could update a metrics store here if needed
          console.log('Reading metrics:', data)
        }
      }

      // Handle other file events
      const handleFileRemoved = (data: { file_path: string }) => {
        if (!isMounted) return

        const currentFileSnapshot = useTeleprompterStore.getState().currentFile
        if (data.file_path === currentFileSnapshot) {
          handleFileChanged({ file_path: data.file_path, change_type: 'deleted' })
        }
      }

      const handleFileWatchError = (data: { file_path: string; error: string }) => {
        if (!isMounted) return

        const currentFileSnapshot = useTeleprompterStore.getState().currentFile
        const notificationLevel = useSettingsStore.getState().fileWatchNotifications

        if (data.file_path === currentFileSnapshot && notificationLevel !== 'none') {
          addNotificationStable.current({
            type: 'error',
            title: 'File Watch Error',
            message: notificationLevel === 'verbose'
              ? `Error watching "${data.file_path.split('/').pop()}": ${data.error || 'Unknown error'}`
              : data.error || 'An error occurred while watching the file.',
          })
        }
      }

      // Add event listeners
      ws.on('connected', handleConnected)
      ws.on('disconnected', handleDisconnected)
      ws.on('error', handleError)
      ws.on('voice_activity', handleVoiceActivity)
      ws.on('file_changed', handleFileChanged)
      ws.on('file_removed', handleFileRemoved)
      ws.on('file_watch_error', handleFileWatchError)
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

      // Clear any pending reload timer
      if (fileReloadTimerRef.current) {
        clearTimeout(fileReloadTimerRef.current)
      }

      if (wsRef.current) {
        wsRef.current.disconnect()
        wsRef.current.removeAllListeners()
      }
      destroyWebSocketClient()
    }
  }, [backendUrl]) // Only depend on backendUrl

  const sendMessage = useCallback((event: WebSocketEvent) => {
    if (wsRef.current?.isConnected) {
      wsRef.current.send(event)
    } else {
      console.warn('Cannot send message: WebSocket not connected')
    }
  }, [])

  return {
    isConnected,
    connectionError,
    sendMessage,
  }
}