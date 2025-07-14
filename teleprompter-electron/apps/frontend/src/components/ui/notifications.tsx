'use client'

import { AnimatePresence, motion } from 'framer-motion'
import { X, Info, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'
import { useNotificationStore } from '@/store/notifications'
import { cn } from '@/lib/utils'

const iconMap = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  error: XCircle,
}

const colorMap = {
  info: 'bg-blue-500',
  success: 'bg-green-500',
  warning: 'bg-yellow-500',
  error: 'bg-red-500',
}

const borderColorMap = {
  info: 'border-blue-500',
  success: 'border-green-500',
  warning: 'border-yellow-500',
  error: 'border-red-500',
}

export function NotificationContainer() {
  const { notifications, removeNotification } = useNotificationStore()

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      <AnimatePresence>
        {notifications.map((notification) => {
          const Icon = iconMap[notification.type]
          
          return (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, x: 100, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.95 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="pointer-events-auto"
            >
              <div
                className={cn(
                  'relative flex items-start gap-3 p-4 pr-10',
                  'bg-background border rounded-lg shadow-lg',
                  'min-w-[300px] max-w-[500px]',
                  borderColorMap[notification.type]
                )}
              >
                <div className={cn('rounded-full p-1', colorMap[notification.type])}>
                  <Icon className="h-4 w-4 text-white" />
                </div>
                
                <div className="flex-1">
                  <h4 className="font-semibold text-sm text-foreground">
                    {notification.title}
                  </h4>
                  {notification.message && (
                    <p className="mt-1 text-sm text-muted-foreground">
                      {notification.message}
                    </p>
                  )}
                  
                  {notification.actions && notification.actions.length > 0 && (
                    <div className="mt-3 flex gap-2">
                      {notification.actions.map((action, index) => (
                        <button
                          key={index}
                          onClick={action.action}
                          className="text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                
                <button
                  onClick={() => removeNotification(notification.id)}
                  className="absolute top-3 right-3 text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}