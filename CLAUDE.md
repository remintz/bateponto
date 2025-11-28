# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BatePonto is a time tracking application with a TUI (Terminal User Interface) built with Python curses. It allows users to track time spent on multiple projects with automatic idle detection.

## Commands

```bash
# Run the application
python main.py

# Build macOS app
./build_macos.sh

# Install dependencies
pip install -r requirements.txt
```

## Architecture

### Core Components (`core/`)

- **Storage**: JSON-based persistence layer (`~/.bateponto/projects.json`, `~/.bateponto/time_entries.json`)
- **ProjectManager**: CRUD operations for projects, handles active/inactive status
- **TimeTracker**: Manages start/stop/pause events, calculates durations

### UI Layer (`ui/`)

All screens inherit a similar pattern with `render()`, `handle_key()`, and draw methods:

- **MainScreen**: Shows 6 project buttons in 2-column layout, real-time clock, active project timer
- **ConfigScreen**: Project CRUD with keyboard-driven forms (A=add, E=edit, D=delete, T=toggle active)
- **ReportScreen**: Period-based reports with CSV export
- **AdjustmentScreen**: Manual time adjustments

### Utilities (`utils/`)

- **SleepDetector**: Monitors system sleep/wake cycles to auto-pause tracking
- **ReportExporter**: CSV export functionality

### Application Flow

`main.py` contains `BatePontoApp` which:
1. Initializes all components and screens
2. Runs the main loop with screen-based state machine (`current_screen`)
3. Delegates input handling to the active screen
4. Returns action strings ('reports', 'config', 'back', 'quit') for navigation

### Data Model

Projects have: `id`, `name`, `color`, `active` (boolean for visibility on main screen)

Time entries have: `project_id`, `event` (start/stop/auto_pause), `timestamp`, `auto_pause` flag

### Key Patterns

- Screens communicate via return values (action strings), not direct calls
- All UI operations use curses safe patterns with try/except for terminal edge cases
- Mouse and keyboard inputs are handled separately
- Project limit on main screen: 6 active projects (3 per column)
