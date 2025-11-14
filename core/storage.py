"""Storage module for persisting data in JSON files."""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class Storage:
    """Handles data persistence using JSON files."""

    def __init__(self, data_dir: str = None):
        """Initialize storage with data directory.

        If data_dir is None, uses ~/.bateponto as default.
        """
        if data_dir is None:
            # Use home folder by default
            self.data_dir = Path.home() / ".bateponto"
        else:
            self.data_dir = Path(data_dir)

        self.data_dir.mkdir(exist_ok=True)

        self.projects_file = self.data_dir / "projects.json"
        self.entries_file = self.data_dir / "time_entries.json"

        self._ensure_files()

    def _ensure_files(self):
        """Ensure data files exist with default structure."""
        if not self.projects_file.exists():
            self._save_json(self.projects_file, {
                "projects": [
                    {
                        "id": "p1",
                        "name": "Projeto 1",
                        "color": "green",
                        "active": True
                    },
                    {
                        "id": "p2",
                        "name": "Projeto 2",
                        "color": "blue",
                        "active": True
                    },
                    {
                        "id": "p3",
                        "name": "Projeto 3",
                        "color": "yellow",
                        "active": True
                    }
                ]
            })

        if not self.entries_file.exists():
            self._save_json(self.entries_file, {"entries": []})

    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """Load JSON data from file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, filepath: Path, data: Dict[str, Any]):
        """Save JSON data to file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Project methods
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        data = self._load_json(self.projects_file)
        return data.get("projects", [])

    def get_active_projects(self) -> List[Dict[str, Any]]:
        """Get only active projects."""
        projects = self.get_projects()
        return [p for p in projects if p.get("active", True)]

    def save_projects(self, projects: List[Dict[str, Any]]):
        """Save projects list."""
        self._save_json(self.projects_file, {"projects": projects})

    def add_project(self, project: Dict[str, Any]):
        """Add a new project."""
        projects = self.get_projects()
        projects.append(project)
        self.save_projects(projects)

    def update_project(self, project_id: str, updates: Dict[str, Any]):
        """Update a project."""
        projects = self.get_projects()
        for project in projects:
            if project["id"] == project_id:
                project.update(updates)
                break
        self.save_projects(projects)

    def delete_project(self, project_id: str):
        """Delete a project."""
        projects = self.get_projects()
        projects = [p for p in projects if p["id"] != project_id]
        self.save_projects(projects)

    # Time entry methods
    def get_entries(self) -> List[Dict[str, Any]]:
        """Get all time entries."""
        data = self._load_json(self.entries_file)
        return data.get("entries", [])

    def add_entry(self, entry: Dict[str, Any]):
        """Add a time entry."""
        entries = self.get_entries()

        # Ensure timestamp is string
        if isinstance(entry.get("timestamp"), datetime):
            entry["timestamp"] = entry["timestamp"].isoformat()

        entries.append(entry)
        self._save_json(self.entries_file, {"entries": entries})

    def get_entries_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get entries for a specific project."""
        entries = self.get_entries()
        return [e for e in entries if e.get("project_id") == project_id]

    def get_entries_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get entries within a date range."""
        entries = self.get_entries()
        filtered = []

        for entry in entries:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            if start_date <= timestamp <= end_date:
                filtered.append(entry)

        return filtered

    def get_entries_by_project_and_date(
        self,
        project_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get entries for a project within a date range."""
        entries = self.get_entries_by_date_range(start_date, end_date)
        return [e for e in entries if e.get("project_id") == project_id]
