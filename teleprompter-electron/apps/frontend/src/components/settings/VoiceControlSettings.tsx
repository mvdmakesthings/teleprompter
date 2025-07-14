"use client"

import React from 'react'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Mic, MicOff, AlertCircle } from 'lucide-react'
import { useTeleprompterStore } from '@/store/teleprompter'
import { useVoiceControl } from '@/hooks/useVoiceControl'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export function VoiceControlSettings() {
  const {
    voiceEnabled,
    setVoiceEnabled,
    voiceSensitivity,
    setVoiceSensitivity,
  } = useTeleprompterStore()
  
  const [processingMode, setProcessingMode] = React.useState<'frontend' | 'backend'>('frontend')
  
  const {
    isProcessing,
    error,
    permissionState,
    requestPermission,
    toggleVoiceControl,
  } = useVoiceControl({
    useBackendProcessing: processingMode === 'backend'
  })
  
  const handleToggleVoice = async () => {
    if (!voiceEnabled && permissionState === 'prompt') {
      const granted = await requestPermission()
      if (!granted) {
        return
      }
    }
    
    await toggleVoiceControl()
  }
  
  const sensitivityLabels = ['Low', 'Medium', 'High', 'Very High']
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {voiceEnabled ? <Mic className="h-5 w-5" /> : <MicOff className="h-5 w-5" />}
          Voice Control
        </CardTitle>
        <CardDescription>
          Control scrolling with your voice. The teleprompter will pause when you stop speaking.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Permission warning */}
        {permissionState === 'denied' && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Microphone access has been denied. Please enable microphone permissions in your browser settings and reload the page.
            </AlertDescription>
          </Alert>
        )}
        
        {/* Error message */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {/* Voice control toggle */}
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="voice-enabled">Enable Voice Control</Label>
            <p className="text-sm text-muted-foreground">
              {voiceEnabled 
                ? isProcessing 
                  ? 'Voice control is active' 
                  : 'Starting voice control...'
                : 'Voice control is disabled'}
            </p>
          </div>
          <Switch
            id="voice-enabled"
            checked={voiceEnabled}
            onCheckedChange={handleToggleVoice}
            disabled={permissionState === 'denied'}
          />
        </div>
        
        {/* Sensitivity slider */}
        <div className="space-y-2">
          <Label htmlFor="voice-sensitivity">
            Sensitivity: {sensitivityLabels[voiceSensitivity]}
          </Label>
          <Slider
            id="voice-sensitivity"
            min={0}
            max={3}
            step={1}
            value={[voiceSensitivity]}
            onValueChange={(values) => setVoiceSensitivity(values[0])}
            disabled={!voiceEnabled}
            className="w-full"
          />
          <p className="text-sm text-muted-foreground">
            Higher sensitivity detects quieter speech but may be triggered by background noise.
          </p>
        </div>
        
        {/* Processing mode selector */}
        <div className="space-y-2">
          <Label htmlFor="processing-mode">Processing Mode</Label>
          <Select
            value={processingMode}
            onValueChange={(value) => setProcessingMode(value as 'frontend' | 'backend')}
            disabled={voiceEnabled}
          >
            <SelectTrigger id="processing-mode">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="frontend">Frontend (Browser)</SelectItem>
              <SelectItem value="backend">Backend (Python VAD)</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-sm text-muted-foreground">
            {processingMode === 'frontend' 
              ? 'Voice detection runs in your browser (lower latency)'
              : 'Voice detection runs on the backend using WebRTC VAD (more accurate)'}
          </p>
        </div>
        
        {/* Auto-pause/resume settings */}
        <div className="space-y-4">
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Behavior Settings</h4>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="auto-pause"
                  defaultChecked={true}
                  disabled={!voiceEnabled}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="auto-pause" className="text-sm font-normal">
                  Auto-pause when you stop speaking
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="auto-resume"
                  defaultChecked={true}
                  disabled={!voiceEnabled}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="auto-resume" className="text-sm font-normal">
                  Auto-resume when you start speaking
                </Label>
              </div>
            </div>
          </div>
        </div>
        
        {/* Test microphone button */}
        {voiceEnabled && isProcessing && (
          <div className="pt-2">
            <p className="text-sm text-muted-foreground">
              Speak into your microphone to test voice detection. The indicator above will show when speech is detected.
            </p>
          </div>
        )}
        
        {/* Permission request button */}
        {permissionState === 'prompt' && !voiceEnabled && (
          <Button
            variant="outline"
            onClick={requestPermission}
            className="w-full"
          >
            <Mic className="mr-2 h-4 w-4" />
            Grant Microphone Access
          </Button>
        )}
      </CardContent>
    </Card>
  )
}