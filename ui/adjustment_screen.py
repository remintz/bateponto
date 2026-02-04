"""
Tela de ajustes de tempo do BatePonto.
"""

import curses
from datetime import datetime, timedelta
from typing import Optional, List
from core.project_manager import ProjectManager
from core.time_tracker import TimeTracker


def safe_addstr(window, y: int, x: int, text: str, *args):
    """Adiciona string com tratamento de erros para evitar crashes do curses."""
    try:
        h, w = window.getmaxyx()
        if y < 0 or y >= h or x < 0 or x >= w:
            return
        max_len = w - x - 1
        if max_len <= 0:
            return
        truncated_text = text[:max_len] if len(text) > max_len else text
        window.addstr(y, x, truncated_text, *args)
    except curses.error:
        pass


class AdjustmentScreen:
    """Tela para visualizar e editar ajustes de tempo por dia."""

    DAYS_PER_PAGE = 7
    WEEKDAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]

    def __init__(
        self,
        stdscr,
        project_manager: ProjectManager,
        time_tracker: TimeTracker
    ):
        self.stdscr = stdscr
        self.project_manager = project_manager
        self.time_tracker = time_tracker

        self.projects: List[dict] = []
        self.selected_project_index = 0
        self.selected_day_index = 0
        self.current_page = 0
        self.days_data: List[dict] = []

        self.edit_mode = False
        self.edit_buffer = ""

        self.message = ""
        self.message_color = 0

        self._init_colors()
        self.refresh_projects()

    def _init_colors(self):
        """Initialize color pairs."""
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Header/Success
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)     # Selected
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Normal
            curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Warning
            curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)      # Error/Negative
            curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Footer

    def refresh_projects(self):
        """Refresh project list."""
        self.projects = self.project_manager.get_active_projects()
        if self.selected_project_index >= len(self.projects):
            self.selected_project_index = max(0, len(self.projects) - 1)
        self.refresh_days_data()

    def refresh_days_data(self):
        """Refresh days data for selected project."""
        if not self.projects:
            self.days_data = []
            return

        project = self.projects[self.selected_project_index]
        project_id = project["id"]

        # Generate last 60 days of data
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.days_data = []

        for i in range(60):  # 60 days back
            day = today - timedelta(days=i)
            day_start = day
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)

            # Get breakdown for this day
            raw_time, adjustment_minutes = self.time_tracker.calculate_project_time_breakdown(
                project_id, day_start, day_end
            )

            self.days_data.append({
                "date": day,
                "date_str": day.strftime("%Y-%m-%d"),
                "weekday": self.WEEKDAYS_PT[day.weekday()],
                "raw_time": raw_time,
                "adjustment": adjustment_minutes
            })

        # Reset selection if out of bounds
        max_index = len(self.days_data) - 1
        if self.selected_day_index > max_index:
            self.selected_day_index = 0
            self.current_page = 0

    def get_current_page_days(self) -> List[dict]:
        """Get days for current page."""
        start = self.current_page * self.DAYS_PER_PAGE
        end = start + self.DAYS_PER_PAGE
        return self.days_data[start:end]

    def get_total_pages(self) -> int:
        """Get total number of pages."""
        if not self.days_data:
            return 1
        return (len(self.days_data) + self.DAYS_PER_PAGE - 1) // self.DAYS_PER_PAGE

    def draw_header(self):
        """Draw header."""
        h, w = self.stdscr.getmaxyx()

        title = "AJUSTES DE TEMPO"
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        else:
            self.stdscr.attron(curses.A_BOLD)

        x_pos = max(0, (w - len(title)) // 2)
        safe_addstr(self.stdscr, 1, x_pos, title)

        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        else:
            self.stdscr.attroff(curses.A_BOLD)

    def draw_project_selector(self):
        """Draw project selector with navigation."""
        h, w = self.stdscr.getmaxyx()

        if not self.projects:
            safe_addstr(self.stdscr, 3, 2, "Nenhum projeto ativo")
            return

        project = self.projects[self.selected_project_index]
        total = len(self.projects)
        current = self.selected_project_index + 1

        # Format: "Projeto: <- [Nome do Projeto] -> (1/6)"
        project_text = f"Projeto: <- [{project['name']}] -> ({current}/{total})"
        x_pos = max(0, (w - len(project_text)) // 2)

        if curses.has_colors():
            safe_addstr(self.stdscr, 3, x_pos, "Projeto: <- [")
            safe_addstr(self.stdscr, 3, x_pos + 13, project['name'], curses.color_pair(2) | curses.A_BOLD)
            safe_addstr(self.stdscr, 3, x_pos + 13 + len(project['name']), f"] -> ({current}/{total})")
        else:
            safe_addstr(self.stdscr, 3, x_pos, project_text)

    def draw_table_header(self):
        """Draw table header."""
        h, w = self.stdscr.getmaxyx()
        y = 5

        # Column headers
        header = "    Data           Dia    Tempo Trabalhado    Ajuste (min)    Final"
        separator = "-" * 72

        safe_addstr(self.stdscr, y, 2, header, curses.A_BOLD)
        safe_addstr(self.stdscr, y + 1, 2, separator)

    def draw_days_table(self):
        """Draw the days table."""
        h, w = self.stdscr.getmaxyx()
        start_y = 7

        page_days = self.get_current_page_days()
        page_start_index = self.current_page * self.DAYS_PER_PAGE

        for i, day_data in enumerate(page_days):
            y = start_y + i
            if y >= h - 4:
                break

            global_index = page_start_index + i
            is_selected = global_index == self.selected_day_index

            # Format date
            date_formatted = day_data["date"].strftime("%d/%m/%Y")
            weekday = day_data["weekday"]

            # Format raw worked time
            raw_seconds = int(day_data["raw_time"].total_seconds())
            raw_str = self._format_time(raw_seconds)

            # Format adjustment
            adj = day_data["adjustment"]
            if self.edit_mode and is_selected:
                adj_str = f"[{self.edit_buffer}_]"
            elif adj != 0:
                adj_str = f"{adj:+d}"
            else:
                adj_str = "0"

            # Format final time
            final_seconds = raw_seconds + (adj * 60)
            final_str = self._format_time(final_seconds)

            # Build row
            prefix = "->" if is_selected else "  "
            row = f"{prefix}{date_formatted}  ({weekday})       {raw_str:>10}        {adj_str:>8}    {final_str:>8}"

            # Apply styling
            if is_selected:
                if curses.has_colors():
                    attr = curses.color_pair(2) | curses.A_BOLD
                else:
                    attr = curses.A_REVERSE
                safe_addstr(self.stdscr, y, 2, row, attr)
            else:
                safe_addstr(self.stdscr, y, 2, row)

    def _format_time(self, total_seconds: int) -> str:
        """Format seconds as HH:MM."""
        if total_seconds < 0:
            sign = "-"
            total_seconds = abs(total_seconds)
        else:
            sign = ""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{sign}{hours:02d}:{minutes:02d}"

    def draw_page_info(self):
        """Draw page information."""
        h, w = self.stdscr.getmaxyx()
        y = h - 5

        current_page = self.current_page + 1
        total_pages = self.get_total_pages()
        page_info = f"Pagina {current_page}/{total_pages} (PgUp/PgDn para navegar)"

        x_pos = max(0, (w - len(page_info)) // 2)
        safe_addstr(self.stdscr, y, x_pos, page_info)

    def draw_message(self):
        """Draw message if any."""
        if self.message:
            h, w = self.stdscr.getmaxyx()
            y = h - 4
            x = max(0, (w - len(self.message)) // 2)

            if curses.has_colors():
                attr = curses.color_pair(self.message_color) | curses.A_BOLD
            else:
                attr = curses.A_BOLD

            safe_addstr(self.stdscr, y, x, self.message, attr)

    def draw_footer(self):
        """Draw footer with shortcuts."""
        h, w = self.stdscr.getmaxyx()
        footer_y = h - 2

        if self.edit_mode:
            shortcuts = "Digite o ajuste (minutos) | ENTER:Salvar | ESC:Cancelar"
        else:
            shortcuts = "LEFT/RIGHT:Projeto | UP/DOWN:Dia | PgUp/PgDn:Pagina | ENTER:Editar | ESC:Voltar"

        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(10) | curses.A_DIM)
        else:
            self.stdscr.attron(curses.A_REVERSE | curses.A_DIM)

        x_pos = max(0, (w - len(shortcuts)) // 2) if len(shortcuts) < w else 0
        safe_addstr(self.stdscr, footer_y, x_pos, shortcuts)

        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(10) | curses.A_DIM)
        else:
            self.stdscr.attroff(curses.A_REVERSE | curses.A_DIM)

    def render(self):
        """Render the adjustment screen."""
        self.stdscr.clear()
        self.draw_header()
        self.draw_project_selector()
        self.draw_table_header()
        self.draw_days_table()
        self.draw_page_info()
        self.draw_message()
        self.draw_footer()
        self.stdscr.refresh()

    def handle_key(self, key: int) -> Optional[str]:
        """Handle keyboard input.

        Returns:
            Optional screen name to switch to, or None to stay
        """
        # Edit mode handling
        if self.edit_mode:
            return self._handle_edit_key(key)

        # Normal mode
        if key == 27:  # ESC
            return "main"

        elif key == curses.KEY_LEFT:
            # Previous project
            if self.projects:
                self.selected_project_index = (self.selected_project_index - 1) % len(self.projects)
                self.selected_day_index = 0
                self.current_page = 0
                self.refresh_days_data()

        elif key == curses.KEY_RIGHT:
            # Next project
            if self.projects:
                self.selected_project_index = (self.selected_project_index + 1) % len(self.projects)
                self.selected_day_index = 0
                self.current_page = 0
                self.refresh_days_data()

        elif key == curses.KEY_UP:
            # Previous day
            if self.days_data and self.selected_day_index > 0:
                self.selected_day_index -= 1
                # Check if we need to change page
                if self.selected_day_index < self.current_page * self.DAYS_PER_PAGE:
                    self.current_page = max(0, self.current_page - 1)

        elif key == curses.KEY_DOWN:
            # Next day
            if self.days_data and self.selected_day_index < len(self.days_data) - 1:
                self.selected_day_index += 1
                # Check if we need to change page
                page_end = (self.current_page + 1) * self.DAYS_PER_PAGE
                if self.selected_day_index >= page_end:
                    self.current_page += 1

        elif key == curses.KEY_PPAGE:  # Page Up
            if self.current_page > 0:
                self.current_page -= 1
                self.selected_day_index = self.current_page * self.DAYS_PER_PAGE

        elif key == curses.KEY_NPAGE:  # Page Down
            if self.current_page < self.get_total_pages() - 1:
                self.current_page += 1
                self.selected_day_index = self.current_page * self.DAYS_PER_PAGE

        elif key in (curses.KEY_ENTER, 10, 13):  # Enter
            if self.days_data:
                self.edit_mode = True
                current_adj = self.days_data[self.selected_day_index]["adjustment"]
                self.edit_buffer = str(current_adj) if current_adj != 0 else ""
                self.message = ""

        return None

    def _handle_edit_key(self, key: int) -> Optional[str]:
        """Handle keyboard input in edit mode."""
        if key == 27:  # ESC - cancel
            self.edit_mode = False
            self.edit_buffer = ""
            self.message = ""

        elif key in (curses.KEY_ENTER, 10, 13):  # Enter - save
            self._save_adjustment()

        elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
            self.edit_buffer = self.edit_buffer[:-1]

        elif 32 <= key <= 126:  # Printable characters
            char = chr(key)
            # Only allow digits and minus sign
            if char in '0123456789':
                self.edit_buffer += char
            elif char == '-' and len(self.edit_buffer) == 0:
                self.edit_buffer = '-'

        return None

    def _save_adjustment(self):
        """Save the current adjustment by adding a new entry to time_entries.json."""
        if not self.projects or not self.days_data:
            self.edit_mode = False
            return

        try:
            new_total = int(self.edit_buffer) if self.edit_buffer and self.edit_buffer != '-' else 0
        except ValueError:
            new_total = 0

        project = self.projects[self.selected_project_index]
        day_data = self.days_data[self.selected_day_index]
        current_adj = day_data["adjustment"]

        # Calculate the difference to add
        diff = new_total - current_adj

        if diff == 0:
            self.message = "Nenhuma alteracao"
            self.message_color = 4  # Yellow
            self.edit_mode = False
            self.edit_buffer = ""
            return

        try:
            # Add a new adjustment entry to time_entries.json
            self.time_tracker.add_adjustment(
                project_id=project["id"],
                minutes=diff,
                description=f"Ajuste manual: {current_adj} -> {new_total}",
                date=day_data["date"].replace(hour=12, minute=0, second=0)  # Meio-dia do dia selecionado
            )

            # Update local data
            day_data["adjustment"] = new_total

            sign = "+" if diff > 0 else ""
            self.message = f"Ajuste de {sign}{diff} min salvo para {day_data['date'].strftime('%d/%m/%Y')}"
            self.message_color = 1  # Green

        except Exception as e:
            self.message = f"Erro ao salvar: {str(e)}"
            self.message_color = 5  # Red

        self.edit_mode = False
        self.edit_buffer = ""
