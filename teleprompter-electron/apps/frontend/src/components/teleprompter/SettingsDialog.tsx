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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useSettingsStore } from '@/store/settings'
import { VoiceControlSettings } from '@/components/settings/VoiceControlSettings'

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
    autoReload,
    fileWatchEnabled,
    fileWatchDebounce,
    fileWatchNotifications,
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
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>
            Configure your teleprompter preferences
          </DialogDescription>
        </DialogHeader>
        
        <Tabs defaultValue="display" className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="display">Display</TabsTrigger>
            <TabsTrigger value="voice">Voice</TabsTrigger>
            <TabsTrigger value="file">File Watch</TabsTrigger>
          </TabsList>
          
          <TabsContent value="display" className="space-y-4 mt-4">
            {/* Display Settings */}
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Font Size</label>
                  <span className="text-sm text-muted-foreground">{fontSize}px</span>
                </div>
                <Slider
                  value={[fontSize]}
                  onValueChange={(value) => {
                    setFontSize(value[0])
                    updateSettings({ fontSize: value[0] })
                  }}
                  min={16}
                  max={120}
                  step={2}
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Default Speed</label>
                  <span className="text-sm text-muted-foreground">{scrollSpeed.toFixed(1)}x</span>
                </div>
                <Slider
                  value={[scrollSpeed]}
                  onValueChange={(value) => {
                    setScrollSpeed(value[0])
                    updateSettings({ scrollSpeed: value[0] })
                  }}
                  min={0.1}
                  max={5}
                  step={0.1}
                />
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="voice" className="space-y-4 mt-4">
            {/* Voice Settings */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <label className="text-sm font-medium">Enable Voice Detection</label>
                  <p className="text-xs text-muted-foreground">Control playback with your voice</p>
                </div>
                <Switch
                  checked={voiceEnabled}
                  onCheckedChange={(checked) => {
                    setVoiceEnabled(checked)
                    updateSettings({ voiceEnabled: checked })
                  }}
                />
              </div>

              {voiceEnabled && (
                <>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Sensitivity</label>
                    <Select
                      value={voiceSensitivity.toString()}
                      onValueChange={(value) => {
                        const intValue = parseInt(value)
                        setVoiceSensitivity(intValue)
                        updateSettings({ voiceSensitivity: intValue })
                      }}
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
                      <label className="text-sm font-medium">Threshold</label>
                      <span className="text-sm text-muted-foreground">{voiceThreshold}dB</span>
                    </div>
                    <Slider
                      value={[voiceThreshold]}
                      onValueChange={(value) => {
                        setVoiceThreshold(value[0])
                        updateSettings({ voiceThreshold: value[0] })
                      }}
                      min={-60}
                      max={0}
                      step={1}
                    />
                  </div>
                </>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="file" className="space-y-4 mt-4">
            {/* File Watch Settings */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <label className="text-sm font-medium">Enable File Watching</label>
                  <p className="text-xs text-muted-foreground">Monitor files for changes</p>
                </div>
                <Switch
                  checked={fileWatchEnabled}
                  onCheckedChange={(checked) => updateSettings({ fileWatchEnabled: checked })}
                />
              </div>
              
              {fileWatchEnabled && (
                <>
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <label className="text-sm font-medium">Auto Reload</label>
                      <p className="text-xs text-muted-foreground">Automatically reload when files change</p>
                    </div>
                    <Switch
                      checked={autoReload}
                      onCheckedChange={(checked) => updateSettings({ autoReload: checked })}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Debounce Delay</label>
                      <span className="text-sm text-muted-foreground">{fileWatchDebounce}ms</span>
                    </div>
                    <Slider
                      value={[fileWatchDebounce]}
                      onValueChange={(value) => updateSettings({ fileWatchDebounce: value[0] })}
                      min={100}
                      max={2000}
                      step={100}
                    />
                    <p className="text-xs text-muted-foreground">
                      Time to wait before reloading after file changes
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Notification Level</label>
                    <Select
                      value={fileWatchNotifications}
                      onValueChange={(value) => updateSettings({ fileWatchNotifications: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="minimal">Minimal</SelectItem>
                        <SelectItem value="verbose">Verbose</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted-foreground">
                      Controls how much information is shown in notifications
                    </p>
                  </div>
                </>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}