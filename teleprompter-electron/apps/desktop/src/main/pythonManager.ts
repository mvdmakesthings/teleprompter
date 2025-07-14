import { ChildProcess, spawn } from 'child_process'
import { app } from 'electron'
import * as path from 'path'
import * as net from 'net'
import { BackendStatus } from '@cuebird/ipc'

export class PythonManager {
  private static instance: PythonManager
  private pythonProcess: ChildProcess | null = null
  private port: number = 0
  private status: BackendStatus = { running: false }
  private startPromise: Promise<void> | null = null

  private constructor() { }

  static getInstance(): PythonManager {
    if (!PythonManager.instance) {
      PythonManager.instance = new PythonManager()
    }
    return PythonManager.instance
  }

  async start(): Promise<void> {
    // Prevent multiple start attempts
    if (this.startPromise) {
      return this.startPromise
    }

    this.startPromise = this.startBackend()
    return this.startPromise
  }

  private async startBackend(): Promise<void> {
    try {
      // Find available port
      this.port = await this.getAvailablePort()

      // Path to Python backend
      const pythonPath = this.getPythonPath()

      // Spawn Python process
      const args = app.isPackaged
        ? ['--port', this.port.toString(), '--host', '127.0.0.1']
        : ['-m', 'teleprompter.backend.main', '--port', this.port.toString(), '--host', '127.0.0.1']

      this.pythonProcess = spawn(pythonPath, args, {
        env: {
          ...process.env,
          PYTHONUNBUFFERED: '1', // Ensure real-time output
        },
        cwd: app.isPackaged ? undefined : path.join(__dirname, '../../../../../') // Project root in dev
      })

      // Handle process events
      this.setupProcessHandlers()

      // Wait for server to be ready
      await this.waitForServer()

      this.status = {
        running: true,
        port: this.port,
        pid: this.pythonProcess.pid
      }

      console.log(`Python backend started on port ${this.port}`)
    } catch (error) {
      this.status = {
        running: false,
        error: (error as Error).message
      }
      throw error
    }
  }

  private setupProcessHandlers() {
    if (!this.pythonProcess) return

    this.pythonProcess.stdout?.on('data', (data) => {
      console.log(`[Backend]: ${data.toString()}`)
    })

    this.pythonProcess.stderr?.on('data', (data) => {
      console.error(`[Backend Error]: ${data.toString()}`)
    })

    this.pythonProcess.on('error', (error) => {
      console.error('Failed to start Python backend:', error)
      this.status = {
        running: false,
        error: error.message
      }
    })

    this.pythonProcess.on('exit', (code, signal) => {
      console.log(`Python backend exited with code ${code}, signal ${signal}`)
      this.status = {
        running: false,
        error: code !== 0 ? `Process exited with code ${code}` : undefined
      }
      this.pythonProcess = null
      this.port = 0
    })
  }

  private getPythonPath(): string {
    if (app.isPackaged) {
      // Production: Use bundled Python
      const platform = process.platform
      const executable = platform === 'win32' ? 'teleprompter-backend.exe' : 'teleprompter-backend'
      return path.join(process.resourcesPath, 'python', executable)
    } else {
      // Development: Use Python module directly
      return process.platform === 'win32' ? 'python' : 'python3'
    }
  }

  private async getAvailablePort(): Promise<number> {
    return new Promise((resolve, reject) => {
      const server = net.createServer()
      server.listen(0, '127.0.0.1', () => {
        const address = server.address()
        if (address && typeof address !== 'string') {
          const port = address.port
          server.close(() => resolve(port))
        } else {
          reject(new Error('Failed to get port'))
        }
      })
      server.on('error', reject)
    })
  }

  private async waitForServer(maxAttempts = 30, delay = 1000): Promise<void> {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const response = await this.checkHealth()
        if (response) {
          return
        }
      } catch (error) {
        // Server not ready yet
      }
      await new Promise(resolve => setTimeout(resolve, delay))
    }
    throw new Error('Backend server failed to start within timeout')
  }

  private async checkHealth(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      const req = net.connect(this.port, '127.0.0.1', () => {
        req.end()
        resolve(true)
      })
      req.on('error', () => reject(false))
      req.setTimeout(1000, () => {
        req.destroy()
        reject(false)
      })
    })
  }

  async stop(): Promise<void> {
    if (this.pythonProcess) {
      return new Promise((resolve) => {
        const cleanup = () => {
          this.pythonProcess = null
          this.port = 0
          this.status = { running: false }
          resolve()
        }

        if (!this.pythonProcess || this.pythonProcess.killed) {
          cleanup()
          return
        }

        this.pythonProcess.once('exit', cleanup)

        // Try graceful shutdown first
        this.pythonProcess.kill('SIGTERM')

        // Force kill after timeout
        setTimeout(() => {
          if (this.pythonProcess && !this.pythonProcess.killed) {
            this.pythonProcess.kill('SIGKILL')
          }
        }, 5000)
      })
    }
  }

  getStatus(): BackendStatus {
    return { ...this.status }
  }

  getApiUrl(): string {
    if (!this.status.running || !this.port) {
      throw new Error('Backend is not running')
    }
    return `http://127.0.0.1:${this.port}`
  }

  isRunning(): boolean {
    return this.status.running
  }
}