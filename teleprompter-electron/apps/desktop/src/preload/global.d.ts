import { Settings } from '@cuebird/shared'

declare global {
  interface Window {
    __CUEBIRD_INIT__?: {
      backendUrl: string
      settings: Settings
    }
  }
}

export {}