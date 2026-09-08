from __future__ import annotations

from textual.widgets import Static

from telorax import __version__


class StatusPanel(Static):
    DEFAULT_CSS = '''
    StatusPanel {
        border: solid $primary;
        padding: 1 2;
        margin: 1 0;
    }
    '''

    def on_mount(self) -> None:
        self.update(self._render())

    def _render(self) -> str:
        return f'''[cyan]Version[/]        v{__version__}
[cyan]Server[/]         [green]● Running[/]
[cyan]Worker[/]         [green]● Idle[/]
[cyan]Database[/]       [yellow]● Not checked[/]
[cyan]Redis[/]          [yellow]● Not checked[/]
[cyan]Operational Accounts[/] 0
[cyan]Queued Campaigns[/]     0
[cyan]Rate Limited[/]        0'''
