"""Reports screen UI for viewing time summaries."""

import curses
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


def safe_addstr(stdscr, y: int, x: int, text: str, attr=0, max_width: int = None):
    """Safely add string to screen with bounds checking."""
    try:
        h, w = stdscr.getmaxyx()
        if y >= h or x >= w or y < 0 or x < 0:
            return False

        available = w - x - 1
        if max_width:
            available = min(available, max_width)

        if available <= 0:
            return False

        stdscr.addstr(y, x, text[:available], attr)
        return True
    except curses.error:
        return False


class ReportScreen:
    """Reports screen with time summaries and export options."""

    def __init__(self, stdscr, project_manager, time_tracker, exporter):
        """Initialize report screen."""
        self.stdscr = stdscr
        self.project_manager = project_manager
        self.time_tracker = time_tracker
        self.exporter = exporter

        self.period_options = [
            ("Hoje", 0),
            ("Esta Semana", 1),
            ("Este Mês", 2),
            ("Últimos 7 dias", 3),
            ("Últimos 30 dias", 4),
            ("Personalizado", 5)
        ]
        self.selected_period = 0
        self.summary_data: List[Dict[str, Any]] = []

        self.start_date: Optional[datetime] = None
        self.end_date: Optional[datetime] = None

    def _get_period_dates(self, period_index: int) -> tuple:
        """Get start and end dates for selected period."""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        if period_index == 0:  # Hoje
            return today_start, today_end

        elif period_index == 1:  # Esta Semana
            # Monday to Sunday
            days_since_monday = now.weekday()
            week_start = today_start - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
            return week_start, week_end

        elif period_index == 2:  # Este Mês
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Last day of month
            if now.month == 12:
                month_end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
            month_end = month_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            return month_start, month_end

        elif period_index == 3:  # Últimos 7 dias
            start = today_start - timedelta(days=6)
            return start, today_end

        elif period_index == 4:  # Últimos 30 dias
            start = today_start - timedelta(days=29)
            return start, today_end

        elif period_index == 5:  # Personalizado
            if self.start_date and self.end_date:
                return self.start_date, self.end_date
            return today_start, today_end

        return today_start, today_end

    def refresh_data(self):
        """Refresh summary data for selected period."""
        start_date, end_date = self._get_period_dates(self.selected_period)
        self.summary_data = self.time_tracker.get_project_summary(start_date, end_date)

    def draw_header(self):
        """Draw header."""
        h, w = self.stdscr.getmaxyx()

        title = "Relatórios de Horas"
        self.stdscr.attron(curses.A_BOLD | curses.A_REVERSE)
        x_pos = max(0, (w - len(title)) // 2)
        safe_addstr(self.stdscr, 0, x_pos, title)
        self.stdscr.attroff(curses.A_BOLD | curses.A_REVERSE)

    def draw_period_selector(self):
        """Draw period selection menu."""
        h, w = self.stdscr.getmaxyx()

        label = "Período:"
        safe_addstr(self.stdscr, 2, 5, label, curses.A_BOLD)

        x = 15
        for i, (period_name, _) in enumerate(self.period_options):
            if x >= w - 2:
                break

            if i == self.selected_period:
                text = f"[{period_name}]"
                attr = curses.A_REVERSE | curses.A_BOLD
            else:
                text = f" {period_name} "
                attr = curses.A_NORMAL

            safe_addstr(self.stdscr, 2, x, text, attr)
            x += len(period_name) + 4

    def draw_summary_table(self):
        """Draw summary table with project hours."""
        h, w = self.stdscr.getmaxyx()

        start_y = 5
        start_x = 5

        # Verificar se tem espaço suficiente
        min_width = 60
        if w < min_width or h < 10:
            msg = "Terminal muito pequeno para relatórios"
            safe_addstr(self.stdscr, h // 2, max(0, (w - len(msg)) // 2), msg)
            return

        # Table header
        safe_addstr(self.stdscr, start_y, start_x, "┌" + "─" * 40 + "┬" + "─" * 15 + "┐")
        safe_addstr(self.stdscr, start_y + 1, start_x, "│ Projeto" + " " * 32 + "│ Horas Totais  │")
        safe_addstr(self.stdscr, start_y + 2, start_x, "├" + "─" * 40 + "┼" + "─" * 15 + "┤")

        # Data rows
        row = start_y + 3
        total_hours = 0.0

        for item in self.summary_data:
            if row >= h - 8:
                break

            project_name = item["project_name"][:38]
            hours = item["total_hours"]
            total_hours += hours

            hours_str = f"{int(hours):02d}:{int((hours % 1) * 60):02d}"
            safe_addstr(self.stdscr, row, start_x, f"│ {project_name:<38} │ {hours_str:>13} │")
            row += 1

        # Bottom border
        if row < h - 6:
            safe_addstr(self.stdscr, row, start_x, "├" + "─" * 40 + "┼" + "─" * 15 + "┤")
            row += 1

            # Total
            total_str = f"{int(total_hours):02d}:{int((total_hours % 1) * 60):02d}"
            safe_addstr(self.stdscr, row, start_x,
                       f"│ TOTAL" + " " * 33 + f"│ {total_str:>13} │",
                       curses.A_BOLD)
            row += 1

            safe_addstr(self.stdscr, row, start_x, "└" + "─" * 40 + "┴" + "─" * 15 + "┘")

    def draw_bar_chart(self):
        """Draw simple ASCII bar chart."""
        h, w = self.stdscr.getmaxyx()

        if not self.summary_data:
            return

        start_y = h - 15
        if start_y < 15 or w < 70:
            return

        start_x = 5

        # Title
        safe_addstr(self.stdscr, start_y, start_x, "Distribuição de Horas:", curses.A_BOLD)
        start_y += 2

        # Find max hours for scaling
        max_hours = max((item["total_hours"] for item in self.summary_data), default=0)
        if max_hours == 0:
            return

        max_bar_width = min(40, w - start_x - 30)

        for item in self.summary_data[:5]:  # Show top 5
            if start_y >= h - 5:
                break

            project_name = item["project_name"][:20]
            hours = item["total_hours"]

            # Calculate bar width
            bar_width = int((hours / max_hours) * max_bar_width)
            bar = "█" * bar_width

            # Nome do projeto
            safe_addstr(self.stdscr, start_y, start_x, f"{project_name:<20} ")

            # Barra
            if curses.has_colors():
                safe_addstr(self.stdscr, start_y, start_x + 21, bar, curses.color_pair(2))
            else:
                safe_addstr(self.stdscr, start_y, start_x + 21, bar)

            # Horas
            hours_str = f" {hours:.1f}h"
            safe_addstr(self.stdscr, start_y, start_x + 21 + bar_width + 1, hours_str)

            start_y += 1

    def draw_footer(self):
        """Draw compact footer with options."""
        h, w = self.stdscr.getmaxyx()

        shortcuts = "←→:Período  E:Exportar  ESC:Voltar"

        self.stdscr.attron(curses.A_REVERSE | curses.A_DIM)
        x_pos = max(0, (w - len(shortcuts)) // 2)
        safe_addstr(self.stdscr, h - 1, x_pos, shortcuts)
        self.stdscr.attroff(curses.A_REVERSE | curses.A_DIM)

    def render(self):
        """Render the report screen."""
        self.stdscr.clear()
        self.refresh_data()
        self.draw_header()
        self.draw_period_selector()
        self.draw_summary_table()
        self.draw_bar_chart()
        self.draw_footer()
        self.stdscr.refresh()

    def handle_key(self, key) -> Optional[str]:
        """
        Handle keyboard input.

        Returns:
            'back' to return to main screen, None otherwise
        """
        # Arrow keys for period selection
        if key == curses.KEY_LEFT:
            self.selected_period = (self.selected_period - 1) % len(self.period_options)
            return None

        elif key == curses.KEY_RIGHT:
            self.selected_period = (self.selected_period + 1) % len(self.period_options)
            return None

        # Export
        elif key in [ord('e'), ord('E')]:
            self.export_report()
            return None

        # Back
        elif key in [27, ord('q'), ord('Q')]:  # ESC or Q
            return 'back'

        return None

    def export_report(self):
        """Export current report to CSV."""
        try:
            start_date, end_date = self._get_period_dates(self.selected_period)
            filepath = self.exporter.export_summary_to_csv(
                self.summary_data,
                start_date,
                end_date
            )

            # Show success message
            h, w = self.stdscr.getmaxyx()
            msg = f"Relatório exportado: {filepath.name}"
            self.stdscr.addstr(h - 4, (w - len(msg)) // 2, msg,
                             curses.A_BOLD | curses.A_REVERSE)
            self.stdscr.refresh()
            curses.napms(2000)  # Show for 2 seconds

        except Exception as e:
            # Show error
            h, w = self.stdscr.getmaxyx()
            msg = f"Erro ao exportar: {str(e)}"
            self.stdscr.addstr(h - 4, (w - len(msg)) // 2, msg,
                             curses.A_BOLD | curses.color_pair(4))
            self.stdscr.refresh()
            curses.napms(2000)
