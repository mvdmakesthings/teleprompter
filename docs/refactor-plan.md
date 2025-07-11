# CueBird Qt to Electron Refactor Plan

## Executive Summary

This document outlines a comprehensive plan to migrate CueBird from PyQt6 to a modern Electron + Next.js + Python architecture. The refactor maintains the existing Python business logic while replacing the Qt UI layer with a more maintainable web-based frontend.

## Goals & Constraints

### Primary Goals
- Replace PyQt6 UI with Electron + Next.js frontend
- Maintain existing Python business logic and domain layer
- Improve developer experience and UI flexibility
- Enable modern web development practices
- Maintain or improve performance

### Constraints
- Preserve all existing functionality
- Maintain the clean DDD architecture
- Keep Python for business logic and services
- Ensure smooth scrolling performance (60 FPS)
- Support voice activity detection

## Architecture Overview

### Current Architecture (PyQt6)
```
PyQt6 Application
├── UI Layer (PyQt6 Widgets)
├── Domain Layer (Python Business Logic)
├── Infrastructure Layer (Settings, Logging)
└── Core Layer (DI Container, Protocols)
```

### Target Architecture (Electron)
```
Electron Application
├── Frontend (Next.js + React)
│   ├── Renderer Process
│   ├── UI Components
│   └── State Management
├── Electron Main Process
│   ├── Window Management
│   ├── IPC Handlers
│   └── Python Process Manager
└── Python Backend Service
    ├── FastAPI Server
    ├── Domain Layer (Unchanged)
    ├── Infrastructure Layer (Adapted)
    └── Core Layer (Adapted)
```

## Self-Contained Architecture

### Overview
CueBird will be a fully self-contained desktop application that requires no internet connection or external services. The Python backend is embedded within the Electron app and communicates locally.

### Architecture Details

```
CueBird.app/exe
├── Electron Runtime
│   ├── Main Process (Node.js)
│   │   ├── Window Management
│   │   ├── Python Process Manager
│   │   └── IPC Handlers
│   └── Renderer Process
│       └── Next.js Static App
└── Resources
    ├── Python Backend (Bundled)
    │   ├── Embedded Python Runtime
    │   ├── FastAPI Server
    │   └── All Dependencies
    └── Frontend Assets
```

### Communication Flow
1. **Electron Main Process** spawns Python backend on app start
2. **Python Backend** starts FastAPI server on dynamic localhost port
3. **Frontend** communicates with backend via `http://127.0.0.1:[dynamic-port]`
4. **No external network** - all communication is local

### Benefits
- **Privacy**: All data stays on user's machine
- **Reliability**: Works offline, no dependency on cloud services
- **Performance**: Local communication is faster than network
- **Security**: No exposed ports or network vulnerabilities

## Migration Strategy

### Phase 1: Backend Preparation (Week 1-2)

#### 1.1 Create Python API Layer
- Install FastAPI and dependencies
- Create API endpoints for all current services:
  - `/api/content/load` - File loading
  - `/api/content/parse` - Markdown parsing
  - `/api/content/analyze` - Content analysis
  - `/api/reading/metrics` - Reading metrics
  - `/api/reading/control` - Scroll control
  - `/api/voice/detect` - Voice activity detection
  - `/api/settings` - Settings management
- Implement WebSocket support for real-time features
- Add CORS configuration for development

#### 1.2 Adapt Core Services
- Modify service interfaces to be API-friendly
- Convert Qt signals to WebSocket events
- Implement JSON serialization for domain models
- Create API response models with Pydantic

#### 1.3 Decouple from Qt Dependencies
- Replace QSettings with JSON-based settings
- Convert Qt-specific utilities to pure Python
- Implement file watching without Qt

### Phase 2: Electron Foundation (Week 2-3)

#### 2.1 Project Setup
```bash
# New project structure
teleprompter-electron/
├── apps/
│   ├── desktop/        # Electron app
│   ├── frontend/       # Next.js app
│   └── backend/        # Python FastAPI
├── packages/
│   ├── shared/         # Shared types/utils
│   └── ipc/           # IPC definitions
└── package.json       # Monorepo root
```

#### 2.2 Electron Main Process
- Set up Electron with TypeScript
- Implement window management
- Create Python subprocess manager
- Set up IPC communication layer
- Implement preload script for security

##### Python Backend Integration (Self-Contained)
The Python FastAPI server will run as a child process within Electron:

```typescript
// electron/main/pythonManager.ts
import { spawn } from 'child_process';
import { app } from 'electron';
import path from 'path';

class PythonManager {
  private pythonProcess: ChildProcess | null = null;
  private port: number = 0;

  async start() {
    // Find available port
    this.port = await getAvailablePort();
    
    // Path to bundled Python executable
    const pythonPath = app.isPackaged
      ? path.join(process.resourcesPath, 'python', 'teleprompter-backend')
      : path.join(__dirname, '../../backend/main.py');
    
    // Spawn Python process
    this.pythonProcess = spawn(pythonPath, [
      '--port', this.port.toString(),
      '--host', '127.0.0.1'  // Only localhost
    ]);
    
    // Wait for server to be ready
    await this.waitForServer();
  }

  getApiUrl() {
    return `http://127.0.0.1:${this.port}`;
  }
}
```

**Key Points:**
- FastAPI runs on localhost only (no external network access)
- Port is dynamically assigned to avoid conflicts
- Python backend is bundled with PyInstaller
- No internet connection required - fully offline

#### 2.3 Next.js Setup
- Initialize Next.js 14 with App Router
- Configure for static export (no SSR)
- Set up Tailwind CSS for styling
- Create base layout structure
- Implement React Server Components support

### Phase 3: Frontend Development (Week 3-5)

#### 3.1 Component Migration
Map PyQt6 widgets to React components:

| PyQt6 Component | React Component | Library |
|-----------------|-----------------|---------|
| QWebEngineView | Custom WebView | Built-in |
| QToolBar | Toolbar Component | Custom |
| QSlider | Range Input | shadcn/ui |
| QPushButton | Button | shadcn/ui |
| QComboBox | Select | shadcn/ui |
| QDialog | Dialog | shadcn/ui |

#### 3.2 Core UI Components
- **TeleprompterDisplay**: Main text display with smooth scrolling
- **ControlPanel**: Speed, font size, play/pause controls
- **VoiceIndicator**: Voice activity visualization
- **ProgressBar**: Reading progress indicator
- **SettingsDialog**: Configuration interface
- **FileLoader**: Drag-and-drop file interface

#### 3.3 State Management
- Use Zustand for global state
- Implement stores for:
  - Content state (loaded text, sections)
  - Reading state (position, speed, playing)
  - Settings state (preferences)
  - Voice state (activity, enabled)

#### 3.4 Real-time Communication
- WebSocket connection to Python backend
- Handle events:
  - Voice activity updates
  - File change notifications
  - Reading metrics updates
- Implement reconnection logic

### Phase 4: Feature Parity (Week 5-6)

#### 4.1 Keyboard Shortcuts
- Implement global shortcuts in Electron main
- Local shortcuts in React components
- Maintain existing key mappings

#### 4.2 Voice Control Integration
- Stream audio data to Python backend
- Display real-time voice activity
- Implement auto-pause/resume logic

#### 4.3 File Watching
- Monitor loaded files for changes
- Implement debounced reload
- Show reload notifications

#### 4.4 Performance Optimization
- Implement virtual scrolling for large texts
- Use React.memo for component optimization
- Implement request debouncing
- Add performance monitoring

### Phase 5: Testing & Polish (Week 6-7)

#### 4.1 Testing Strategy
- Unit tests for React components (Vitest)
- Integration tests for Electron IPC
- E2E tests with Playwright
- Maintain Python backend tests

#### 4.2 Build & Distribution

##### Self-Contained Packaging Strategy
The app will be fully self-contained with no external dependencies:

```yaml
# electron-builder.yml
appId: com.cuebird.teleprompter
directories:
  output: dist
  buildResources: build
files:
  - "!**/.vscode/*"
  - "!backend/**"  # Exclude source, include binary
  - "frontend/out/**/*"  # Next.js static export
extraResources:
  - from: "backend/dist/teleprompter-backend"
    to: "python/teleprompter-backend"
    filter: ["**/*"]
```

**Build Process:**
1. **Backend Compilation**:
   ```bash
   cd backend
   poetry install
   pyinstaller --onefile \
     --name teleprompter-backend \
     --add-data "domain:domain" \
     --hidden-import uvicorn \
     --hidden-import fastapi \
     main.py
   ```

2. **Frontend Build**:
   ```bash
   cd frontend
   npm run build  # Creates static export
   ```

3. **Electron Package**:
   ```bash
   electron-builder --mac --win --linux
   ```

**Result**: Single executable with embedded Python runtime, no internet required

- Configure electron-builder
- Bundle Python with PyInstaller
- Create installers for each platform
- Implement auto-update mechanism

#### 4.3 Migration Testing
- Feature comparison checklist
- Performance benchmarking
- User acceptance testing
- Bug fixing and optimization

## Technical Decisions

### Communication Protocol
**Choice: Local WebSocket + REST API**
- All communication via localhost (127.0.0.1)
- WebSocket for real-time features (voice, file watching)
- REST for request/response operations
- JSON for data serialization
- No external network access required

### Frontend Framework
**Choice: Next.js 14 with App Router**
- Modern React features (Server Components)
- Excellent developer experience
- Built-in optimization
- Static export for Electron

### State Management
**Choice: Zustand**
- Lightweight and performant
- TypeScript support
- Easy integration with React
- DevTools support

### UI Component Library
**Choice: shadcn/ui + Tailwind CSS**
- Customizable components
- Consistent design system
- Accessibility built-in
- Small bundle size

### Python Backend Framework
**Choice: FastAPI**
- Async support
- WebSocket support
- Automatic API documentation
- Pydantic integration

## File Mapping

### Python Files to Preserve
All files in these directories remain largely unchanged:
- `src/teleprompter/core/` (except Qt dependencies)
- `src/teleprompter/domain/`
- `src/teleprompter/utils/` (adapted for non-Qt)

### Python Files to Create
```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── routes/
│   │   ├── content.py
│   │   ├── reading.py
│   │   ├── voice.py
│   │   └── settings.py
│   ├── websocket/
│   │   ├── handlers.py
│   │   └── events.py
│   └── models/
│       ├── requests.py
│       └── responses.py
└── services/
    └── adapters.py      # Adapt existing services
```

### TypeScript Files to Create
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── api/          # API client
├── components/
│   ├── teleprompter/
│   ├── controls/
│   ├── settings/
│   └── ui/
├── hooks/
│   ├── useWebSocket.ts
│   ├── useKeyboard.ts
│   └── useVoice.ts
├── store/
│   ├── content.ts
│   ├── reading.ts
│   └── settings.ts
└── lib/
    ├── api.ts
    └── utils.ts
```

## Risk Mitigation

### Performance Risks
- **Risk**: Web-based scrolling may not match Qt performance
- **Mitigation**: Use CSS transforms, RAF, and virtual scrolling

### Complexity Risks
- **Risk**: Managing multiple processes increases complexity
- **Mitigation**: Use PM2 or similar for process management

### Platform Risks
- **Risk**: Platform-specific issues with Electron
- **Mitigation**: Early testing on all target platforms

## Success Criteria

1. **Feature Parity**: All PyQt6 features work in Electron
2. **Performance**: Maintain 60 FPS scrolling
3. **Stability**: No crashes or memory leaks
4. **Developer Experience**: Faster development cycle
5. **User Experience**: Improved UI responsiveness

## Timeline Summary

- **Week 1-2**: Backend API preparation
- **Week 2-3**: Electron foundation setup
- **Week 3-5**: Frontend development
- **Week 5-6**: Feature parity implementation
- **Week 6-7**: Testing and polish

Total estimated time: 7 weeks for complete migration

## Next Steps

1. Set up new project structure
2. Create FastAPI backend skeleton
3. Implement first API endpoint
4. Create minimal Electron app
5. Begin incremental migration

## Appendix: Technology Versions

- Electron: 32.x
- Next.js: 14.x
- React: 18.x
- FastAPI: 0.115.x
- Node.js: 20.x
- Python: 3.13+
- TypeScript: 5.x