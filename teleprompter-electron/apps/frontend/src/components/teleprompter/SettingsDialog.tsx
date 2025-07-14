"use client"

import React from 'react'
import { GearIcon } from '@radix-ui/react-icons'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useSettingsStore } from '@/store/settings'

interface SettingsDialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  // Get current values from teleprompter store
  const { fontSize, scrollSpeed } = useTeleprompterStore()
  
  // Get settings and actions from settings store
  const {
    voiceEnabled,
    voiceSensitivity,
    voiceThreshold,
    updateSettings,
  } = useSettingsStore()
  
  // Also get setters from teleprompter store for immediate updates
  const { setScrollSpeed, setFontSize, setVoiceEnabled, setVoiceSensitivity, setVoiceThreshold } = useTeleprompterStore()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon">
          <GearIcon className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>
            Configure your teleprompter preferences
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6 py-4">
          {/* Display Settings */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Display</h3>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm">Font Size</label>
                <span className="text-sm text-muted-foreground">{fontSize}px</span>
              </div>
              <Slider
                value={[fontSize]}
                onValueChange={(value) => setFontSize(value[0])}
                min={16}
                max={120}
                step={2}
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm">Default Speed</label>
                <span className="text-sm text-muted-foreground">{scrollSpeed.toFixed(1)}x</span>
              </div>
              <Slider
                value={[scrollSpeed]}
                onValueChange={(value) => setScrollSpeed(value[0])}
                min={0.1}
                max={5}
                step={0.1}
              />
            </div>
          </div>

          {/* Voice Settings */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Voice Control</h3>
            
            <div className="flex items-center justify-between">
              <label className="text-sm">Enable Voice Detection</label>
              <Button
                variant={voiceEnabled ? "default" : "outline"}
                size="sm"
                onClick={() => setVoiceEnabled(!voiceEnabled)}
              >
                {voiceEnabled ? "On" : "Off"}
              </Button>
            </div>

            {voiceEnabled && (
              <>
                <div className="space-y-2">
                  <label className="text-sm">Sensitivity</label>
                  <Select
                    value={voiceSensitivity.toString()}
                    onValueChange={(value) => setVoiceSensitivity(parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0">Most Aggressive</SelectItem>
                      <SelectItem value="1">Aggressive</SelectItem>
                      <SelectItem value="2">Normal</SelectItem>
                      <SelectItem value="3">Least Aggressive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-sm">Threshold</label>
                    <span className="text-sm text-muted-foreground">{voiceThreshold}dB</span>
                  </div>
                  <Slider
                    value={[voiceThreshold]}
                    onValueChange={(value) => setVoiceThreshold(value[0])}
                    min={-60}
                    max={0}
                    step={1}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}