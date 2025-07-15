import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import {
  ScrollState,
  ContentInfo,
  FileInfo,
  VoiceActivity,
  ReadingMetrics,
  DEFAULT_WORDS_PER_MINUTE
} from '@cuebird/shared'
import { apiClient } from '@/lib/api-client'

interface TeleprompterState {
  // Content state
  content: {
    html: string
    markdown: string
    info: ContentInfo | null
    file: FileInfo | null
  }

  // Scroll state
  scroll: ScrollState

  // Voice state
  voice: VoiceActivity

  // Reading metrics
  metrics: ReadingMetrics | null

  // Actions
  loadFile: (filePath: string) => Promise<void>
  loadMarkdown: (markdown: string) => Promise<void>
  setScrollPosition: (position: number) => void
  setScrollSpeed: (speed: number) => void
  togglePlayPause: () => void
  updateVoiceActivity: (activity: VoiceActivity) => void
  calculateMetrics: () => void
  reset: () => void
}

const initialState = {
  content: {
    html: '',
    markdown: '',
    info: null,
    file: null,
  },
  scroll: {
    position: 0,
    speed: 1.0,
    isPlaying: false,
    progress: 0,
  },
  voice: {
    state: 'inactive' as const,
    isSpeaking: false,
    audioLevel: 0,
    sensitivity: 1,
    timestamp: new Date(),
  },
  metrics: null,
}

export const useTeleprompterStore = create<TeleprompterState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Load file
      loadFile: async (filePath: string) => {
        try {
          const response = await apiClient.loadContent({ filePath })

          set({
            content: {
              html: response.html,
              markdown: response.markdown,
              info: response.contentInfo,
              file: response.fileInfo,
            },
            scroll: { ...initialState.scroll },
            metrics: null,
          })

          // Calculate initial metrics
          get().calculateMetrics()
        } catch (error) {
          console.error('Failed to load file:', error)
          throw error
        }
      },

      // Load markdown directly
      loadMarkdown: async (markdown: string) => {
        try {
          const response = await apiClient.parseContent({
            content: markdown,
            format: 'markdown'
          })

          set({
            content: {
              html: response.html,
              markdown,
              info: response.contentInfo,
              file: null,
            },
            scroll: { ...initialState.scroll },
            metrics: null,
          })

          // Calculate initial metrics
          get().calculateMetrics()
        } catch (error) {
          console.error('Failed to parse markdown:', error)
          throw error
        }
      },

      // Update scroll position
      setScrollPosition: (position: number) => {
        const { content, scroll } = get()
        const progress = Math.max(0, Math.min(1, position))

        // Only update if position actually changed
        if (scroll.position === position) return

        // Calculate metrics inline to avoid triggering another store update
        let newMetrics = null
        if (content.info) {
          const wordCount = content.info.wordCount
          const wpm = DEFAULT_WORDS_PER_MINUTE * scroll.speed
          const totalTime = (wordCount / wpm) * 60 // in seconds
          const elapsedTime = totalTime * progress
          const remainingTime = totalTime - elapsedTime

          newMetrics = {
            wordsPerMinute: wpm,
            elapsedTime,
            remainingTime,
            totalTime,
          }
        }

        set(state => ({
          scroll: {
            ...state.scroll,
            position,
            progress,
          },
          metrics: newMetrics || state.metrics
        }))
      },

      // Update scroll speed
      setScrollSpeed: (speed: number) => {
        const { content, scroll } = get()

        // Only update if speed actually changed
        if (scroll.speed === speed) return

        // Calculate metrics inline to avoid triggering another store update
        let newMetrics = null
        if (content.info) {
          const wordCount = content.info.wordCount
          const wpm = DEFAULT_WORDS_PER_MINUTE * speed
          const totalTime = (wordCount / wpm) * 60 // in seconds
          const elapsedTime = totalTime * scroll.progress
          const remainingTime = totalTime - elapsedTime

          newMetrics = {
            wordsPerMinute: wpm,
            elapsedTime,
            remainingTime,
            totalTime,
          }
        }

        set(state => ({
          scroll: {
            ...state.scroll,
            speed,
          },
          metrics: newMetrics || state.metrics
        }))
      },

      // Toggle play/pause
      togglePlayPause: () => {
        set(state => ({
          scroll: {
            ...state.scroll,
            isPlaying: !state.scroll.isPlaying,
          }
        }))
      },

      // Update voice activity
      updateVoiceActivity: (activity: VoiceActivity) => {
        set({ voice: activity })

        // Auto-pause/resume based on voice
        const { scroll } = get()
        if (activity.isSpeaking && scroll.isPlaying) {
          set(state => ({
            scroll: { ...state.scroll, isPlaying: false }
          }))
        } else if (!activity.isSpeaking && !scroll.isPlaying) {
          // Could auto-resume here if desired
        }
      },

      // Calculate reading metrics
      calculateMetrics: () => {
        const { content, scroll } = get()
        if (!content.info) return

        const wordCount = content.info.wordCount
        const wpm = DEFAULT_WORDS_PER_MINUTE * scroll.speed
        const totalTime = (wordCount / wpm) * 60 // in seconds
        const elapsedTime = totalTime * scroll.progress
        const remainingTime = totalTime - elapsedTime

        set({
          metrics: {
            wordsPerMinute: wpm,
            elapsedTime,
            remainingTime,
            totalTime,
          }
        })
      },

      // Reset state
      reset: () => {
        set(initialState)
      },
    }),
    {
      name: 'cuebird-teleprompter-store',
    }
  )
)