"""Time tracking module."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from core.storage import Storage


class TimeTracker:
    """Tracks time spent on projects."""

    def __init__(self, storage: Storage):
        """Initialize time tracker with storage."""
        self.storage = storage
        self.current_project: Optional[str] = None
        self.current_start: Optional[datetime] = None
        self.current_elapsed: timedelta = timedelta()
        self.paused_project: Optional[str] = None  # Store auto-paused project
        self.pause_start: Optional[datetime] = None  # When pause started

    def start_project(self, project_id: str) -> bool:
        """Start tracking time for a project."""
        # Stop current project if any
        if self.current_project:
            self.stop_project()

        self.current_project = project_id
        self.current_start = datetime.now()
        self.current_elapsed = timedelta()

        # Record start event
        self.storage.add_entry({
            "project_id": project_id,
            "event": "start",
            "timestamp": self.current_start,
            "auto_pause": False
        })

        return True

    def stop_project(self, auto_pause: bool = False) -> Optional[timedelta]:
        """Stop tracking current project."""
        if not self.current_project or not self.current_start:
            return None

        stop_time = datetime.now()

        # Record stop event
        self.storage.add_entry({
            "project_id": self.current_project,
            "event": "auto_pause" if auto_pause else "stop",
            "timestamp": stop_time,
            "auto_pause": auto_pause
        })

        # Calculate total elapsed time
        elapsed = self.current_elapsed + (stop_time - self.current_start)

        self.current_project = None
        self.current_start = None
        self.current_elapsed = timedelta()

        return elapsed

    def pause_project(self) -> bool:
        """Pause current project (auto-pause)."""
        if self.current_project:
            # Store which project was paused and when
            self.paused_project = self.current_project
            self.pause_start = datetime.now()
            
            self.stop_project(auto_pause=True)
            return True
        return False

    def resume_paused_project(self) -> bool:
        """Resume a project that was auto-paused.
        
        Returns:
            True if a project was resumed, False otherwise
        """
        if not self.paused_project or not self.pause_start:
            return False
        
        project_id = self.paused_project
        pause_start = self.pause_start
        pause_end = datetime.now()
        
        # Clear paused state
        self.paused_project = None
        self.pause_start = None
        
        # Record pause duration as a negative adjustment
        pause_duration = pause_end - pause_start
        pause_minutes = int(pause_duration.total_seconds() / 60)
        
        if pause_minutes > 0:  # Only record if pause was at least 1 minute
            self.storage.add_entry({
                "project_id": project_id,
                "event": "pause_adjustment",
                "timestamp": pause_end,
                "minutes": -pause_minutes,  # Negative to subtract from total time
                "description": f"Pausa automática por inatividade ({pause_minutes} min)",
                "auto_pause": True
            })
        
        # Resume the project
        return self.start_project(project_id)

    def add_adjustment(
        self, 
        project_id: str, 
        minutes: int, 
        description: str = "",
        date: Optional[datetime] = None
    ) -> bool:
        """Add a time adjustment (positive or negative) to a project.
        
        Args:
            project_id: ID of the project
            minutes: Number of minutes to adjust (positive or negative)
            description: Optional description/reason for the adjustment
            date: Optional date for the adjustment (defaults to now)
        
        Returns:
            True if successful
        """
        if date is None:
            date = datetime.now()
        
        # Record adjustment event
        self.storage.add_entry({
            "project_id": project_id,
            "event": "adjustment",
            "timestamp": date,
            "minutes": minutes,
            "description": description,
            "auto_pause": False
        })
        
        return True

    def get_current_elapsed(self) -> timedelta:
        """Get elapsed time for current project."""
        if not self.current_start:
            return timedelta()

        return self.current_elapsed + (datetime.now() - self.current_start)

    def is_tracking(self) -> bool:
        """Check if currently tracking a project."""
        return self.current_project is not None

    def get_current_project(self) -> Optional[str]:
        """Get currently tracked project ID."""
        return self.current_project

    def calculate_project_time(
        self,
        project_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> timedelta:
        """Calculate total time for a project in a date range."""
        entries = self.storage.get_entries_by_project_and_date(
            project_id,
            start_date,
            end_date
        )

        total_time = timedelta()
        last_start = None

        for entry in entries:
            timestamp = datetime.fromisoformat(entry["timestamp"])

            if entry["event"] == "start":
                last_start = timestamp
            elif entry["event"] in ["stop", "auto_pause"] and last_start:
                total_time += timestamp - last_start
                last_start = None
            elif entry["event"] in ["adjustment", "pause_adjustment"]:
                # Add or subtract adjustment time
                adjustment_minutes = entry.get("minutes", 0)
                total_time += timedelta(minutes=adjustment_minutes)

        # If project is still running and it's the current project
        if last_start and self.current_project == project_id:
            total_time += datetime.now() - last_start

        return total_time

    def get_today_time(self, project_id: str) -> timedelta:
        """Get time worked on project today."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

        return self.calculate_project_time(project_id, today_start, today_end)

    def get_all_projects_today(self, project_ids: List[str]) -> Dict[str, timedelta]:
        """Get today's time for all projects."""
        result = {}
        for project_id in project_ids:
            result[project_id] = self.get_today_time(project_id)
        return result

    def get_project_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, any]]:
        """Get summary of time for all projects in date range."""
        projects = self.storage.get_projects()
        summary = []

        for project in projects:
            project_id = project["id"]
            total_time = self.calculate_project_time(project_id, start_date, end_date)

            summary.append({
                "project_id": project_id,
                "project_name": project["name"],
                "total_time": total_time,
                "total_hours": total_time.total_seconds() / 3600
            })

        # Sort by total time descending
        summary.sort(key=lambda x: x["total_time"], reverse=True)
        return summary

    def format_timedelta(self, td: timedelta) -> str:
        """Format timedelta as HH:MM:SS."""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def format_timedelta_short(self, td: timedelta) -> str:
        """Format timedelta as HH:MM."""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
