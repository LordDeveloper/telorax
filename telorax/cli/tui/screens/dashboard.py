from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Static

from telorax import __version__
from telorax.cli.tui.widgets.footer import NavigationFooter
from telorax.cli.tui.widgets.header_logo import HeaderLogo
from telorax.cli.tui.widgets.menu_list import MenuList
from telorax.cli.tui.widgets.status_panel import StatusPanel


class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Vertical(
            HeaderLogo(),
            Static(f'[dim]Telegram Account Automation Platform · v{__version__}[/]'),
            StatusPanel(),
            MenuList(),
            NavigationFooter(),
            id='dashboard',
        )
