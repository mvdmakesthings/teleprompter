"use client"

import React from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Keyboard } from 'lucide-react'
import { useKeyboard } from '@/hooks/useKeyboard'

export function KeyboardHelp() {
  const { getShortcuts } = useKeyboard()
  const shortcuts = getShortcuts()

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" title="Keyboard Shortcuts">
          <Keyboard className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Keyboard Shortcuts</DialogTitle>
          <DialogDescription>
            Quick reference for all available keyboard shortcuts
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="mb-2 font-semibold">Playback Controls</h3>
              <div className="space-y-1">
                <KeyboardShortcut keys="Space" description="Play/Pause" />
                <KeyboardShortcut keys="R" description="Reset to beginning" />
                <KeyboardShortcut keys="Esc" description="Exit fullscreen or stop" />
              </div>
            </div>
            <div>
              <h3 className="mb-2 font-semibold">Speed Controls</h3>
              <div className="space-y-1">
                <KeyboardShortcut keys="+/-" description="Increase/Decrease speed" />
                <KeyboardShortcut keys="↑/↓" description="Increase/Decrease speed" />
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="mb-2 font-semibold">Navigation</h3>
              <div className="space-y-1">
                <KeyboardShortcut keys="←/→" description="Previous/Next section" />
                <KeyboardShortcut keys="PgUp/PgDn" description="Previous/Next section" />
              </div>
            </div>
            <div>
              <h3 className="mb-2 font-semibold">Features</h3>
              <div className="space-y-1">
                <KeyboardShortcut keys="V" description="Toggle voice control" />
                <KeyboardShortcut keys="C" description="Toggle cursor visibility" />
              </div>
            </div>
          </div>
          <div>
            <h3 className="mb-2 font-semibold">Global Shortcuts (work when app is not focused)</h3>
            <div className="space-y-1">
              <KeyboardShortcut keys="Cmd/Ctrl+Space" description="Play/Pause" />
              <KeyboardShortcut keys="Cmd/Ctrl+R" description="Reset to beginning" />
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

interface KeyboardShortcutProps {
  keys: string
  description: string
}

function KeyboardShortcut({ keys, description }: KeyboardShortcutProps) {
  return (
    <div className="flex items-center justify-between text-sm">
      <kbd className="rounded bg-muted px-2 py-1 font-mono text-xs">
        {keys}
      </kbd>
      <span className="text-muted-foreground">{description}</span>
    </div>
  )
}