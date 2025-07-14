import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AppProvider } from '@/components/providers/app-provider'
import { WebSocketProvider } from '@/components/providers/websocket-provider'
import { NotificationContainer } from '@/components/ui/notifications'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CueBird Teleprompter',
  description: 'Professional-grade teleprompter application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppProvider>
          <WebSocketProvider>
            {children}
            <NotificationContainer />
          </WebSocketProvider>
        </AppProvider>
      </body>
    </html>
  )
}