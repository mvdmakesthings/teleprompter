# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Teleprompter - A simple teleprompter application built with Python 3.13+ using Poetry for dependency management.

## Development Commands

### Environment Setup
```bash
poetry install              # Install dependencies
poetry shell               # Activate virtual environment
```

### Running the Application
```bash
poetry run python -m teleprompter.main    # Run the main application
```

## Project Structure

The project follows a standard Python package structure:
- `src/teleprompter/` - Main package directory containing the application code
- `src/teleprompter/main.py` - Application entry point

## Important Notes

- This is a Poetry-managed project, all dependencies should be added via `poetry add`
- Python 3.13+ is required
- The project is licensed under MIT
- When adding new Python modules, ensure `__init__.py` files exist in package directories