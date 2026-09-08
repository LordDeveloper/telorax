from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from telorax.cli.tui.screens.dashboard import DashboardScreen


class TeloraxApp(App):
    TITLE = 'Telorax'
    CSS_PATH = 'theme.tcss'

    BINDINGS = [
        Binding('q', 'quit', 'Exit'),
        Binding('escape', 'back', 'Back'),
    ]

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())

    def action_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()


def run_dashboard() -> None:
    TeloraxApp().run()
