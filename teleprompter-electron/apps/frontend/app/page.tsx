'use client'

import { useEffect, useState } from 'react'
import { Settings } from '@cuebird/shared'

export default function Home() {
  const [backendUrl, setBackendUrl] = useState<string>('')
  const [settings, setSettings] = useState<Settings | null>(null)
  const [status, setStatus] = useState<string>('Initializing...')

  useEffect(() => {
    // Check if running in Electron
    if (typeof window !== 'undefined' && window.electronAPI) {
      // Get backend URL from Electron
      window.electronAPI.getBackendUrl()
        .then(url => {
          setBackendUrl(url)
          setStatus('Connected to backend')
          return window.electronAPI.getSettings()
        })
        .then(settings => {
          setSettings(settings)
        })
        .catch(err => {
          setStatus(`Error: ${err.message}`)
        })
    } else {
      // Development mode - connect to local backend
      setBackendUrl('http://localhost:8000')
      setStatus('Development mode')
    }
  }, [])

  const testBackend = async () => {
    if (!backendUrl) return

    try {
      const response = await fetch(`${backendUrl}/health`)
      const data = await response.json()
      setStatus(`Backend health: ${data.status}`)
    } catch (err) {
      setStatus(`Backend error: ${err.message}`)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-8">CueBird Teleprompter</h1>
        
        <div className="mb-8">
          <p className="text-lg mb-2">Status: {status}</p>
          <p className="text-sm text-gray-400">Backend URL: {backendUrl || 'Not connected'}</p>
        </div>

        <button
          onClick={testBackend}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Test Backend Connection
        </button>

        {settings && (
          <div className="mt-8 text-left">
            <h2 className="text-2xl font-semibold mb-4">Current Settings</h2>
            <pre className="bg-gray-800 p-4 rounded">
              {JSON.stringify(settings, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </main>
  )
}