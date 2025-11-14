"""Idle detection module using pynput."""

from datetime import datetime, timedelta
from threading import Thread, Lock
from typing import Optional, Callable
import time


class IdleDetector:
    """Detects user inactivity using keyboard and mouse monitoring."""

    def __init__(self, idle_timeout_minutes: int = 5):
        """
        Initialize idle detector.

        Args:
            idle_timeout_minutes: Minutes of inactivity before triggering idle state
        """
        self.idle_timeout = timedelta(minutes=idle_timeout_minutes)
        self.last_activity = datetime.now()
        self.is_idle = False
        self.running = False
        self.lock = Lock()
        self.on_idle_callback: Optional[Callable] = None
        self.on_active_callback: Optional[Callable] = None
        self.monitor_thread: Optional[Thread] = None

        # pynput listeners
        self.keyboard_listener = None
        self.mouse_listener = None

    def _on_activity(self):
        """Called when user activity is detected."""
        with self.lock:
            was_idle = self.is_idle
            self.last_activity = datetime.now()
            self.is_idle = False

            # Trigger active callback if we were idle
            if was_idle and self.on_active_callback:
                self.on_active_callback()

    def _on_keyboard_event(self, *args, **kwargs):
        """Handle keyboard events."""
        self._on_activity()

    def _on_mouse_event(self, *args, **kwargs):
        """Handle mouse events."""
        self._on_activity()

    def _check_idle(self):
        """Check if user has been idle."""
        while self.running:
            with self.lock:
                elapsed = datetime.now() - self.last_activity

                if not self.is_idle and elapsed >= self.idle_timeout:
                    self.is_idle = True
                    if self.on_idle_callback:
                        self.on_idle_callback()

            time.sleep(1)  # Check every second

    def start(self):
        """Start monitoring for idle state."""
        if self.running:
            return

        try:
            from pynput import keyboard, mouse

            # Start keyboard listener
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_keyboard_event,
                on_release=self._on_keyboard_event
            )
            self.keyboard_listener.start()

            # Start mouse listener
            self.mouse_listener = mouse.Listener(
                on_move=self._on_mouse_event,
                on_click=self._on_mouse_event,
                on_scroll=self._on_mouse_event
            )
            self.mouse_listener.start()

            # Start idle checker thread
            self.running = True
            self.monitor_thread = Thread(target=self._check_idle, daemon=True)
            self.monitor_thread.start()

        except ImportError:
            # pynput not available, disable idle detection
            pass

    def stop(self):
        """Stop monitoring."""
        self.running = False

        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def set_idle_callback(self, callback: Callable):
        """Set callback for when user becomes idle."""
        self.on_idle_callback = callback

    def set_active_callback(self, callback: Callable):
        """Set callback for when user becomes active after being idle."""
        self.on_active_callback = callback

    def get_idle_time(self) -> timedelta:
        """Get current idle time."""
        with self.lock:
            if self.is_idle:
                return datetime.now() - self.last_activity
            return timedelta()

    def reset(self):
        """Reset idle detector."""
        with self.lock:
            self.last_activity = datetime.now()
            self.is_idle = False
