export interface AudioProcessor {
  start(): Promise<void>
  stop(): void
  isRunning(): boolean
  getAudioLevel(): number
}

export interface VoiceControlOptions {
  sampleRate?: number
  frameSize?: number
  onVoiceActivity?: (isActive: boolean, level: number) => void
  onError?: (error: Error) => void
  onAudioData?: (data: Float32Array) => void  // Callback for raw audio data
  useBackendProcessing?: boolean  // Whether to use backend VAD processing
}

export class WebAudioProcessor implements AudioProcessor {
  private audioContext: AudioContext | null = null
  private analyser: AnalyserNode | null = null
  private microphone: MediaStreamAudioSourceNode | null = null
  private stream: MediaStream | null = null
  private processor: ScriptProcessorNode | null = null
  private running = false
  private audioLevel = 0
  private options: Required<VoiceControlOptions>
  private animationFrameId: number | null = null
  
  // Voice activity detection parameters
  private voiceThreshold = 0.02
  private voiceFrames = 0
  private silenceFrames = 0
  private readonly voiceFramesRequired = 3  // Frames needed to detect voice
  private readonly silenceFramesRequired = 10  // Frames needed to detect silence
  
  // Audio data buffering for backend processing
  private audioBuffer: Float32Array[] = []
  private readonly maxBufferSize = 10  // Max frames to buffer
  
  constructor(options: VoiceControlOptions = {}) {
    this.options = {
      sampleRate: options.sampleRate || 16000,
      frameSize: options.frameSize || 2048,
      onVoiceActivity: options.onVoiceActivity || (() => {}),
      onError: options.onError || (() => {}),
      onAudioData: options.onAudioData || (() => {}),
      useBackendProcessing: options.useBackendProcessing || false,
    }
  }
  
  async start(): Promise<void> {
    if (this.running) {
      return
    }
    
    try {
      // Request microphone access
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: this.options.sampleRate,
        }
      })
      
      // Create audio context
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: this.options.sampleRate,
      })
      
      // Create analyser node for level detection
      this.analyser = this.audioContext.createAnalyser()
      this.analyser.fftSize = 2048
      this.analyser.smoothingTimeConstant = 0.8
      
      // Create microphone source
      this.microphone = this.audioContext.createMediaStreamSource(this.stream)
      
      // Create script processor for real-time processing
      this.processor = this.audioContext.createScriptProcessor(
        this.options.frameSize,
        1,  // input channels
        1   // output channels
      )
      
      // Process audio data
      this.processor.onaudioprocess = (e) => {
        if (!this.running) return
        
        const inputData = e.inputBuffer.getChannelData(0)
        this.processAudioFrame(inputData)
      }
      
      // Connect nodes
      this.microphone.connect(this.analyser)
      this.microphone.connect(this.processor)
      this.processor.connect(this.audioContext.destination)
      
      this.running = true
      this.startLevelMonitoring()
      
    } catch (error) {
      this.handleError(error as Error)
      throw error
    }
  }
  
  stop(): void {
    this.running = false
    
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }
    
    if (this.processor) {
      this.processor.disconnect()
      this.processor = null
    }
    
    if (this.microphone) {
      this.microphone.disconnect()
      this.microphone = null
    }
    
    if (this.analyser) {
      this.analyser.disconnect()
      this.analyser = null
    }
    
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }
    
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
      this.stream = null
    }
    
    this.audioLevel = 0
    this.voiceFrames = 0
    this.silenceFrames = 0
    this.audioBuffer = []
  }
  
  isRunning(): boolean {
    return this.running
  }
  
  getAudioLevel(): number {
    return this.audioLevel
  }
  
  setVoiceThreshold(threshold: number): void {
    this.voiceThreshold = Math.max(0, Math.min(1, threshold))
  }
  
  private processAudioFrame(data: Float32Array): void {
    // Calculate RMS (Root Mean Square) for audio level
    let sum = 0
    for (let i = 0; i < data.length; i++) {
      sum += data[i] * data[i]
    }
    const rms = Math.sqrt(sum / data.length)
    this.audioLevel = Math.min(1, rms * 10)  // Scale for visibility
    
    // Send raw audio data to backend if enabled
    if (this.options.useBackendProcessing) {
      // Buffer audio frames to reduce network overhead
      this.audioBuffer.push(new Float32Array(data))
      
      // Send buffered data when we have enough frames
      if (this.audioBuffer.length >= 1) {  // Send immediately for real-time processing
        const combinedData = this.combineAudioBuffers()
        this.options.onAudioData(combinedData)
        this.audioBuffer = []
      }
    } else {
      // Local voice activity detection
      if (rms > this.voiceThreshold) {
        this.voiceFrames++
        this.silenceFrames = 0
        
        if (this.voiceFrames >= this.voiceFramesRequired) {
          this.options.onVoiceActivity(true, this.audioLevel)
        }
      } else {
        this.silenceFrames++
        this.voiceFrames = 0
        
        if (this.silenceFrames >= this.silenceFramesRequired) {
          this.options.onVoiceActivity(false, this.audioLevel)
        }
      }
    }
  }
  
  private startLevelMonitoring(): void {
    if (!this.analyser || !this.running) return
    
    const dataArray = new Uint8Array(this.analyser.frequencyBinCount)
    
    const monitor = () => {
      if (!this.running || !this.analyser) return
      
      this.analyser.getByteFrequencyData(dataArray)
      
      // Calculate average level from frequency data
      let sum = 0
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i]
      }
      const average = sum / dataArray.length
      
      // Update visual level (normalized to 0-1)
      const visualLevel = average / 255
      
      // Continue monitoring
      this.animationFrameId = requestAnimationFrame(monitor)
    }
    
    monitor()
  }
  
  private handleError(error: Error): void {
    console.error('Voice control error:', error)
    
    let userFriendlyMessage = 'Voice control error'
    
    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
      userFriendlyMessage = 'Microphone access denied. Please allow microphone access and try again.'
    } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
      userFriendlyMessage = 'No microphone found. Please connect a microphone and try again.'
    } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
      userFriendlyMessage = 'Microphone is already in use by another application.'
    } else if (error.name === 'OverconstrainedError' || error.name === 'ConstraintNotSatisfiedError') {
      userFriendlyMessage = 'Microphone does not support the required settings.'
    }
    
    this.options.onError(new Error(userFriendlyMessage))
  }
  
  private combineAudioBuffers(): Float32Array {
    // Calculate total length
    const totalLength = this.audioBuffer.reduce((sum, buf) => sum + buf.length, 0)
    const combined = new Float32Array(totalLength)
    
    // Copy all buffers into combined buffer
    let offset = 0
    for (const buffer of this.audioBuffer) {
      combined.set(buffer, offset)
      offset += buffer.length
    }
    
    return combined
  }
}

// Alternative processor using Web Audio API Worklet (modern approach)
export class AudioWorkletProcessor implements AudioProcessor {
  private audioContext: AudioContext | null = null
  private microphone: MediaStreamAudioSourceNode | null = null
  private stream: MediaStream | null = null
  private workletNode: AudioWorkletNode | null = null
  private running = false
  private audioLevel = 0
  private options: Required<VoiceControlOptions>
  
  constructor(options: VoiceControlOptions = {}) {
    this.options = {
      sampleRate: options.sampleRate || 16000,
      frameSize: options.frameSize || 2048,
      onVoiceActivity: options.onVoiceActivity || (() => {}),
      onError: options.onError || (() => {}),
      onAudioData: options.onAudioData || (() => {}),
      useBackendProcessing: options.useBackendProcessing || false,
    }
  }
  
  async start(): Promise<void> {
    if (this.running) return
    
    try {
      // Request microphone access
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: this.options.sampleRate,
        }
      })
      
      // Create audio context
      this.audioContext = new AudioContext({
        sampleRate: this.options.sampleRate,
      })
      
      // Try to use AudioWorklet if available
      if (this.audioContext.audioWorklet) {
        try {
          // Load the processor module
          await this.audioContext.audioWorklet.addModule('/audio-processor.js')
          
          // Create worklet node
          this.workletNode = new AudioWorkletNode(this.audioContext, 'voice-processor', {
            numberOfInputs: 1,
            numberOfOutputs: 0,
            processorOptions: {
              frameSize: this.options.frameSize,
              voiceThreshold: 0.02,
            }
          })
          
          // Handle messages from the worklet
          this.workletNode.port.onmessage = (event) => {
            if (event.data.type === 'voiceActivity') {
              this.audioLevel = event.data.level
              this.options.onVoiceActivity(event.data.isActive, event.data.level)
            }
          }
          
          // Create microphone source
          this.microphone = this.audioContext.createMediaStreamSource(this.stream)
          
          // Connect nodes
          this.microphone.connect(this.workletNode)
          
          this.running = true
          
        } catch (workletError) {
          console.warn('AudioWorklet not available, falling back to ScriptProcessor')
          // Fall back to WebAudioProcessor
          this.stop()
          throw new Error('AudioWorklet not supported')
        }
      } else {
        throw new Error('AudioWorklet not supported')
      }
      
    } catch (error) {
      this.handleError(error as Error)
      throw error
    }
  }
  
  stop(): void {
    this.running = false
    
    if (this.workletNode) {
      this.workletNode.disconnect()
      this.workletNode = null
    }
    
    if (this.microphone) {
      this.microphone.disconnect()
      this.microphone = null
    }
    
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }
    
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
      this.stream = null
    }
    
    this.audioLevel = 0
  }
  
  isRunning(): boolean {
    return this.running
  }
  
  getAudioLevel(): number {
    return this.audioLevel
  }
  
  private handleError(error: Error): void {
    console.error('Voice control error:', error)
    
    let userFriendlyMessage = 'Voice control error'
    
    if (error.name === 'NotAllowedError') {
      userFriendlyMessage = 'Microphone access denied. Please allow microphone access and try again.'
    } else if (error.name === 'NotFoundError') {
      userFriendlyMessage = 'No microphone found. Please connect a microphone and try again.'
    }
    
    this.options.onError(new Error(userFriendlyMessage))
  }
}

// Factory function to create the best available processor
export function createAudioProcessor(options?: VoiceControlOptions): AudioProcessor {
  // For now, use WebAudioProcessor as it's more compatible
  // In the future, we could detect AudioWorklet support and use that
  return new WebAudioProcessor(options)
}