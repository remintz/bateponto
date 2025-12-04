"""Export utilities for generating reports."""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class ReportExporter:
    """Handles exporting reports to various formats."""

    def __init__(self, export_dir: str = None):
        """Initialize exporter with export directory.

        If export_dir is None, uses ~/.bateponto/exports as default.
        """
        if export_dir is None:
            # Use home folder by default
            self.export_dir = Path.home() / ".bateponto" / "exports"
        else:
            self.export_dir = Path(export_dir)

        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_summary_to_csv(
        self,
        summary: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
        filename: str = None
    ) -> Path:
        """
        Export project summary to CSV.

        Args:
            summary: List of project summaries with totals
            start_date: Report start date
            end_date: Report end date
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bateponto_report_{timestamp}.csv"

        filepath = self.export_dir / filename

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(["BatePonto - Relatório de Horas"])
            writer.writerow([
                f"Período: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
            ])
            writer.writerow([])

            # Write data header
            writer.writerow(["Projeto", "Horas Totais", "Horas Decimais"])

            # Write project data
            for item in summary:
                hours = item["total_hours"]
                hours_formatted = f"{int(hours):02d}:{int((hours % 1) * 60):02d}"
                writer.writerow([
                    item["project_name"],
                    hours_formatted,
                    f"{hours:.2f}"
                ])

            # Write total
            total_hours = sum(item["total_hours"] for item in summary)
            total_formatted = f"{int(total_hours):02d}:{int((total_hours % 1) * 60):02d}"
            writer.writerow([])
            writer.writerow(["TOTAL", total_formatted, f"{total_hours:.2f}"])

        return filepath

    def export_detailed_to_csv(
        self,
        entries: List[Dict[str, Any]],
        projects_map: Dict[str, str],
        filename: str = None
    ) -> Path:
        """
        Export detailed time entries to CSV.

        Args:
            entries: List of time entries
            projects_map: Map of project_id to project_name
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bateponto_detailed_{timestamp}.csv"

        filepath = self.export_dir / filename

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(["BatePonto - Registro Detalhado"])
            writer.writerow([])

            # Write data header
            writer.writerow([
                "Data/Hora",
                "Projeto",
                "Evento",
                "Pausa Automática"
            ])

            # Write entries
            for entry in entries:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                project_name = projects_map.get(entry["project_id"], entry["project_id"])
                event = entry["event"]
                auto_pause = "Sim" if entry.get("auto_pause", False) else "Não"

                # Translate events
                event_map = {
                    "start": "Início",
                    "stop": "Parada",
                    "auto_pause": "Pausa Automática"
                }
                event_translated = event_map.get(event, event)

                writer.writerow([
                    timestamp.strftime("%d/%m/%Y %H:%M:%S"),
                    project_name,
                    event_translated,
                    auto_pause
                ])

        return filepath

    def export_daily_breakdown_to_csv(
        self,
        entries: List[Dict[str, Any]],
        projects_map: Dict[str, str],
        start_date: datetime,
        end_date: datetime,
        filename: str = None
    ) -> Path:
        """
        Export daily breakdown of hours per project to CSV.

        Creates a simple table with dates as rows and projects as columns,
        showing total hours worked on each project per day.

        Args:
            entries: List of time entries
            projects_map: Map of project_id to project_name
            start_date: Report start date
            end_date: Report end date
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bateponto_daily_{timestamp}.csv"

        filepath = self.export_dir / filename

        # Get unique project IDs from entries
        project_ids = sorted(set(entry["project_id"] for entry in entries))
        project_names = [projects_map.get(pid, pid) for pid in project_ids]

        # Build daily totals: {date_str: {project_id: timedelta}}
        daily_totals: Dict[str, Dict[str, timedelta]] = {}

        # Process entries to calculate time per project per day
        # Group entries by project
        entries_by_project: Dict[str, List[Dict[str, Any]]] = {}
        for entry in entries:
            pid = entry["project_id"]
            if pid not in entries_by_project:
                entries_by_project[pid] = []
            entries_by_project[pid].append(entry)

        # Calculate daily time for each project
        for project_id, proj_entries in entries_by_project.items():
            # Sort entries by timestamp
            proj_entries.sort(key=lambda e: e["timestamp"])

            last_start = None
            for entry in proj_entries:
                ts = datetime.fromisoformat(entry["timestamp"])
                date_str = ts.strftime("%Y-%m-%d")

                if date_str not in daily_totals:
                    daily_totals[date_str] = {}

                if entry["event"] == "start":
                    last_start = ts
                elif entry["event"] in ["stop", "auto_pause"] and last_start:
                    # Handle sessions that span midnight
                    start_date_str = last_start.strftime("%Y-%m-%d")
                    end_date_str = ts.strftime("%Y-%m-%d")

                    if start_date_str == end_date_str:
                        # Same day
                        duration = ts - last_start
                        if start_date_str not in daily_totals:
                            daily_totals[start_date_str] = {}
                        if project_id not in daily_totals[start_date_str]:
                            daily_totals[start_date_str][project_id] = timedelta()
                        daily_totals[start_date_str][project_id] += duration
                    else:
                        # Spans multiple days - split by day
                        current = last_start
                        while current.strftime("%Y-%m-%d") <= end_date_str:
                            curr_date_str = current.strftime("%Y-%m-%d")
                            if curr_date_str not in daily_totals:
                                daily_totals[curr_date_str] = {}
                            if project_id not in daily_totals[curr_date_str]:
                                daily_totals[curr_date_str][project_id] = timedelta()

                            if curr_date_str == end_date_str:
                                # Last day - from midnight to end
                                day_start = ts.replace(hour=0, minute=0, second=0, microsecond=0)
                                if curr_date_str == start_date_str:
                                    daily_totals[curr_date_str][project_id] += ts - last_start
                                else:
                                    daily_totals[curr_date_str][project_id] += ts - day_start
                                break
                            elif curr_date_str == start_date_str:
                                # First day - from start to midnight
                                next_day = (current + timedelta(days=1)).replace(
                                    hour=0, minute=0, second=0, microsecond=0
                                )
                                daily_totals[curr_date_str][project_id] += next_day - current
                            else:
                                # Middle days - full 24 hours
                                daily_totals[curr_date_str][project_id] += timedelta(hours=24)

                            current = (current + timedelta(days=1)).replace(
                                hour=0, minute=0, second=0, microsecond=0
                            )

                    last_start = None
                elif entry["event"] in ["adjustment", "pause_adjustment"]:
                    # Add adjustment to the day
                    adjustment_minutes = entry.get("minutes", 0)
                    if date_str not in daily_totals:
                        daily_totals[date_str] = {}
                    if project_id not in daily_totals[date_str]:
                        daily_totals[date_str][project_id] = timedelta()
                    daily_totals[date_str][project_id] += timedelta(minutes=adjustment_minutes)

        # Sort dates
        sorted_dates = sorted(daily_totals.keys())

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')

            # Write column headers
            header = ["Data"] + project_names
            writer.writerow(header)

            # Write daily data
            for date_str in sorted_dates:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                row = [date_obj.strftime("%d/%m/%Y")]

                for pid in project_ids:
                    duration = daily_totals[date_str].get(pid, timedelta())
                    row.append(self._format_hours(duration))

                writer.writerow(row)

        return filepath

    def _format_hours(self, td: timedelta) -> str:
        """Format timedelta as HH:MM for display."""
        total_seconds = int(td.total_seconds())
        if total_seconds < 0:
            sign = "-"
            total_seconds = abs(total_seconds)
        else:
            sign = ""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{sign}{hours:02d}:{minutes:02d}"

    def format_duration(self, td: timedelta) -> str:
        """Format timedelta as HH:MM:SS."""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
