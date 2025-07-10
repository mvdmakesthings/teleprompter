# Contributing to CueBird Teleprompter

First off, thank you for considering contributing to Teleprompter! 🎉 It's people like you that make Teleprompter such a great tool for content creators worldwide.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Issues](#issues)
  - [Pull Requests](#pull-requests)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Request Process](#pull-request-process)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
  - [Python Style Guide](#python-style-guide)
  - [Commit Messages](#commit-messages)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)
- [Recognition](#recognition)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to Github Issues

### Our Standards

- **Be welcoming**: Use inclusive language and be respectful of differing viewpoints
- **Be considerate**: Your work will affect others, so be thoughtful about the impact
- **Be patient**: Remember that everyone was new once
- **Be helpful**: Share knowledge and help others learn

## Getting Started

### Issues

#### Before Creating an Issue

- **Check existing issues**: Search to see if the problem has already been reported
- **Check closed issues**: Your issue might have been resolved already
- **Try the latest version**: Update to the latest version to see if it's fixed

#### Creating a Good Issue

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed and what you expected
- Include screenshots if applicable
- Include your environment details:
  - OS and version
  - Python version
  - Teleprompter version
  - Hardware specs (if performance-related)

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible
- Follow the [Python style guide](#python-style-guide)
- Include thoughtfully-worded, well-structured tests
- Document new code
- End all files with a newline

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as [GitHub issues](https://github.com/yourusername/teleprompter/issues). Create an issue and provide the following information:

**Bug Report Template:**
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 11, macOS 14, Ubuntu 22.04]
 - Python version: [e.g. 3.13.0]
 - Teleprompter version: [e.g. 1.2.0]
 - Display resolution: [e.g. 1920x1080]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are also tracked as [GitHub issues](https://github.com/yourusername/teleprompter/issues).

**Enhancement Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

### Your First Code Contribution

Unsure where to begin? Look for these labels:

- `good first issue` - Simple issues perfect for beginners
- `help wanted` - Issues where we need community help
- `documentation` - Help improve our docs
- `ui/ux` - Frontend improvements
- `performance` - Speed and efficiency improvements

### Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Set up your development environment** (see below)
3. **Make your changes** following our style guidelines
4. **Add tests** for any new functionality
5. **Run the test suite** to ensure nothing is broken
6. **Update documentation** as needed
7. **Submit a pull request** with a comprehensive description

**Important**: By submitting a pull request, you agree that your contributions will be dual-licensed under both GPL v3 and our commercial license. This allows us to maintain both an open-source version and offer commercial licensing options.

## Development Setup

### Prerequisites

- Python 3.13+
- Poetry
- Git
- A working microphone (for testing voice features)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/yourusername/teleprompter.git
cd teleprompter

# Add upstream remote
git remote add upstream https://github.com/originalowner/teleprompter.git

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Create a new branch
git checkout -b feature/your-feature-name
```

### Running the Application

```bash
# Activate virtual environment
poetry shell

# Run the application
python -m teleprompter

# Or use the task runner
poetry poe run
```

## Style Guidelines

### Python Style Guide

We use `ruff` for both linting and formatting. Our configuration is in `pyproject.toml`.

**Key Guidelines:**

- Follow PEP 8
- Use type hints for all function signatures
- Write descriptive variable names
- Keep functions small and focused
- Use Protocol types for interfaces
- Document all public APIs

**Example:**
```python
from typing import Protocol

class ScrollControllerProtocol(Protocol):
    """Protocol for scroll controller implementations."""
    
    def start_scrolling(self, speed: float) -> None:
        """Start scrolling at the specified speed.
        
        Args:
            speed: Scrolling speed multiplier (0.05 to 5.0)
        """
        ...
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Build process or auxiliary tool changes

**Examples:**
```
feat: add keyboard shortcut for section navigation
fix: prevent scroll position reset on file reload
docs: update voice control setup instructions
refactor: extract scroll logic into dedicated service
```

## Project Structure

```
src/teleprompter/
├── core/              # Business logic & contracts
│   ├── protocols.py   # Interface definitions
│   ├── container.py   # Dependency injection
│   └── services.py    # Business services
├── domain/            # Domain models
│   ├── content/       # Content management
│   ├── reading/       # Reading control
│   └── voice/         # Voice detection
├── infrastructure/    # External services
└── ui/               # User interface
    ├── widgets/      # UI components
    └── managers/     # UI state management
```

**Architecture Guidelines:**

- Follow Domain-Driven Design principles
- Use dependency injection for all services
- Define interfaces as Protocols
- Keep UI logic separate from business logic
- Write unit tests for all domain logic

## Testing

### Running Tests

```bash
# Run all tests
poetry poe test

# Run with coverage
poetry poe test-coverage

# Run specific test file
poetry run pytest tests/test_file_manager.py

# Run with verbose output
poetry run pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source code structure
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

**Example Test:**
```python
import pytest
from teleprompter.domain.content.file_manager import FileManager

class TestFileManager:
    def test_load_valid_markdown_file(self, tmp_path):
        """Test loading a valid markdown file."""
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Content")
        
        # Test loading
        manager = FileManager()
        content = manager.load_file(str(test_file))
        
        assert content == "# Test Content"
    
    def test_load_nonexistent_file_raises_error(self):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        manager = FileManager()
        
        with pytest.raises(FileNotFoundError):
            manager.load_file("/nonexistent/file.md")
```

## Documentation

### Code Documentation

- Add docstrings to all public classes and methods
- Use Google-style docstrings
- Include type information in docstrings
- Provide usage examples for complex functionality

### Project Documentation

- Update README.md for user-facing changes
- Update CLAUDE.md for architectural changes
- Add entries to CHANGELOG.md
- Create wiki pages for detailed guides

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas

### Getting Help

- Search existing issues and discussions
- Ask in Discord for quick questions
- Create an issue for bugs or feature requests

## Recognition

Contributors are recognized in several ways:

- **Release Notes**: Mentioned in release notes for significant contributions
- **Shoutout in Contributors list**: Listed in the Contributors list in the README.md

### Types of Contributions We Recognize

- 💻 Code contributions
- 📖 Documentation improvements
- 🐛 Bug reports with reproducible steps
- 💡 Feature suggestions with detailed proposals
- 🎨 UI/UX improvements

---

## Thank You! 🙏

Your contributions make CueBird Teleprompter better for everyone. We're excited to see what you'll bring to the project!

If you have any questions, don't hesitate to reach out. Happy contributing!