"""Project management module."""

from typing import List, Dict, Any, Optional
from core.storage import Storage


class ProjectManager:
    """Manages projects and their configuration."""

    def __init__(self, storage: Storage):
        """Initialize project manager with storage."""
        self.storage = storage

    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        return self.storage.get_projects()

    def get_active_projects(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get active projects, limited to a specific number for UI."""
        active = self.storage.get_active_projects()
        return active[:limit]

    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific project by ID."""
        projects = self.storage.get_projects()
        for project in projects:
            if project["id"] == project_id:
                return project
        return None

    def create_project(
        self,
        name: str,
        color: str = "white",
        active: bool = True
    ) -> Dict[str, Any]:
        """Create a new project."""
        projects = self.storage.get_projects()

        # Generate unique ID
        max_id = 0
        for project in projects:
            try:
                pid = int(project["id"].replace("p", ""))
                if pid > max_id:
                    max_id = pid
            except (ValueError, AttributeError):
                pass

        new_id = f"p{max_id + 1}"

        project = {
            "id": new_id,
            "name": name,
            "color": color,
            "active": active
        }

        self.storage.add_project(project)
        return project

    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
        active: Optional[bool] = None
    ) -> bool:
        """Update a project's properties."""
        updates = {}
        if name is not None:
            updates["name"] = name
        if color is not None:
            updates["color"] = color
        if active is not None:
            updates["active"] = active

        if updates:
            self.storage.update_project(project_id, updates)
            return True
        return False

    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        project = self.get_project_by_id(project_id)
        if project:
            self.storage.delete_project(project_id)
            return True
        return False

    def toggle_project_active(self, project_id: str) -> bool:
        """Toggle a project's active status."""
        project = self.get_project_by_id(project_id)
        if project:
            new_status = not project.get("active", True)
            self.storage.update_project(project_id, {"active": new_status})
            return new_status
        return False

    def get_project_color_code(self, color: str) -> int:
        """Convert color name to curses color pair code."""
        color_map = {
            "green": 1,
            "blue": 2,
            "yellow": 3,
            "red": 4,
            "magenta": 5,
            "cyan": 6,
            "white": 7
        }
        return color_map.get(color.lower(), 7)
