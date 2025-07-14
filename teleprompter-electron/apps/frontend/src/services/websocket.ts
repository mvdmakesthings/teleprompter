import { EventEmitter } from 'events'

export type WebSocketEvent = 
  | { type: 'voice_activity'; data: { is_active: boolean; level: number } }
  | { type: 'file_changed'; data: { file_path: string; change_type: 'modified' | 'deleted' } }
  | { type: 'reading_metrics'; data: { words_per_minute: number; estimated_time: number } }
  | { type: 'error'; data: { message: string; code?: string } }

interface WebSocketOptions {
  url: string
  reconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
}

export class WebSocketClient extends EventEmitter {
  private ws: WebSocket | null = null
  private url: string
  private options: Required<WebSocketOptions>
  private reconnectAttempts = 0
  private reconnectTimer: NodeJS.Timeout | null = null
  private heartbeatTimer: NodeJS.Timeout | null = null
  private isClosing = false

  constructor(options: WebSocketOptions) {
    super()
    this.url = options.url
    this.options = {
      url: options.url,
      reconnect: options.reconnect ?? true,
      reconnectInterval: options.reconnectInterval ?? 1000,
      maxReconnectAttempts: options.maxReconnectAttempts ?? 10,
      heartbeatInterval: options.heartbeatInterval ?? 30000,
    }
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    this.isClosing = false
    
    try {
      this.ws = new WebSocket(this.url)
      
      this.ws.onopen = this.handleOpen.bind(this)
      this.ws.onmessage = this.handleMessage.bind(this)
      this.ws.onerror = this.handleError.bind(this)
      this.ws.onclose = this.handleClose.bind(this)
    } catch (error) {
      this.handleError(error as Event)
    }
  }

  disconnect(): void {
    this.isClosing = true
    this.cleanup()
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }
  }

  send(event: WebSocketEvent): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(event))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  private handleOpen(): void {
    console.log('WebSocket connected')
    this.emit('connected')
    this.reconnectAttempts = 0
    this.startHeartbeat()
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data) as WebSocketEvent
      this.emit(data.type, data.data)
      this.emit('message', data)
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error)
    this.emit('error', error)
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason)
    this.cleanup()
    this.emit('disconnected', event)
    
    if (!this.isClosing && this.options.reconnect && this.reconnectAttempts < this.options.maxReconnectAttempts) {
      this.scheduleReconnect()
    }
  }

  private scheduleReconnect(): void {
    const backoffDelay = Math.min(
      this.options.reconnectInterval * Math.pow(2, this.reconnectAttempts),
      30000 // Max 30 seconds
    )
    
    this.reconnectAttempts++
    console.log(`Reconnecting in ${backoffDelay}ms (attempt ${this.reconnectAttempts})`)
    
    this.reconnectTimer = setTimeout(() => {
      this.connect()
    }, backoffDelay)
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, this.options.heartbeatInterval)
  }

  private cleanup(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }
}

// Singleton instance
let wsClient: WebSocketClient | null = null
let wsClientPromise: Promise<WebSocketClient> | null = null

export function getWebSocketClient(url?: string): WebSocketClient {
  if (!wsClient && url) {
    // Prevent race condition by using a promise
    if (!wsClientPromise) {
      wsClientPromise = Promise.resolve(new WebSocketClient({ url }))
      wsClientPromise.then(client => {
        wsClient = client
        wsClientPromise = null
      })
    }
    
    // Return the existing client if available, otherwise create synchronously
    if (wsClient) {
      return wsClient
    }
    
    // Synchronous fallback for immediate use
    wsClient = new WebSocketClient({ url })
    wsClientPromise = null
  }
  
  if (!wsClient) {
    throw new Error('WebSocket client not initialized')
  }
  
  return wsClient
}

export function destroyWebSocketClient(): void {
  if (wsClient) {
    wsClient.disconnect()
    wsClient.removeAllListeners()
    wsClient = null
    wsClientPromise = null
  }
}