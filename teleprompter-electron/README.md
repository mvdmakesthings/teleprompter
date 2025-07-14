# CueBird Teleprompter - Electron Frontend

Modern teleprompter application built with Electron, Next.js, and FastAPI.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development mode (backend + frontend + electron)
npm run dev
```

That's it! The app will launch with hot-reload enabled.

## 📁 Architecture

This is a monorepo containing:

- **apps/desktop** - Electron main process with window management
- **apps/frontend** - Next.js React app with Tailwind CSS
- **apps/backend** - Python FastAPI backend integration
- **packages/** - Shared TypeScript types and utilities

## Development Setup

### Prerequisites

- Node.js 20+
- Python 3.13+
- Poetry (for Python dependencies)

### Installation

```bash
# Install Node dependencies
npm install

# Install Python dependencies (from root teleprompter directory)
cd ../
poetry install
```

### Development

Run all apps in development mode:

```bash
# From teleprompter-electron directory
npm run dev
```

Or run individual apps:

```bash
# Desktop (Electron)
npm run desktop:dev

# Frontend (Next.js)
npm run frontend:dev

# Backend (Python)
cd ../ && poetry run python -m teleprompter.backend.main
```

## 🏗️ Building for Production

```bash
# Build for current platform
npm run build

# Build for specific platforms
npm run build:mac    # macOS (Universal)
npm run build:win    # Windows (64-bit)
npm run build:linux  # Linux (AppImage)
```

The built applications will be in the `dist/` directory.

## Project Structure

```
teleprompter-electron/
├── apps/
│   ├── desktop/        # Electron main process
│   │   ├── src/
│   │   │   ├── main/   # Main process code
│   │   │   └── preload/ # Preload scripts
│   │   └── package.json
│   ├── frontend/       # Next.js app
│   │   ├── app/        # App router pages
│   │   ├── src/        # Components, hooks, stores
│   │   └── package.json
│   └── backend/        # Python backend wrapper
│       └── main.py     # Entry point for bundled backend
├── packages/
│   ├── shared/         # Shared types and constants
│   └── ipc/           # IPC channel definitions
└── package.json       # Root workspace config
```

## ✨ Key Features

### 🎯 Core Features
- **Voice Control**: Dual-mode voice activity detection
- **Virtual Scrolling**: Smooth performance for large texts
- **Real-time Updates**: WebSocket-powered file watching
- **Keyboard Shortcuts**: Global and local shortcuts
- **Performance Monitoring**: Real-time FPS and metrics

### 🛠️ Technical Features
- **Self-contained**: Python backend embedded in app
- **Type-safe**: Full TypeScript + Pydantic validation
- **Secure**: Context isolation and secure IPC
- **Modern Stack**: React 18, Next.js 14, Zustand
- **Cross-platform**: Windows, macOS, Linux support

## ⚙️ Configuration

Frontend settings are stored in browser localStorage, while backend settings use JSON configuration files. See the main [README](../README.md) for configuration details.

## License

MIT