import type { IpcApi } from '@cuebird/ipc'
import type { Settings } from '@cuebird/shared'

declare global {
  interface Window {
    electronAPI: IpcApi
    __CUEBIRD_INIT__?: {
      backendUrl: string
      settings: Settings
    }
  }
}

export {}