# Phase 4.1: Keyboard Shortcuts Implementation

## Overview

This document describes the implementation of keyboard shortcuts for the CueBird teleprompter application as part of the PyQt6 to Electron migration.

## Implementation Details

### 1. Main Process (Electron)

#### ShortcutManager (`apps/desktop/src/main/shortcutManager.ts`)
- Manages both global and local keyboard shortcuts
- Registers default shortcuts based on PyQt6 implementation
- Handles global shortcuts using Electron's `globalShortcut` API
- Sends shortcut trigger events to renderer process via IPC

#### IPC Integration
- Added new IPC channels for shortcut management:
  - `SHORTCUTS_REGISTER`: Register a new shortcut
  - `SHORTCUTS_UNREGISTER`: Unregister a shortcut
  - `SHORTCUTS_TRIGGERED`: Event sent when shortcut is triggered
  - `SHORTCUTS_GET_ALL`: Get all registered shortcuts

### 2. Renderer Process (React)

#### useKeyboard Hook (`apps/frontend/src/hooks/useKeyboard.ts`)
- Central hook for keyboard shortcut handling
- Maps keyboard events to actions
- Integrates with Zustand stores for state updates
- Handles both local keyboard events and global shortcut triggers from main process

#### Keyboard Shortcuts Implemented

**Playback Controls:**
- `Space`: Toggle play/pause
- `R`: Reset to beginning
- `Escape`: Exit fullscreen or stop scrolling

**Speed Controls:**
- `+/-`: Increase/decrease speed
- `↑/↓`: Increase/decrease speed (arrow keys)

**Navigation:**
- `←/→`: Previous/next section
- `PageUp/PageDown`: Previous/next section

**Feature Toggles:**
- `V`: Toggle voice control
- `C`: Toggle cursor visibility

**Global Shortcuts (work when app is not focused):**
- `Cmd/Ctrl+Space`: Toggle play/pause
- `Cmd/Ctrl+R`: Reset to beginning

### 3. Additional Features

#### Cursor Visibility Management
- `useCursorVisibility` hook manages cursor hiding/showing
- Supports manual toggle with `C` key
- Auto-hide functionality after 3 seconds of inactivity

#### Keyboard Help Dialog
- `KeyboardHelp` component displays all available shortcuts
- Accessible via keyboard icon in the header
- Shows both local and global shortcuts

### 4. State Integration

#### Settings Store Updates
- Added `cursorHidden` state for cursor visibility
- Added `voiceControlEnabled` state for voice control toggle
- Integrated with persistence layer

#### Type Definitions
- Updated IPC types to include `ShortcutDefinition` interface
- Extended `IpcApi` interface with shortcut-related methods
- Updated global window types for proper TypeScript support

## Testing the Implementation

1. **Local Shortcuts**: Focus the app window and press any of the keyboard shortcuts
2. **Global Shortcuts**: Use Cmd/Ctrl+Space or Cmd/Ctrl+R when the app is not focused
3. **Cursor Toggle**: Press 'C' to toggle cursor visibility
4. **Voice Toggle**: Press 'V' to toggle voice control
5. **Help Dialog**: Click the keyboard icon in the header to see all shortcuts

## Files Modified/Created

### Created:
- `/apps/desktop/src/main/shortcutManager.ts` - Shortcut management in main process
- `/apps/frontend/src/hooks/useKeyboard.ts` - React hook for keyboard handling
- `/apps/frontend/src/hooks/useCursorVisibility.ts` - Cursor visibility management
- `/apps/frontend/src/components/teleprompter/KeyboardHelp.tsx` - Help dialog component

### Modified:
- `/packages/ipc/src/channels.ts` - Added shortcut-related IPC channels
- `/packages/ipc/src/types.ts` - Added ShortcutDefinition type and IPC methods
- `/apps/desktop/src/main/index.ts` - Integrated ShortcutManager
- `/apps/desktop/src/main/ipcHandlers.ts` - Added shortcut IPC handlers
- `/apps/desktop/src/preload/index.ts` - Exposed shortcut API to renderer
- `/apps/frontend/src/store/settings.ts` - Added cursor and voice control state
- `/apps/frontend/app/page.tsx` - Integrated keyboard hooks and help dialog
- `/apps/frontend/src/types/global.d.ts` - Updated window types

## Next Steps

- Test all shortcuts thoroughly on different platforms (Windows, macOS, Linux)
- Consider adding customizable keyboard shortcuts in settings
- Add visual indicators when shortcuts are triggered
- Implement additional shortcuts as needed based on user feedback