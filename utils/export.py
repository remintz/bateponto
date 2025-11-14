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

    def format_duration(self, td: timedelta) -> str:
        """Format timedelta as HH:MM:SS."""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
