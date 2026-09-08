from textual.widgets import Static


class NavigationFooter(Static):
    DEFAULT_CSS = '''
    NavigationFooter {
        dock: bottom;
        text-align: center;
        color: $text-muted;
        padding: 1 0;
    }
    '''

    def on_mount(self) -> None:
        self.update('↑/↓ move    Enter select    Esc back    q exit')
