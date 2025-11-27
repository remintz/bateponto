"""Main screen UI with timer and project buttons."""

import curses
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple


def safe_addstr(stdscr, y: int, x: int, text: str, attr=0, max_width: int = None):
    """Safely add string to screen with bounds checking."""
    try:
        h, w = stdscr.getmaxyx()
        if y >= h or x >= w or y < 0 or x < 0:
            return False

        # Limitar texto ao espaço disponível
        available = w - x - 1
        if max_width:
            available = min(available, max_width)

        if available <= 0:
            return False

        stdscr.addstr(y, x, text[:available], attr)
        return True
    except curses.error:
        return False


class MainScreen:
    """Main screen with clock, timer, and project buttons."""

    def __init__(self, stdscr, project_manager, time_tracker):
        """Initialize main screen."""
        self.stdscr = stdscr
        self.project_manager = project_manager
        self.time_tracker = time_tracker

        self.selected_index = 0
        self.projects: List[Dict[str, Any]] = []
        self.project_times: Dict[str, timedelta] = {}
        self.mouse_enabled = False

        # Color pairs
        self._init_colors()

        # Layout dimensions - compacto para minimizar espaço
        self.header_height = 4  # Reduzido de 5 para 4
        self.footer_height = 1  # Reduzido de 3 para 1 (apenas linha de status)
        self.button_height = 5  # Reduzido de 6 para 5
        self.button_width = 28  # Reduzido de 30 para 28

    def _init_colors(self):
        """Initialize color pairs for curses."""
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()

            # Color pairs: fg, bg
            curses.init_pair(1, curses.COLOR_GREEN, -1)    # Green
            curses.init_pair(2, curses.COLOR_BLUE, -1)     # Blue
            curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Yellow
            curses.init_pair(4, curses.COLOR_RED, -1)      # Red
            curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Magenta
            curses.init_pair(6, curses.COLOR_CYAN, -1)     # Cyan
            curses.init_pair(7, curses.COLOR_WHITE, -1)    # White

            # Special pairs
            curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN)   # Active project
            curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Selected
            curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Header
            curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_RED)    # PAUSED alert

        # Enable mouse
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
            self.mouse_enabled = True
        except:
            pass

    def refresh_projects(self):
        """Refresh project list and times."""
        self.projects = self.project_manager.get_active_projects(limit=5)

        # Get today's times for all projects
        project_ids = [p["id"] for p in self.projects]
        self.project_times = self.time_tracker.get_all_projects_today(project_ids)

    def draw_header(self):
        """Draw compact header with title and clock."""
        h, w = self.stdscr.getmaxyx()

        # Title e data/hora na mesma linha para economizar espaço
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%d/%m")

        title = "BatePonto"
        time_str = f"{current_date} {current_time}"

        # Título à esquerda, hora à direita
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(10) | curses.A_BOLD)
        else:
            self.stdscr.attron(curses.A_BOLD | curses.A_REVERSE)

        safe_addstr(self.stdscr, 0, 1, title)
        if w > len(time_str) + 1:
            safe_addstr(self.stdscr, 0, w - len(time_str) - 1, time_str)

        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(10) | curses.A_BOLD)
        else:
            self.stdscr.attroff(curses.A_BOLD | curses.A_REVERSE)

        # Check if paused - show prominent alert
        if self.time_tracker.is_paused():
            paused_id = self.time_tracker.get_paused_project()
            project = self.project_manager.get_project_by_id(paused_id) if paused_id else None
            pause_duration = self.time_tracker.get_pause_duration()
            pause_str = self.time_tracker.format_timedelta(pause_duration)
            
            if project:
                project_name = project["name"][:15]
                # Blinking effect using time
                blink = int(datetime.now().timestamp() * 2) % 2 == 0
                
                # Line 1: Big PAUSED alert
                alert_line1 = "⏸  CONTAGEM PAUSADA  ⏸"
                # Line 2: Project info and pause duration
                alert_line2 = f"{project_name} | Pausado há {pause_str}"
                # Line 3: Instructions
                alert_line3 = "Pressione ENTER para retomar"
                
                # Draw blinking alert box
                if curses.has_colors():
                    if blink:
                        attr = curses.color_pair(11) | curses.A_BOLD | curses.A_BLINK
                    else:
                        attr = curses.color_pair(4) | curses.A_BOLD  # Red text
                else:
                    attr = curses.A_REVERSE | curses.A_BOLD | (curses.A_BLINK if blink else 0)
                
                # Center and draw alert lines
                x1 = max(0, (w - len(alert_line1)) // 2)
                x2 = max(0, (w - len(alert_line2)) // 2)
                x3 = max(0, (w - len(alert_line3)) // 2)
                
                # Fill background for line 1
                if curses.has_colors() and blink:
                    bg_line = " " * min(w - 2, len(alert_line1) + 4)
                    bg_x = max(0, (w - len(bg_line)) // 2)
                    safe_addstr(self.stdscr, 1, bg_x, bg_line, curses.color_pair(11))
                
                safe_addstr(self.stdscr, 1, x1, alert_line1, attr)
                safe_addstr(self.stdscr, 2, x2, alert_line2, 
                          curses.color_pair(4) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD)
                safe_addstr(self.stdscr, 3, x3, alert_line3,
                          curses.color_pair(3) if curses.has_colors() else curses.A_DIM)

        # Active project timer - compacto em uma linha
        elif self.time_tracker.is_tracking():
            elapsed = self.time_tracker.get_current_elapsed()
            timer_str = self.time_tracker.format_timedelta(elapsed)
            project_id = self.time_tracker.get_current_project()
            project = self.project_manager.get_project_by_id(project_id)

            if project:
                project_name = project["name"][:20]  # Limitar tamanho
                active_str = f"● {project_name} | {timer_str}"

                x_pos = max(0, (w - len(active_str)) // 2)
                if curses.has_colors():
                    safe_addstr(self.stdscr, 1, x_pos, active_str,
                              curses.color_pair(8) | curses.A_BOLD)
                else:
                    safe_addstr(self.stdscr, 1, x_pos, active_str,
                              curses.A_REVERSE | curses.A_BOLD)

    def draw_project_button(self, y: int, x: int, index: int, project: Dict[str, Any]):
        """Draw a project button."""
        is_selected = (index == self.selected_index)
        is_active = (self.time_tracker.get_current_project() == project["id"])

        # Get project time today
        project_time = self.project_times.get(project["id"], timedelta())
        time_str = self.time_tracker.format_timedelta_short(project_time)

        # Button border and content
        width = self.button_width
        height = self.button_height

        # Determine colors
        if curses.has_colors():
            if is_active:
                color = curses.color_pair(8) | curses.A_BOLD
            elif is_selected:
                color = curses.color_pair(9) | curses.A_BOLD
            else:
                color_code = self.project_manager.get_project_color_code(project.get("color", "white"))
                color = curses.color_pair(color_code)
        else:
            if is_active:
                color = curses.A_REVERSE | curses.A_BOLD
            elif is_selected:
                color = curses.A_REVERSE
            else:
                color = curses.A_NORMAL

        # Draw box
        try:
            for i in range(height):
                self.stdscr.addstr(y + i, x, " " * width, color)

            # Border
            self.stdscr.addstr(y, x, "┌" + "─" * (width - 2) + "┐", color)
            for i in range(1, height - 1):
                self.stdscr.addstr(y + i, x, "│", color)
                self.stdscr.addstr(y + i, x + width - 1, "│", color)
            self.stdscr.addstr(y + height - 1, x, "└" + "─" * (width - 2) + "┘", color)

            # Project number and name - compacto
            num_str = f"[{index + 1}]"
            name = project["name"][:width - 6]
            header = f"{num_str} {name}"
            self.stdscr.addstr(y + 1, x + 2, header, color | curses.A_BOLD)

            # Status e tempo na mesma linha
            status = "●" if is_active else "○"
            time_label = f"{status} {time_str}"
            self.stdscr.addstr(y + 3, x + 2, time_label, color)

        except curses.error:
            pass  # Ignore if can't draw (terminal too small)

    def draw_projects(self):
        """Draw all project buttons."""
        h, w = self.stdscr.getmaxyx()

        start_y = self.header_height + 2
        start_x = 5

        # Calculate layout (2 columns for 5 projects, 3 in first column)
        col_width = self.button_width + 5

        for i, project in enumerate(self.projects):
            if i < 3:
                # First column
                y = start_y + (i * (self.button_height + 1))
                x = start_x
            else:
                # Second column
                y = start_y + ((i - 3) * (self.button_height + 1))
                x = start_x + col_width

            self.draw_project_button(y, x, i, project)

    def draw_footer(self):
        """Draw footer with compact keyboard shortcuts."""
        h, w = self.stdscr.getmaxyx()
        footer_y = h - self.footer_height

        # Footer compacto: apenas atalhos essenciais
        shortcuts = "1-5:Projeto  R:Relatórios  A:Ajustes  C:Config  Q:Sair"

        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(10) | curses.A_DIM)
        else:
            self.stdscr.attron(curses.A_REVERSE | curses.A_DIM)

        # Centralizar ou alinhar à esquerda se não couber
        x_pos = max(0, (w - len(shortcuts)) // 2) if len(shortcuts) < w else 0
        safe_addstr(self.stdscr, footer_y, x_pos, shortcuts)

        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(10) | curses.A_DIM)
        else:
            self.stdscr.attroff(curses.A_REVERSE | curses.A_DIM)

    def render(self):
        """Render the entire screen."""
        self.stdscr.clear()
        self.refresh_projects()
        self.draw_header()
        self.draw_projects()
        self.draw_footer()
        self.stdscr.refresh()

    def handle_key(self, key) -> Optional[str]:
        """
        Handle keyboard input.

        Returns:
            Action string or None ('reports', 'config', 'quit')
        """
        # Number keys (1-5)
        if ord('1') <= key <= ord('5'):
            index = key - ord('1')
            if index < len(self.projects):
                self.toggle_project(index)
                return None

        # Arrow keys
        elif key == curses.KEY_UP:
            self.selected_index = (self.selected_index - 1) % len(self.projects)
            return None

        elif key == curses.KEY_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.projects)
            return None

        # Enter or Space
        elif key in [curses.KEY_ENTER, ord('\n'), ord('\r'), ord(' ')]:
            self.toggle_project(self.selected_index)
            return None

        # Commands
        elif key in [ord('r'), ord('R')]:
            return 'reports'

        elif key in [ord('c'), ord('C')]:
            return 'config'

        elif key in [ord('a'), ord('A')]:
            return 'adjustments'

        elif key in [ord('q'), ord('Q')]:
            return 'quit'

        elif key in [ord('p'), ord('P')]:
            # Pause current project
            if self.time_tracker.is_tracking():
                self.time_tracker.stop_project()
            return None

        return None

    def handle_mouse(self, mouse_event) -> Optional[str]:
        """Handle mouse click events."""
        try:
            _, x, y, _, bstate = curses.getmouse()

            if bstate & curses.BUTTON1_CLICKED:
                # Check if click was on a project button
                start_y = self.header_height + 2
                start_x = 5
                col_width = self.button_width + 5

                for i in range(len(self.projects)):
                    if i < 3:
                        btn_y = start_y + (i * (self.button_height + 1))
                        btn_x = start_x
                    else:
                        btn_y = start_y + ((i - 3) * (self.button_height + 1))
                        btn_x = start_x + col_width

                    # Check if click is within button bounds
                    if (btn_y <= y < btn_y + self.button_height and
                        btn_x <= x < btn_x + self.button_width):
                        self.toggle_project(i)
                        return None

        except curses.error:
            pass

        return None

    def toggle_project(self, index: int):
        """Toggle project tracking on/off."""
        if index >= len(self.projects):
            return

        project = self.projects[index]
        project_id = project["id"]

        if self.time_tracker.get_current_project() == project_id:
            # Stop current project
            self.time_tracker.stop_project()
        else:
            # Start this project (will auto-stop current if any)
            self.time_tracker.start_project(project_id)
