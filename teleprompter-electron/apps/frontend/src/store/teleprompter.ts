import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

interface Section {
  id: string
  title: string
  level: number
  position: number
}

interface TeleprompterState {
  // Content
  content: string
  rawContent: string
  currentFile: string | null
  wordCount: number
  sections: Section[]
  
  // Playback
  isPlaying: boolean
  scrollSpeed: number
  scrollPosition: number
  
  // Display
  fontSize: number
  contentHeight: number
  viewportHeight: number
  
  // Voice
  voiceEnabled: boolean
  isVoiceActive: boolean
  voiceSensitivity: number
  voiceThreshold: number
  
  // Computed getters
  progress: () => number
  remainingTime: () => number
  currentSection: () => Section | null
  canScroll: () => boolean
  isAtEnd: () => boolean
  
  // Actions
  setContent: (content: string) => void
  setRawContent: (rawContent: string) => void
  setCurrentFile: (file: string | null) => void
  setWordCount: (count: number) => void
  setSections: (sections: Section[]) => void
  setIsPlaying: (playing: boolean) => void
  setScrollSpeed: (speed: number) => void
  setScrollPosition: (position: number) => void
  setFontSize: (size: number) => void
  setContentHeight: (height: number) => void
  setViewportHeight: (height: number) => void
  setVoiceEnabled: (enabled: boolean) => void
  setIsVoiceActive: (active: boolean) => void
  setVoiceSensitivity: (sensitivity: number) => void
  setVoiceThreshold: (threshold: number) => void
  reset: () => void
  
  // Batch updates
  loadContent: (data: {
    content: string
    rawContent: string
    filePath: string
    wordCount: number
    sections: Section[]
  }) => void
}

const initialState = {
  content: '',
  rawContent: '',
  currentFile: null,
  wordCount: 0,
  sections: [],
  isPlaying: false,
  scrollSpeed: 1.0,
  scrollPosition: 0,
  fontSize: 48,
  contentHeight: 0,
  viewportHeight: 0,
  voiceEnabled: false,
  isVoiceActive: false,
  voiceSensitivity: 1,
  voiceThreshold: -40,
}

export const useTeleprompterStore = create<TeleprompterState>()(
  devtools(
    (set, get) => ({
      ...initialState,
      
      setContent: (content) => set({ content }),
      setRawContent: (rawContent) => set({ rawContent }),
      setCurrentFile: (currentFile) => set({ currentFile }),
      setWordCount: (wordCount) => set({ wordCount }),
      setSections: (sections) => set({ sections }),
      setIsPlaying: (isPlaying) => set({ isPlaying }),
      setScrollSpeed: (scrollSpeed) => {
        const validated = Math.max(0.1, Math.min(5, scrollSpeed))
        set({ scrollSpeed: validated })
      },
      setScrollPosition: (scrollPosition) => {
        const { contentHeight, viewportHeight } = get()
        const maxScroll = Math.max(0, contentHeight - viewportHeight)
        const validated = Math.max(0, Math.min(maxScroll, scrollPosition))
        set({ scrollPosition: validated })
      },
      setFontSize: (fontSize) => {
        const validated = Math.max(16, Math.min(120, fontSize))
        set({ fontSize: validated })
      },
      setContentHeight: (contentHeight) => set({ contentHeight }),
      setViewportHeight: (viewportHeight) => set({ viewportHeight }),
      setVoiceEnabled: (voiceEnabled) => set({ voiceEnabled }),
      setIsVoiceActive: (isVoiceActive) => set({ isVoiceActive }),
      setVoiceSensitivity: (voiceSensitivity) => set({ voiceSensitivity }),
      setVoiceThreshold: (voiceThreshold) => set({ voiceThreshold }),
      
      reset: () => set(initialState),
      
      // Computed getters
      progress: () => {
        const { scrollPosition, contentHeight, viewportHeight } = get()
        const maxScroll = Math.max(0, contentHeight - viewportHeight)
        return maxScroll > 0 ? Math.min((scrollPosition / maxScroll) * 100, 100) : 0
      },
      
      remainingTime: () => {
        const { scrollPosition, contentHeight, viewportHeight, scrollSpeed } = get()
        const remainingPixels = Math.max(0, contentHeight - viewportHeight - scrollPosition)
        // Avoid division by zero and return Infinity for very slow speeds
        if (scrollSpeed <= 0 || !isFinite(scrollSpeed)) return Infinity
        return remainingPixels / (scrollSpeed * 60)
      },
      
      currentSection: () => {
        const { sections, scrollPosition } = get()
        if (!sections.length) return null
        
        // Find the section that the current scroll position is in
        let current = sections[0]
        for (const section of sections) {
          if (section.position <= scrollPosition) {
            current = section
          } else {
            break
          }
        }
        return current
      },
      
      canScroll: () => {
        const { contentHeight, viewportHeight } = get()
        return contentHeight > viewportHeight
      },
      
      isAtEnd: () => {
        const { scrollPosition, contentHeight, viewportHeight } = get()
        const maxScroll = Math.max(0, contentHeight - viewportHeight)
        return scrollPosition >= maxScroll
      },
      
      // Batch update for loading content
      loadContent: (data) => {
        set({
          content: data.content,
          rawContent: data.rawContent,
          currentFile: data.filePath,
          wordCount: data.wordCount,
          sections: data.sections,
          scrollPosition: 0,
          isPlaying: false,
        })
      },
    }),
    {
      name: 'teleprompter-store',
    }
  )
)