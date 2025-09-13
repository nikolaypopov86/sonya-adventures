from typing import Callable

from arcade.gui import UIFlatButton


class Button(UIFlatButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.on_click: Callable | None = None

    def click(self):
        self.on_click()
