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
      setScrollSpeed: (scrollSpeed) => set({ scrollSpeed }),
      setScrollPosition: (scrollPosition) => set({ scrollPosition }),
      setFontSize: (fontSize) => set({ fontSize }),
      setContentHeight: (contentHeight) => set({ contentHeight }),
      setViewportHeight: (viewportHeight) => set({ viewportHeight }),
      setVoiceEnabled: (voiceEnabled) => set({ voiceEnabled }),
      setIsVoiceActive: (isVoiceActive) => set({ isVoiceActive }),
      setVoiceSensitivity: (voiceSensitivity) => set({ voiceSensitivity }),
      setVoiceThreshold: (voiceThreshold) => set({ voiceThreshold }),
      
      reset: () => set(initialState),
    }),
    {
      name: 'teleprompter-store',
    }
  )
)