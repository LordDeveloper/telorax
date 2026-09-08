from __future__ import annotations

from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

MENU_ITEMS: list[tuple[str, str]] = [
    ('1', 'Setup wizard'),
    ('2', 'Worker engine'),
    ('3', 'Operations'),
    ('4', 'Accounts'),
    ('5', 'Session import'),
    ('6', 'Configuration'),
    ('7', 'Backups'),
    ('8', 'Diagnostics'),
    ('9', 'Statistics'),
    ('10', 'Update telorax'),
    ('11', 'Auth credentials'),
    ('0', 'Exit'),
]


class MenuList(OptionList):
    class Selected(Message):
        def __init__(self, label: str) -> None:
            self.label = label
            super().__init__()

    def on_mount(self) -> None:
        for _key, label in MENU_ITEMS:
            self.add_option(Option(label))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        label = str(event.option.prompt)
        if label == 'Exit':
            self.app.exit()
            return
        self.post_message(self.Selected(label))
