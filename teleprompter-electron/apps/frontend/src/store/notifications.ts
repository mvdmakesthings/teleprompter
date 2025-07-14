import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

export type NotificationType = 'info' | 'success' | 'warning' | 'error'

export interface Notification {
  id: string
  type: NotificationType
  title: string
  message?: string
  duration?: number // Duration in milliseconds, null for permanent
  timestamp: number
  actions?: Array<{
    label: string
    action: () => void
  }>
}

interface NotificationState {
  notifications: Notification[]
  
  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => string
  removeNotification: (id: string) => void
  clearAll: () => void
  
  // Convenience methods
  info: (title: string, message?: string, duration?: number) => string
  success: (title: string, message?: string, duration?: number) => string
  warning: (title: string, message?: string, duration?: number) => string
  error: (title: string, message?: string, duration?: number) => string
}

const DEFAULT_DURATION = 5000 // 5 seconds

export const useNotificationStore = create<NotificationState>()(
  devtools(
    (set, get) => ({
      notifications: [],
      
      addNotification: (notification) => {
        const id = `notification-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
        const newNotification: Notification = {
          ...notification,
          id,
          timestamp: Date.now(),
          duration: notification.duration ?? DEFAULT_DURATION,
        }
        
        set((state) => ({
          notifications: [...state.notifications, newNotification]
        }))
        
        // Auto-remove after duration (if not permanent)
        if (newNotification.duration && newNotification.duration > 0) {
          setTimeout(() => {
            get().removeNotification(id)
          }, newNotification.duration)
        }
        
        return id
      },
      
      removeNotification: (id) => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id)
        }))
      },
      
      clearAll: () => {
        set({ notifications: [] })
      },
      
      // Convenience methods
      info: (title, message, duration) => {
        return get().addNotification({
          type: 'info',
          title,
          message,
          duration,
        })
      },
      
      success: (title, message, duration) => {
        return get().addNotification({
          type: 'success',
          title,
          message,
          duration,
        })
      },
      
      warning: (title, message, duration) => {
        return get().addNotification({
          type: 'warning',
          title,
          message,
          duration,
        })
      },
      
      error: (title, message, duration) => {
        return get().addNotification({
          type: 'error',
          title,
          message,
          duration: duration ?? 10000, // Errors stay longer by default
        })
      },
    }),
    {
      name: 'notification-store',
    }
  )
)