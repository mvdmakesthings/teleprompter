# CueBird Teleprompter - Electron Edition

A modern teleprompter application built with Electron, Next.js, and Python.

## Architecture

This is a monorepo containing:

- **apps/desktop** - Electron main process (TypeScript)
- **apps/frontend** - Next.js frontend with static export
- **apps/backend** - Python FastAPI backend wrapper
- **packages/shared** - Shared types and constants
- **packages/ipc** - Electron IPC definitions

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

## Building for Production

### 1. Build Frontend

```bash
cd apps/frontend
npm run build
```

This creates a static export in `apps/frontend/out/`.

### 2. Build Python Backend

```bash
cd apps/backend
npm run build
```

This uses PyInstaller to create a standalone executable.

### 3. Package Electron App

```bash
cd apps/desktop
npm run build
npm run package
```

This creates platform-specific installers in `apps/desktop/release/`.

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

## Key Features

- **Self-contained**: Python backend runs as subprocess
- **Type-safe**: Full TypeScript support across packages
- **Secure**: Context isolation and secure IPC
- **Modern**: React 18, Next.js 14, Zustand for state
- **Cross-platform**: Windows, macOS, Linux support

## Configuration

The app uses a layered configuration approach:

1. Default settings in `packages/shared/src/constants.ts`
2. User settings stored via `electron-store`
3. Environment-specific overrides

## License

MIT