#!/usr/bin/env python3
"""BatePonto - Time Tracking Application."""

import curses
import sys
import time
from pathlib import Path
from typing import Optional

from core.storage import Storage
from core.project_manager import ProjectManager
from core.time_tracker import TimeTracker
from utils.idle_detector import IdleDetector
from utils.export import ReportExporter

from ui.main_screen import MainScreen
from ui.report_screen import ReportScreen
from ui.config_screen import ConfigScreen
from ui.adjustment_screen import AdjustmentScreen


class BatePontoApp:
    """Main application class."""

    def __init__(self, stdscr):
        """Initialize application."""
        self.stdscr = stdscr
        self.running = True
        self.current_screen = "main"

        # Initialize core components
        self.storage = Storage()
        self.project_manager = ProjectManager(self.storage)
        self.time_tracker = TimeTracker(self.storage)
        self.exporter = ReportExporter()

        # Initialize idle detector
        self.idle_detector = IdleDetector(idle_timeout_minutes=5)
        self.idle_detector.set_idle_callback(self._on_idle)
        self.idle_detector.set_active_callback(self._on_active)
        self.idle_detector.start()

        # Initialize screens
        self.main_screen = MainScreen(stdscr, self.project_manager, self.time_tracker)
        self.report_screen = ReportScreen(stdscr, self.project_manager, self.time_tracker, self.exporter)
        self.config_screen = ConfigScreen(stdscr, self.project_manager, self.storage)
        self.adjustment_screen = AdjustmentScreen(stdscr, self.project_manager, self.time_tracker)

        # Configure curses
        curses.curs_set(0)  # Hide cursor
        self.stdscr.timeout(100)  # Non-blocking input with 100ms timeout

    def _on_idle(self):
        """Called when user becomes idle."""
        if self.time_tracker.is_tracking():
            self.time_tracker.pause_project()

    def _on_active(self):
        """Called when user becomes active after being idle."""
        # Automatically resume the paused project
        self.time_tracker.resume_paused_project()

    def run(self):
        """Main application loop."""
        try:
            while self.running:
                # Render current screen
                if self.current_screen == "main":
                    self.main_screen.render()
                    action = self._handle_main_screen()

                    if action == 'reports':
                        self.current_screen = 'reports'
                    elif action == 'config':
                        self.current_screen = 'config'
                    elif action == 'adjustments':
                        self.current_screen = 'adjustments'
                    elif action == 'quit':
                        self._quit_app()

                elif self.current_screen == "reports":
                    self.report_screen.render()
                    action = self._handle_report_screen()

                    if action == 'back':
                        self.current_screen = 'main'

                elif self.current_screen == "config":
                    self.config_screen.render()
                    action = self._handle_config_screen()

                    if action == 'back':
                        self.current_screen = 'main'

                elif self.current_screen == "adjustments":
                    self.adjustment_screen.render()
                    action = self._handle_adjustment_screen()

                    if action == 'main':
                        self.current_screen = 'main'
                        self.main_screen.refresh_projects()

                # Small delay to prevent high CPU usage
                time.sleep(0.01)

        except KeyboardInterrupt:
            self._quit_app()
        finally:
            self._cleanup()

    def _handle_main_screen(self) -> str:
        """Handle input for main screen."""
        try:
            key = self.stdscr.getch()

            if key == -1:  # No input
                return None

            # Check for mouse event
            if key == curses.KEY_MOUSE:
                return self.main_screen.handle_mouse(key)

            # Handle keyboard
            return self.main_screen.handle_key(key)

        except curses.error:
            return None

    def _handle_report_screen(self) -> str:
        """Handle input for report screen."""
        try:
            key = self.stdscr.getch()

            if key == -1:
                return None

            return self.report_screen.handle_key(key)

        except curses.error:
            return None

    def _handle_config_screen(self) -> str:
        """Handle input for config screen."""
        try:
            key = self.stdscr.getch()

            if key == -1:
                return None

            return self.config_screen.handle_key(key)

        except curses.error:
            return None

    def _handle_adjustment_screen(self) -> Optional[str]:
        """Handle adjustment screen input."""
        try:
            key = self.stdscr.getch()

            if key != -1:  # If a key was pressed
                action = self.adjustment_screen.handle_key(key)
                return action

        except Exception:
            pass

        return None

    def _quit_app(self):
        """Quit the application."""
        # Check if project is running
        if self.time_tracker.is_tracking():
            h, w = self.stdscr.getmaxyx()

            # Show confirmation dialog
            msg1 = "Há um projeto em andamento!"
            msg2 = "Deseja parar e sair? (S/N)"

            self.stdscr.addstr(h // 2, (w - len(msg1)) // 2, msg1,
                             curses.A_BOLD | curses.A_REVERSE)
            self.stdscr.addstr(h // 2 + 1, (w - len(msg2)) // 2, msg2,
                             curses.A_REVERSE)
            self.stdscr.refresh()

            # Wait for confirmation
            self.stdscr.timeout(-1)  # Blocking
            while True:
                key = self.stdscr.getch()
                if key in [ord('s'), ord('S'), ord('y'), ord('Y')]:
                    self.time_tracker.stop_project()
                    break
                elif key in [ord('n'), ord('N')]:
                    self.stdscr.timeout(100)
                    return
                elif key == 27:  # ESC
                    self.stdscr.timeout(100)
                    return

        self.running = False

    def _cleanup(self):
        """Clean up resources."""
        # Stop idle detector
        self.idle_detector.stop()

        # Stop any running project
        if self.time_tracker.is_tracking():
            self.time_tracker.stop_project()


def main(stdscr):
    """Main entry point for curses application."""
    app = BatePontoApp(stdscr)
    app.run()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Erro fatal: {e}", file=sys.stderr)
        sys.exit(1)
