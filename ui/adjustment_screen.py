"""
Tela de ajustes de tempo do BatePonto.
"""

import curses
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
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
    """Tela para adicionar ajustes de tempo."""

    def __init__(
        self,
        stdscr,
        project_manager: ProjectManager,
        time_tracker: TimeTracker
    ):
        self.stdscr = stdscr
        self.project_manager = project_manager
        self.time_tracker = time_tracker

        self.selected_project_index = 0
        self.projects = []
        self.input_mode = None  # None, 'minutes', 'description'
        self.input_buffer = ""
        self.minutes = 0
        self.description = ""
        self.message = ""
        self.message_color = 0

        self._init_colors()
        self.refresh_projects()

    def _init_colors(self):
        """Initialize color pairs."""
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Header
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)     # Selected
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Normal
            curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Warning
            curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)      # Error
            curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Footer

    def refresh_projects(self):
        """Refresh project list."""
        self.projects = self.project_manager.get_active_projects()

    def draw_header(self):
        """Draw header."""
        h, w = self.stdscr.getmaxyx()

        title = "AJUSTES DE TEMPO"
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        else:
            self.stdscr.attron(curses.A_BOLD)

        x_pos = max(0, (w - len(title)) // 2)
        safe_addstr(self.stdscr, 0, x_pos, title)

        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        else:
            self.stdscr.attroff(curses.A_BOLD)

        # Instructions
        instructions = "Adicione ajustes positivos (horas extras) ou negativos (descontos)"
        x_pos = max(0, (w - len(instructions)) // 2)
        safe_addstr(self.stdscr, 2, x_pos, instructions)

    def draw_projects(self):
        """Draw project selection."""
        h, w = self.stdscr.getmaxyx()
        start_y = 4

        safe_addstr(self.stdscr, start_y, 2, "Selecione o projeto:")

        for i, project in enumerate(self.projects):
            y = start_y + 2 + i
            if y >= h - 10:  # Leave space for input fields
                break

            prefix = "→ " if i == self.selected_project_index else "  "
            text = f"{prefix}{project['name']}"

            if i == self.selected_project_index:
                if curses.has_colors():
                    attr = curses.color_pair(2) | curses.A_BOLD
                else:
                    attr = curses.A_REVERSE
                safe_addstr(self.stdscr, y, 4, text, attr)
            else:
                safe_addstr(self.stdscr, y, 4, text)

    def draw_input_fields(self):
        """Draw input fields for minutes and description."""
        h, w = self.stdscr.getmaxyx()
        start_y = h - 8

        # Minutes input
        minutes_label = "Minutos (positivo ou negativo):"
        safe_addstr(self.stdscr, start_y, 2, minutes_label)

        if self.input_mode == 'minutes':
            minutes_text = f"[{self.input_buffer}_]"
            if curses.has_colors():
                attr = curses.color_pair(2)
            else:
                attr = curses.A_REVERSE
            safe_addstr(self.stdscr, start_y, len(minutes_label) + 3, minutes_text, attr)
        else:
            minutes_text = f"[{self.minutes}]" if self.minutes != 0 else "[ ]"
            safe_addstr(self.stdscr, start_y, len(minutes_label) + 3, minutes_text)

        # Description input
        desc_label = "Descrição (opcional):"
        safe_addstr(self.stdscr, start_y + 2, 2, desc_label)

        if self.input_mode == 'description':
            desc_text = f"[{self.input_buffer}_]"
            if curses.has_colors():
                attr = curses.color_pair(2)
            else:
                attr = curses.A_REVERSE
            safe_addstr(self.stdscr, start_y + 2, len(desc_label) + 3, desc_text, attr)
        else:
            desc_text = f"[{self.description}]" if self.description else "[ ]"
            safe_addstr(self.stdscr, start_y + 2, len(desc_label) + 3, desc_text)

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

        shortcuts = "↑/↓:Projeto  M:Minutos  D:Descrição  S:Salvar  ESC:Voltar"

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
        self.draw_projects()
        self.draw_input_fields()
        self.draw_message()
        self.draw_footer()
        self.stdscr.refresh()

    def handle_key(self, key: int) -> Optional[str]:
        """Handle keyboard input.

        Returns:
            Optional screen name to switch to, or None to stay
        """
        # In input mode
        if self.input_mode:
            if key == 27:  # ESC
                self.input_mode = None
                self.input_buffer = ""
            elif key in (curses.KEY_ENTER, 10, 13):  # Enter
                if self.input_mode == 'minutes':
                    try:
                        self.minutes = int(self.input_buffer) if self.input_buffer else 0
                        self.message = ""
                    except ValueError:
                        self.message = "Erro: Digite apenas números"
                        self.message_color = 5
                elif self.input_mode == 'description':
                    self.description = self.input_buffer

                self.input_mode = None
                self.input_buffer = ""
            elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                self.input_buffer = self.input_buffer[:-1]
            elif 32 <= key <= 126:  # Printable characters
                if self.input_mode == 'minutes':
                    # Only allow digits and minus sign
                    if chr(key) in '0123456789-':
                        # Only allow minus at the start
                        if chr(key) == '-' and len(self.input_buffer) == 0:
                            self.input_buffer += chr(key)
                        elif chr(key) != '-':
                            self.input_buffer += chr(key)
                else:
                    self.input_buffer += chr(key)
            return None

        # Normal mode
        if key == 27:  # ESC
            return "main"
        elif key == curses.KEY_UP:
            if self.projects:
                self.selected_project_index = (self.selected_project_index - 1) % len(self.projects)
        elif key == curses.KEY_DOWN:
            if self.projects:
                self.selected_project_index = (self.selected_project_index + 1) % len(self.projects)
        elif key in (ord('m'), ord('M')):
            self.input_mode = 'minutes'
            self.input_buffer = str(self.minutes) if self.minutes != 0 else ""
            self.message = ""
        elif key in (ord('d'), ord('D')):
            self.input_mode = 'description'
            self.input_buffer = self.description
            self.message = ""
        elif key in (ord('s'), ord('S')):
            self._save_adjustment()

        return None

    def _save_adjustment(self):
        """Save the adjustment."""
        if not self.projects:
            self.message = "Erro: Nenhum projeto disponível"
            self.message_color = 5
            return

        if self.minutes == 0:
            self.message = "Erro: Digite um valor diferente de zero"
            self.message_color = 5
            return

        project = self.projects[self.selected_project_index]

        try:
            self.time_tracker.add_adjustment(
                project_id=project['id'],
                minutes=self.minutes,
                description=self.description
            )

            sign = "+" if self.minutes > 0 else ""
            self.message = f"Ajuste de {sign}{self.minutes} min salvo para {project['name']}"
            self.message_color = 1  # Green

            # Reset fields
            self.minutes = 0
            self.description = ""

        except Exception as e:
            self.message = f"Erro ao salvar: {str(e)}"
            self.message_color = 5  # Red
