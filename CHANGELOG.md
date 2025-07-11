# Changelog

All notable changes to CueBird Teleprompter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Cross-platform distribution support for macOS and Windows
- PyInstaller packaging configuration with proper PyQt6-WebEngine bundling
- Automated build scripts for both platforms
- GitHub Actions workflow for automated releases
- Pre-built installers (DMG for macOS, EXE/ZIP for Windows)
- Resource path handling for bundled executables
- Platform-specific build configurations

### Changed
- Updated IconManager to use resource path helper for bundled environments
- Added PyInstaller dependencies to development requirements

### Technical
- Created `cuebird.spec` with platform-specific configurations
- Added `build_macos.sh` script with code signing support
- Added `build_windows.bat` script with Inno Setup integration
- Implemented `resource_path.py` utility for handling bundled resources
- Set up CI/CD pipeline for automated builds and releases

## [0.1.0] - 2025-01-10

### Added
- Initial release of CueBird Teleprompter
- Core teleprompter functionality with smooth 60 FPS scrolling
- Voice activity detection for hands-free control
- Markdown file support with live preview
- Adjustable scrolling speed (0.05x to 5x)
- Dynamic font sizing (16px to 120px)
- Section navigation (jump between headers)
- File watching with automatic reload
- Reading statistics and progress tracking
- Keyboard shortcuts for all major functions
- Dark theme optimized for teleprompter use
- Configuration system with JSON support
- Comprehensive error handling and logging

### Technical
- Built with PyQt6 and Python 3.13+
- Domain-Driven Design (DDD) architecture
- Dependency injection container
- Protocol-oriented design for flexibility
- WebRTC VAD integration for voice detection
- QWebEngineView for smooth text rendering
- Poetry for dependency management
- Comprehensive test suite with pytest

[Unreleased]: https://github.com/mvdmakesthings/teleprompter/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mvdmakesthings/teleprompter/releases/tag/v0.1.0