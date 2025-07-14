'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { createAudioProcessor, AudioProcessor } from '@/services/voice-control'
import { getAudioStreamingService } from '@/services/audio-streaming'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useWebSocketContext } from '@/components/providers/websocket-provider'

export interface UseVoiceControlOptions {
  autoPauseEnabled?: boolean
  autoResumeEnabled?: boolean
  debounceMs?: number
  useBackendProcessing?: boolean  // Use backend VAD instead of frontend
}

export function useVoiceControl(options: UseVoiceControlOptions = {}) {
  const {
    autoPauseEnabled = true,
    autoResumeEnabled = true,
    debounceMs = 500,
    useBackendProcessing = false,  // Default to frontend processing for now
  } = options

  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [audioLevel, setAudioLevel] = useState(0)
  const [permissionState, setPermissionState] = useState<PermissionState>('prompt')
  
  const processorRef = useRef<AudioProcessor | null>(null)
  const audioStreamingRef = useRef(getAudioStreamingService())
  const lastVoiceStateRef = useRef(false)
  const pauseTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const resumeTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  
  const { sendMessage } = useWebSocketContext()
  const {
    voiceEnabled,
    setVoiceEnabled,
    setIsVoiceActive,
    isPlaying,
    setIsPlaying,
    voiceSensitivity,
    voiceThreshold,
  } = useTeleprompterStore()

  // Check microphone permission status
  useEffect(() => {
    if ('permissions' in navigator) {
      navigator.permissions.query({ name: 'microphone' as PermissionName })
        .then(result => {
          setPermissionState(result.state)
          result.addEventListener('change', () => {
            setPermissionState(result.state)
          })
        })
        .catch(() => {
          // Permissions API might not be available
          console.warn('Permissions API not available')
        })
    }
  }, [])

  // Handle voice activity
  const handleVoiceActivity = useCallback((isActive: boolean, level: number) => {
    setAudioLevel(level)
    setIsVoiceActive(isActive)
    
    // Only send to backend if using frontend processing
    // (backend processing sends its own updates)
    if (!useBackendProcessing) {
      sendMessage({
        type: 'voice_activity',
        data: { is_active: isActive, level }
      })
    }
    
    // Handle auto pause/resume
    if (isActive !== lastVoiceStateRef.current) {
      lastVoiceStateRef.current = isActive
      
      if (isActive) {
        // Voice detected - clear pause timeout and maybe resume
        if (pauseTimeoutRef.current) {
          clearTimeout(pauseTimeoutRef.current)
          pauseTimeoutRef.current = null
        }
        
        if (autoResumeEnabled && !isPlaying) {
          // Debounce resume to avoid flickering
          if (resumeTimeoutRef.current) {
            clearTimeout(resumeTimeoutRef.current)
          }
          
          resumeTimeoutRef.current = setTimeout(() => {
            setIsPlaying(true)
            resumeTimeoutRef.current = null
          }, debounceMs)
        }
      } else {
        // Voice stopped - clear resume timeout and maybe pause
        if (resumeTimeoutRef.current) {
          clearTimeout(resumeTimeoutRef.current)
          resumeTimeoutRef.current = null
        }
        
        if (autoPauseEnabled && isPlaying) {
          // Debounce pause to avoid flickering
          if (pauseTimeoutRef.current) {
            clearTimeout(pauseTimeoutRef.current)
          }
          
          pauseTimeoutRef.current = setTimeout(() => {
            setIsPlaying(false)
            pauseTimeoutRef.current = null
          }, debounceMs)
        }
      }
    }
  }, [
    isPlaying,
    setIsPlaying,
    setIsVoiceActive,
    sendMessage,
    autoPauseEnabled,
    autoResumeEnabled,
    debounceMs,
    useBackendProcessing
  ])

  // Handle errors
  const handleError = useCallback((error: Error) => {
    console.error('Voice control error:', error)
    setError(error.message)
    setIsProcessing(false)
    setVoiceEnabled(false)
  }, [setVoiceEnabled])
  
  // Handle audio data for backend processing
  const handleAudioData = useCallback((data: Float32Array) => {
    if (useBackendProcessing && audioStreamingRef.current) {
      audioStreamingRef.current.sendAudioData(data)
    }
  }, [useBackendProcessing])

  // Start voice processing
  const startVoiceProcessing = useCallback(async () => {
    if (processorRef.current?.isRunning()) {
      return
    }
    
    setError(null)
    setIsProcessing(true)
    
    try {
      // Start backend streaming if enabled
      if (useBackendProcessing) {
        await audioStreamingRef.current.start(handleVoiceActivity)
      }
      
      if (!processorRef.current) {
        processorRef.current = createAudioProcessor({
          onVoiceActivity: handleVoiceActivity,
          onError: handleError,
          onAudioData: handleAudioData,
          useBackendProcessing,
        })
      }
      
      await processorRef.current.start()
      
      // Update threshold based on sensitivity
      if (processorRef.current && 'setVoiceThreshold' in processorRef.current) {
        const threshold = mapSensitivityToThreshold(voiceSensitivity)
        ;(processorRef.current as any).setVoiceThreshold(threshold)
      }
      
      setIsProcessing(true)
      setError(null)
      
      // Notify backend
      sendMessage({
        type: 'voice_activity',
        data: { is_active: false, level: 0 }
      })
      
    } catch (err) {
      handleError(err as Error)
      processorRef.current = null
    }
  }, [handleVoiceActivity, handleError, handleAudioData, voiceSensitivity, sendMessage, useBackendProcessing])

  // Stop voice processing
  const stopVoiceProcessing = useCallback(async () => {
    if (processorRef.current) {
      processorRef.current.stop()
      processorRef.current = null
    }
    
    // Stop backend streaming if enabled
    if (useBackendProcessing) {
      await audioStreamingRef.current.stop()
    }
    
    // Clear any pending timeouts
    if (pauseTimeoutRef.current) {
      clearTimeout(pauseTimeoutRef.current)
      pauseTimeoutRef.current = null
    }
    if (resumeTimeoutRef.current) {
      clearTimeout(resumeTimeoutRef.current)
      resumeTimeoutRef.current = null
    }
    
    setIsProcessing(false)
    setAudioLevel(0)
    setIsVoiceActive(false)
    lastVoiceStateRef.current = false
    
    // Notify backend
    sendMessage({
      type: 'voice_activity',
      data: { is_active: false, level: 0 }
    })
  }, [setIsVoiceActive, sendMessage, useBackendProcessing])

  // Toggle voice control
  const toggleVoiceControl = useCallback(async () => {
    if (voiceEnabled) {
      stopVoiceProcessing()
      setVoiceEnabled(false)
    } else {
      setVoiceEnabled(true)
      await startVoiceProcessing()
    }
  }, [voiceEnabled, setVoiceEnabled, startVoiceProcessing, stopVoiceProcessing])

  // Effect to handle voice enabled state changes
  useEffect(() => {
    if (voiceEnabled && !processorRef.current?.isRunning()) {
      startVoiceProcessing()
    } else if (!voiceEnabled && processorRef.current?.isRunning()) {
      stopVoiceProcessing()
    }
  }, [voiceEnabled, startVoiceProcessing, stopVoiceProcessing])

  // Update voice threshold when sensitivity changes
  useEffect(() => {
    if (processorRef.current && 'setVoiceThreshold' in processorRef.current) {
      const threshold = mapSensitivityToThreshold(voiceSensitivity)
      ;(processorRef.current as any).setVoiceThreshold(threshold)
    }
    
    // Update backend sensitivity if using backend processing
    if (useBackendProcessing && audioStreamingRef.current) {
      audioStreamingRef.current.setSensitivity(voiceSensitivity)
    }
  }, [voiceSensitivity, useBackendProcessing])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopVoiceProcessing()
    }
  }, [stopVoiceProcessing])

  // Request microphone permission
  const requestPermission = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach(track => track.stop())
      setPermissionState('granted')
      return true
    } catch (error) {
      if ((error as Error).name === 'NotAllowedError') {
        setPermissionState('denied')
      }
      return false
    }
  }, [])

  return {
    isProcessing,
    error,
    audioLevel,
    permissionState,
    toggleVoiceControl,
    startVoiceProcessing,
    stopVoiceProcessing,
    requestPermission,
  }
}

// Helper function to map sensitivity (0-3) to threshold (0-1)
function mapSensitivityToThreshold(sensitivity: number): number {
  // Higher sensitivity = lower threshold
  const thresholds = [0.05, 0.03, 0.02, 0.01]
  return thresholds[Math.min(Math.max(0, sensitivity), 3)]
}