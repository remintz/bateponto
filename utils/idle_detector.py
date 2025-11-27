"""Sleep detection module - detects when system wakes from sleep."""

from datetime import datetime, timedelta
from threading import Thread, Lock
from typing import Optional, Callable
import time


class SleepDetector:
    """Detects when the system wakes up from sleep/suspend."""

    def __init__(self, sleep_threshold_minutes: int = 5):
        """
        Initialize sleep detector.

        Args:
            sleep_threshold_minutes: Minutes of sleep before triggering callback
        """
        self.sleep_threshold = timedelta(minutes=sleep_threshold_minutes)
        self.is_sleeping = False
        self.running = False
        self.sleep_start: Optional[datetime] = None
        self.lock = Lock()
        self.on_sleep_callback: Optional[Callable] = None
        self.on_wake_callback: Optional[Callable] = None
        self.monitor_thread: Optional[Thread] = None

    def _check_sleep(self):
        """Monitor for system sleep by detecting time jumps."""
        last_check = datetime.now()

        while self.running:
            now = datetime.now()
            time_since_last_check = now - last_check

            # If more than 30 seconds passed since last check (normally 1 second),
            # the system was probably sleeping
            if time_since_last_check.total_seconds() > 30:
                with self.lock:
                    # System just woke up from sleep
                    if time_since_last_check >= self.sleep_threshold:
                        # Sleep was long enough to trigger callback
                        if not self.is_sleeping:
                            self.is_sleeping = True
                            self.sleep_start = last_check
                            if self.on_sleep_callback:
                                self.on_sleep_callback()

            last_check = now
            time.sleep(1)

    def start(self):
        """Start monitoring for sleep state."""
        if self.running:
            return

        self.running = True
        self.monitor_thread = Thread(target=self._check_sleep, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        """Stop monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def set_sleep_callback(self, callback: Callable):
        """Set callback for when system wakes from sleep."""
        self.on_sleep_callback = callback

    def set_wake_callback(self, callback: Callable):
        """Set callback for when user acknowledges wake (manual action)."""
        self.on_wake_callback = callback

    def get_sleep_duration(self) -> timedelta:
        """Get how long the system was sleeping."""
        with self.lock:
            if self.is_sleeping and self.sleep_start:
                return datetime.now() - self.sleep_start
            return timedelta()

    def acknowledge_wake(self):
        """Called when user takes action after wake (e.g., clicks a project)."""
        with self.lock:
            was_sleeping = self.is_sleeping
            self.is_sleeping = False
            self.sleep_start = None

            if was_sleeping and self.on_wake_callback:
                self.on_wake_callback()

    def reset(self):
        """Reset sleep detector state."""
        with self.lock:
            self.is_sleeping = False
            self.sleep_start = None


# Alias for backward compatibility
IdleDetector = SleepDetector
