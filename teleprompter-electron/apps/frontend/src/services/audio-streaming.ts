/**
 * Audio streaming service for sending audio data to the backend
 */

import { apiClient } from '@/lib/api-client'

export interface AudioStreamConfig {
  sampleRate: number
  frameSize: number
  frameDuration: number  // in milliseconds
}

export class AudioStreamingService {
  private ws: WebSocket | null = null
  private isStreaming = false
  private config: AudioStreamConfig
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  
  constructor(config: Partial<AudioStreamConfig> = {}) {
    this.config = {
      sampleRate: config.sampleRate || 16000,
      frameSize: config.frameSize || 2048,
      frameDuration: config.frameDuration || 30,  // 30ms frames for WebRTC VAD
    }
  }
  
  /**
   * Start streaming audio to the backend
   */
  async start(onVoiceActivity?: (isActive: boolean, level: number) => void): Promise<void> {
    if (this.isStreaming) {
      return
    }
    
    try {
      // Start voice detection on the backend
      await apiClient.post('/api/voice/detect', {
        action: 'start',
        sensitivity: 2,
      })
      
      // Establish WebSocket connection for audio streaming
      await this.connectWebSocket(onVoiceActivity)
      
      this.isStreaming = true
    } catch (error) {
      console.error('Failed to start audio streaming:', error)
      throw error
    }
  }
  
  /**
   * Stop streaming audio
   */
  async stop(): Promise<void> {
    if (!this.isStreaming) {
      return
    }
    
    this.isStreaming = false
    
    // Close WebSocket connection
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    // Stop voice detection on the backend
    try {
      await apiClient.post('/api/voice/detect', {
        action: 'stop',
      })
    } catch (error) {
      console.error('Failed to stop voice detection:', error)
    }
  }
  
  /**
   * Send audio data to the backend
   */
  sendAudioData(audioData: Float32Array): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return
    }
    
    // Convert Float32Array to Int16Array for WebRTC VAD compatibility
    const int16Data = this.float32ToInt16(audioData)
    
    // Send audio data as binary
    this.ws.send(int16Data.buffer)
  }
  
  /**
   * Update voice detection sensitivity
   */
  async setSensitivity(sensitivity: number): Promise<void> {
    try {
      await apiClient.post('/api/voice/detect', {
        action: 'update',
        sensitivity,
      })
    } catch (error) {
      console.error('Failed to update sensitivity:', error)
    }
  }
  
  private async connectWebSocket(onVoiceActivity?: (isActive: boolean, level: number) => void): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = apiClient.getWebSocketUrl('/ws/audio')
      this.ws = new WebSocket(wsUrl)
      
      this.ws.binaryType = 'arraybuffer'
      
      this.ws.onopen = () => {
        console.log('Audio WebSocket connected')
        this.reconnectAttempts = 0
        
        // Send initial configuration
        this.ws!.send(JSON.stringify({
          type: 'config',
          sampleRate: this.config.sampleRate,
          frameSize: this.config.frameSize,
          frameDuration: this.config.frameDuration,
        }))
        
        resolve()
      }
      
      this.ws.onmessage = (event) => {
        try {
          // Handle text messages (voice activity updates)
          if (typeof event.data === 'string') {
            const data = JSON.parse(event.data)
            
            if (data.type === 'voice_activity' && onVoiceActivity) {
              onVoiceActivity(data.is_active, data.audio_level)
            }
          }
        } catch (error) {
          console.error('Error processing WebSocket message:', error)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('Audio WebSocket error:', error)
        reject(error)
      }
      
      this.ws.onclose = () => {
        console.log('Audio WebSocket closed')
        
        // Attempt to reconnect if still streaming
        if (this.isStreaming && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
          
          setTimeout(() => {
            this.connectWebSocket(onVoiceActivity).catch(console.error)
          }, this.reconnectDelay * this.reconnectAttempts)
        }
      }
    })
  }
  
  /**
   * Convert Float32Array to Int16Array
   */
  private float32ToInt16(float32Array: Float32Array): Int16Array {
    const int16Array = new Int16Array(float32Array.length)
    
    for (let i = 0; i < float32Array.length; i++) {
      // Clamp to [-1, 1] range
      const clamped = Math.max(-1, Math.min(1, float32Array[i]))
      // Convert to 16-bit integer
      int16Array[i] = Math.round(clamped * 32767)
    }
    
    return int16Array
  }
}

// Singleton instance
let audioStreamingService: AudioStreamingService | null = null

export function getAudioStreamingService(): AudioStreamingService {
  if (!audioStreamingService) {
    audioStreamingService = new AudioStreamingService()
  }
  return audioStreamingService
}