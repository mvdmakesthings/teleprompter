/**
 * Type declarations for the IPC API exposed via contextBridge
 */

import { IpcApi } from './types'

declare global {
  interface Window {
    electronAPI: IpcApi
  }
}