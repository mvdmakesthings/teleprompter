# Teleprompter Application - Product Requirements Document

## Executive Summary

The Teleprompter Application is a Python-based desktop application designed for content creators and video producers to display scripted content in a smooth, readable format during video recording sessions. The application reads markdown files and presents them in a traditional teleprompter style with customizable display settings.

## Target Users

### Primary Users
- **Content Creators**: YouTubers, podcasters, and social media influencers who need to deliver scripted content
- **Video Producers**: Professional video production teams requiring reliable teleprompter functionality

### User Context
- Users typically engage with the application for short sessions (5-15 minutes)
- Sessions align with video recording takes
- Users need quick setup and minimal distractions during recording

## Core Features

### 1. File Management
- **Single File Loading**: Support loading one markdown (.md) file at a time
- **File Selection**: Simple file picker interface to select markdown files from local system
- **File Validation**: Verify file is valid markdown before loading

### 2. Markdown Rendering
The application must support rendering of the following markdown elements:
- **Headers**: H1-H6 with appropriate visual hierarchy
- **Text Formatting**: Bold (**text**) and italic (*text*)
- **Lists**: Both ordered (1. 2. 3.) and unordered (- or *) lists
- **Links**: Display link text (URLs can be shown but not clickable during teleprompting)

### 3. Display Controls

#### Playback Controls
- **Play/Pause**: Start or stop automatic scrolling
- **Speed Adjustment**: 
  - Mouse wheel for smooth real-time speed control
  - Visual speed indicator (e.g., 1x, 1.5x, 2x)
  - Speed range: 0.3x to 5x normal reading speed

#### Visual Controls
- **Font Size**: Adjustable text size (range: 16px to 72px)
- **Font Colors**: 
  - Text color selection
  - Background color selection
  - Preset for traditional teleprompter (white text on black background)

### 4. Display Modes
- **Windowed Mode**: Resizable window for setup and practice
- **Full-Screen Mode**: Distraction-free full-screen display for recording
- **Mode Toggle**: Easy switching between modes

### 5. Settings Persistence
- **Local Storage**: Save user preferences in application configuration file
- **Persisted Settings**:
  - Last used font size
  - Color preferences
  - Default scroll speed
  - Window size and position (for windowed mode)

## User Interface Specifications

### Layout Structure
```
+----------------------------------+
|        Control Bar               |
|  [File] [Play/Pause] [FS]       |
|  Speed: [----o----] Font: [24]  |
+----------------------------------+
|                                  |
|         Scrolling Text           |
|           Display                |
|            Area                  |
|                                  |
|                                  |
+----------------------------------+
```

### Visual Design
- **Primary Style**: Traditional teleprompter aesthetic
  - Black background (#000000)
  - White text (#FFFFFF)
  - High contrast for visibility
- **Font**: Sans-serif, optimized for readability
- **Text Alignment**: Center-aligned
- **Scroll Direction**: Bottom to top (traditional teleprompter style)

### Control Elements
1. **File Selector**: Button to open file picker
2. **Play/Pause Button**: Toggle with clear visual states
3. **Speed Slider**: Horizontal slider with current speed display
4. **Font Size Input**: Number input with increment/decrement buttons
5. **Color Pickers**: For text and background colors
6. **Full-Screen Toggle**: Icon button for mode switching

## Technical Requirements

### Platform
- **Type**: Python desktop application
- **Python Version**: Python 3.13+
- **Operating Systems**: Windows, macOS, Linux
- **GUI Framework**: Modern Python GUI framework (e.g., PyQt, Tkinter, or Kivy)
- **Package Management**: Poetry for dependency management

### Performance
- **Smooth Scrolling**: 60 FPS scrolling performance
- **Low Latency**: Immediate response to control changes
- **Resource Efficiency**: Minimal CPU/memory usage during idle
- **Native Performance**: Leverage OS-native rendering capabilities

### Data Handling
- **File Size Limit**: Support markdown files up to 1MB
- **Character Encoding**: UTF-8 support
- **Error Handling**: Graceful handling of malformed markdown
- **File System Access**: Native file picker dialogs

## User Workflows

### Primary Workflow
1. User launches desktop application
2. Clicks "Load File" and selects markdown script
3. Adjusts font size and colors if needed
4. Enters full-screen mode
5. Starts recording video
6. Presses play to begin scrolling
7. Adjusts speed with mouse wheel as needed
8. Pauses/resumes as required during recording
9. Exits full-screen when finished

### Setup Workflow
1. User opens application
2. Configures preferred settings (font, colors, default speed)
3. Tests with sample text
4. Settings automatically saved for next session

## Success Metrics

1. **Load Time**: File loads and displays within 1 second
2. **Scroll Smoothness**: No visible stuttering at any speed
3. **Control Responsiveness**: < 50ms response to user inputs
4. **Session Completion**: 95% of sessions complete without errors

## Future Considerations

While not in initial scope, the following features may be considered for future releases:
- Multiple file queue/playlist
- Remote control via mobile device
- Custom fonts
- Mirror/flip display option
- Bookmarks and navigation markers
- Export of timing data
- Integration with video recording software (OBS Studio, etc.)
- Hotkey support for hands-free control
- Multiple monitor support
- Teleprompter hardware integration
- Voice-activated controls
- Script editing within the application

## Constraints and Limitations

1. **No Network Features**: All functionality must work completely offline
2. **No User Accounts**: No login or cloud sync required
3. **Single File Focus**: One script at a time to maintain simplicity
4. **No Audio Sync**: No audio cue or timing features in v1

## Acceptance Criteria

The application will be considered complete when:
1. Can load and display markdown files with specified formatting
2. Smooth scrolling works at all speed settings
3. All controls function as specified
4. Settings persist between application sessions
5. Full-screen mode works without UI glitches
6. Performance meets specified targets
7. Works reliably on target operating systems