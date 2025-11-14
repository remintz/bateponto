"""Configuration screen for managing projects with full CRUD."""

import curses
from typing import List, Dict, Any, Optional


class ConfigScreen:
    """Configuration screen for editing projects with full CRUD operations."""

    def __init__(self, stdscr, project_manager, storage):
        """Initialize config screen."""
        self.stdscr = stdscr
        self.project_manager = project_manager
        self.storage = storage

        self.projects: List[Dict[str, Any]] = []
        self.selected_index = 0
        self.mode = "list"  # list, add, edit, delete
        self.edit_field = 0  # Which field is being edited
        self.edit_buffer = {"name": "", "color": "", "active": True}

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

    def draw_project_list(self):
        """Draw list of projects."""
        h, w = self.stdscr.getmaxyx()

        start_y = 2
        start_x = 2

        # Table header
        self.stdscr.addstr(start_y, start_x, "ID   Nome                      Cor       Ativo", curses.A_BOLD)
        self.stdscr.addstr(start_y + 1, start_x, "─" * 50)

        row = start_y + 2

        for i, project in enumerate(self.projects):
            if row >= h - 8:
                break

            project_id = project["id"]
            name = project["name"][:20].ljust(20)
            color = project.get("color", "white").ljust(8)
            active = "Sim" if project.get("active", True) else "Não"

            # Highlight selected
            attr = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL

            try:
                line = f"{project_id:<4} {name} {color} {active}"
                self.stdscr.addstr(row, start_x, line, attr)
                row += 1
            except curses.error:
                break

    def draw_add_edit_form(self):
        """Draw add/edit form."""
        h, w = self.stdscr.getmaxyx()

        title = "Novo Projeto" if self.mode == "add" else "Editar Projeto"
        start_y = h // 2 - 8
        start_x = w // 2 - 25

        # Draw form box
        box_width = 50
        box_height = 12

        try:
            # Background box
            for i in range(box_height):
                self.stdscr.addstr(start_y + i, start_x, " " * box_width, curses.A_REVERSE)

            # Title
            self.stdscr.addstr(start_y + 1, start_x + 2, title, curses.A_REVERSE | curses.A_BOLD)

            # Fields
            fields = [
                ("Nome:", self.edit_buffer["name"]),
                ("Cor:", self.edit_buffer["color"]),
                ("Ativo:", "Sim" if self.edit_buffer["active"] else "Não")
            ]

            for i, (label, value) in enumerate(fields):
                y = start_y + 3 + (i * 2)
                attr = curses.A_REVERSE | curses.A_BOLD if i == self.edit_field else curses.A_REVERSE

                self.stdscr.addstr(y, start_x + 2, label, curses.A_REVERSE)
                self.stdscr.addstr(y, start_x + 12, f"{value:<30}", attr)

            # Instructions
            self.stdscr.addstr(start_y + 10, start_x + 2,
                             "Tab:Próximo  Enter:Salvar  ESC:Cancelar", curses.A_REVERSE | curses.A_DIM)

        except curses.error:
            pass

    def draw_delete_confirm(self):
        """Draw delete confirmation dialog."""
        h, w = self.stdscr.getmaxyx()

        project = self.projects[self.selected_index]
        msg1 = f"Deletar projeto '{project['name']}'?"
        msg2 = "S/N"

        y = h // 2
        self.stdscr.addstr(y, (w - len(msg1)) // 2, msg1, curses.A_REVERSE | curses.A_BOLD)
        self.stdscr.addstr(y + 1, (w - len(msg2)) // 2, msg2, curses.A_REVERSE)

    def draw_footer(self):
        """Draw footer."""
        h, w = self.stdscr.getmaxyx()

        if self.mode == "list":
            shortcuts = "A:Adicionar  E:Editar  D:Deletar  T:Toggle  ESC:Voltar"
        else:
            shortcuts = ""

        try:
            if shortcuts:
                self.stdscr.attron(curses.A_REVERSE | curses.A_DIM)
                x_pos = max(0, (w - len(shortcuts)) // 2)
                self.stdscr.addstr(h - 1, x_pos, shortcuts[:w-1])
                self.stdscr.attroff(curses.A_REVERSE | curses.A_DIM)
        except curses.error:
            pass

    def render(self):
        """Render the config screen."""
        self.stdscr.clear()
        self.refresh_projects()
        self.draw_header()

        if self.mode == "list":
            self.draw_project_list()
            self.draw_footer()
        elif self.mode in ["add", "edit"]:
            self.draw_project_list()  # Show list in background
            self.draw_add_edit_form()
        elif self.mode == "delete":
            self.draw_project_list()
            self.draw_delete_confirm()

        self.stdscr.refresh()

    def handle_key(self, key) -> Optional[str]:
        """Handle keyboard input."""
        if self.mode == "list":
            return self._handle_list_mode(key)
        elif self.mode in ["add", "edit"]:
            return self._handle_form_mode(key)
        elif self.mode == "delete":
            return self._handle_delete_mode(key)

        return None

    def _handle_list_mode(self, key) -> Optional[str]:
        """Handle keys in list mode."""
        # Arrow keys
        if key == curses.KEY_UP:
            self.selected_index = max(0, self.selected_index - 1)

        elif key == curses.KEY_DOWN:
            self.selected_index = min(len(self.projects) - 1, self.selected_index + 1)

        # Add project
        elif key in [ord('a'), ord('A')]:
            self.mode = "add"
            self.edit_field = 0
            self.edit_buffer = {"name": "", "color": "green", "active": True}

        # Edit project
        elif key in [ord('e'), ord('E')]:
            if 0 <= self.selected_index < len(self.projects):
                self.mode = "edit"
                self.edit_field = 0
                project = self.projects[self.selected_index]
                self.edit_buffer = {
                    "id": project["id"],
                    "name": project["name"],
                    "color": project.get("color", "green"),
                    "active": project.get("active", True)
                }

        # Delete project
        elif key in [ord('d'), ord('D')]:
            if 0 <= self.selected_index < len(self.projects):
                self.mode = "delete"

        # Toggle active
        elif key in [ord('t'), ord('T')]:
            if 0 <= self.selected_index < len(self.projects):
                project = self.projects[self.selected_index]
                self.project_manager.toggle_project_active(project["id"])

        # Back
        elif key in [27, ord('q'), ord('Q')]:  # ESC or Q
            return 'back'

        return None

    def _handle_form_mode(self, key) -> Optional[str]:
        """Handle keys in form mode (add/edit)."""
        # Tab - next field
        if key == ord('\t'):
            self.edit_field = (self.edit_field + 1) % 3

        # ESC - cancel
        elif key == 27:
            self.mode = "list"

        # Enter - save
        elif key in [curses.KEY_ENTER, ord('\n'), ord('\r')]:
            self._save_project()
            self.mode = "list"

        # Edit current field
        elif self.edit_field == 0:  # Name field
            self._handle_text_input(key, "name")

        elif self.edit_field == 1:  # Color field
            # Cycle through colors
            if key in [curses.KEY_LEFT, curses.KEY_RIGHT, ord(' ')]:
                current_color = self.edit_buffer["color"]
                try:
                    idx = self.color_options.index(current_color)
                    if key == curses.KEY_LEFT:
                        idx = (idx - 1) % len(self.color_options)
                    else:
                        idx = (idx + 1) % len(self.color_options)
                    self.edit_buffer["color"] = self.color_options[idx]
                except ValueError:
                    self.edit_buffer["color"] = self.color_options[0]

        elif self.edit_field == 2:  # Active field
            if key in [ord(' '), curses.KEY_LEFT, curses.KEY_RIGHT]:
                self.edit_buffer["active"] = not self.edit_buffer["active"]

        return None

    def _handle_delete_mode(self, key) -> Optional[str]:
        """Handle keys in delete confirmation mode."""
        if key in [ord('s'), ord('S'), ord('y'), ord('Y')]:
            # Confirm delete
            project = self.projects[self.selected_index]
            self.project_manager.delete_project(project["id"])
            self.selected_index = max(0, self.selected_index - 1)
            self.mode = "list"

        elif key in [ord('n'), ord('N'), 27]:
            # Cancel
            self.mode = "list"

        return None

    def _handle_text_input(self, key, field_name: str):
        """Handle text input for a field."""
        current_text = self.edit_buffer[field_name]

        if key == curses.KEY_BACKSPACE or key == 127:
            self.edit_buffer[field_name] = current_text[:-1]
        elif 32 <= key <= 126:  # Printable characters
            if len(current_text) < 30:
                self.edit_buffer[field_name] = current_text + chr(key)

    def _save_project(self):
        """Save the project (add or edit)."""
        if not self.edit_buffer["name"].strip():
            return  # Don't save empty names

        if self.mode == "add":
            self.project_manager.create_project(
                name=self.edit_buffer["name"],
                color=self.edit_buffer["color"],
                active=self.edit_buffer["active"]
            )
        elif self.mode == "edit":
            self.project_manager.update_project(
                project_id=self.edit_buffer["id"],
                name=self.edit_buffer["name"],
                color=self.edit_buffer["color"],
                active=self.edit_buffer["active"]
            )
