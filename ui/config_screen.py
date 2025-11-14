"""Configuration screen for managing projects."""

import curses
from typing import List, Dict, Any, Optional


class ConfigScreen:
    """Configuration screen for editing projects."""

    def __init__(self, stdscr, project_manager, storage):
        """Initialize config screen."""
        self.stdscr = stdscr
        self.project_manager = project_manager
        self.storage = storage

        self.projects: List[Dict[str, Any]] = []
        self.selected_index = 0

        self.color_options = [
            "green", "blue", "yellow", "red", "magenta", "cyan", "white"
        ]

    def refresh_projects(self):
        """Refresh project list."""
        self.projects = self.project_manager.get_all_projects()

    def draw_header(self):
        """Draw header."""
        h, w = self.stdscr.getmaxyx()

        title = "Configuração de Projetos"
        self.stdscr.attron(curses.A_BOLD | curses.A_REVERSE)
        self.stdscr.addstr(0, (w - len(title)) // 2, title)
        self.stdscr.attroff(curses.A_BOLD | curses.A_REVERSE)

        subtitle = "Edite o arquivo data/projects.json para adicionar/editar projetos"
        self.stdscr.addstr(2, (w - len(subtitle)) // 2, subtitle, curses.A_DIM)

    def draw_project_list(self):
        """Draw list of projects."""
        h, w = self.stdscr.getmaxyx()

        start_y = 5
        start_x = 5

        # Table header
        self.stdscr.addstr(start_y, start_x,
                          "┌" + "─" * 5 + "┬" + "─" * 30 + "┬" + "─" * 12 + "┬" + "─" * 8 + "┐")
        self.stdscr.addstr(start_y + 1, start_x,
                          "│ ID  │ Nome" + " " * 25 + "│ Cor        │ Ativo  │")
        self.stdscr.addstr(start_y + 2, start_x,
                          "├" + "─" * 5 + "┼" + "─" * 30 + "┼" + "─" * 12 + "┼" + "─" * 8 + "┤")

        row = start_y + 3

        for i, project in enumerate(self.projects):
            if row >= h - 10:
                break

            project_id = project["id"]
            name = project["name"][:28]
            color = project.get("color", "white")
            active = "Sim" if project.get("active", True) else "Não"

            # Highlight selected
            attr = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL

            try:
                line = f"│ {project_id:<3} │ {name:<28} │ {color:<10} │ {active:<6} │"
                self.stdscr.addstr(row, start_x, line, attr)
                row += 1
            except curses.error:
                break

        # Bottom border
        if row < h - 8:
            self.stdscr.addstr(row, start_x,
                              "└" + "─" * 5 + "┴" + "─" * 30 + "┴" + "─" * 12 + "┴" + "─" * 8 + "┘")

    def draw_instructions(self):
        """Draw instructions."""
        h, w = self.stdscr.getmaxyx()

        instructions = [
            "",
            "Para editar projetos:",
            "",
            "1. Pressione ESC/Q para sair desta tela",
            "2. Edite o arquivo: data/projects.json",
            "3. Adicione, remova ou edite projetos conforme necessário",
            "4. Reinicie o programa para aplicar as mudanças",
            "",
            "Formato de cada projeto:",
            '  {"id": "p1", "name": "Nome", "color": "green", "active": true}',
            "",
            "Cores disponíveis: green, blue, yellow, red, magenta, cyan, white"
        ]

        start_y = h - len(instructions) - 5
        if start_y < 15:
            start_y = 15

        for i, line in enumerate(instructions):
            if start_y + i >= h - 3:
                break
            try:
                if i == 0 or i == 2 or i == 7:
                    continue
                elif "Formato" in line or "Cores" in line:
                    self.stdscr.addstr(start_y + i, 5, line, curses.A_BOLD)
                elif line.startswith("  {"):
                    if curses.has_colors():
                        self.stdscr.addstr(start_y + i, 5, line, curses.color_pair(6))
                    else:
                        self.stdscr.addstr(start_y + i, 5, line)
                else:
                    self.stdscr.addstr(start_y + i, 5, line)
            except curses.error:
                break

    def draw_footer(self):
        """Draw footer."""
        h, w = self.stdscr.getmaxyx()

        shortcuts = [
            "↑↓: Navegar",
            "T: Toggle Ativo",
            "ESC/Q: Voltar"
        ]

        line = "  |  ".join(shortcuts)

        try:
            self.stdscr.attron(curses.A_REVERSE)
            self.stdscr.addstr(h - 2, (w - len(line)) // 2, line)
            self.stdscr.attroff(curses.A_REVERSE)
        except curses.error:
            pass

    def render(self):
        """Render the config screen."""
        self.stdscr.clear()
        self.refresh_projects()
        self.draw_header()
        self.draw_project_list()
        self.draw_instructions()
        self.draw_footer()
        self.stdscr.refresh()

    def handle_key(self, key) -> Optional[str]:
        """
        Handle keyboard input.

        Returns:
            'back' to return to main screen, None otherwise
        """
        # Arrow keys
        if key == curses.KEY_UP:
            self.selected_index = max(0, self.selected_index - 1)
            return None

        elif key == curses.KEY_DOWN:
            self.selected_index = min(len(self.projects) - 1, self.selected_index + 1)
            return None

        # Toggle active
        elif key in [ord('t'), ord('T')]:
            if 0 <= self.selected_index < len(self.projects):
                project = self.projects[self.selected_index]
                self.project_manager.toggle_project_active(project["id"])
            return None

        # Back
        elif key in [27, ord('q'), ord('Q')]:  # ESC or Q
            return 'back'

        return None
