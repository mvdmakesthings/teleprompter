import { useCallback, useRef } from 'react'

export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): (...args: Parameters<T>) => void {
  const lastRunRef = useRef(0)
  const timeoutRef = useRef<NodeJS.Timeout>()

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now()
      const timeSinceLastRun = now - lastRunRef.current

      if (timeSinceLastRun >= delay) {
        lastRunRef.current = now
        callback(...args)
      } else {
        // Clear any existing timeout
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current)
        }

        // Schedule the next run
        timeoutRef.current = setTimeout(() => {
          lastRunRef.current = Date.now()
          callback(...args)
        }, delay - timeSinceLastRun)
      }
    },
    [callback, delay]
  )
}