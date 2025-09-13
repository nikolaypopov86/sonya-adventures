import logging
from typing import Callable

from misc.config import AppConfig
from .components.interactive import InteractiveComponentTuple
from controllers.controller import GameController

import arcade
import arcade.gui
from arcade.gui import UIFlatButton

logger = logging.getLogger(__name__)

app_config = AppConfig()

BUTTON_WIDTH = app_config.WINDOW_WIDTH//4
BUTTON_HEIGHT = app_config.WINDOW_HEIGHT//15


def get_text_widget() -> arcade.gui.UILabel:
    text_widget = arcade.gui.UILabel(
        text="TEMPLATE",
        font_size=app_config.WINDOW_HEIGHT//20,
        text_color=arcade.csscolor.WHITE
    )
    return text_widget

class GameOverView(arcade.View):
    def __init__(self, main_menu):
        logger.debug(f"Выполнение метода __init__")
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.grid: arcade.gui.UIGridLayout | None = None
        self.anchor: arcade.gui.UIAnchorLayout | None = None

        self.text_list: list[arcade.Text] | None = None

        self.result: int | None = None

        self.main_menu_view = main_menu

        self.interactive_components: InteractiveComponentTuple | None = None

        self.controller: GameController | None = None



    def on_show_view(self) -> None:
        self.controller = GameController()

        logger.debug(f"Выполнение метода on_show_view")
        arcade.set_background_color(app_config.MENU_BACKGROUND_COLOR)

        self.text_list = [arcade.Text(
            "Кошечка Соня устала и ушла спать",
            x=app_config.WINDOW_WIDTH / 2,
            y=app_config.WINDOW_HEIGHT / 3 * 2,
            color=arcade.csscolor.WHITE,
            font_size=app_config.WINDOW_HEIGHT // 20,
            anchor_x="center"
        ), ]

        if self.anchor is not None:
            self.anchor.clear()

        buttons = self.get_buttons()

        self.interactive_components = InteractiveComponentTuple(buttons)

        menu_button = buttons[0]

        @menu_button[0].event("on_click")
        def on_click_menu_button(event):
            self.show_menu()

        self.grid = arcade.gui.UIGridLayout(
            x=app_config.WINDOW_WIDTH // 3,
            y=app_config.WINDOW_HEIGHT // 2,
            column_count=1, row_count=3, horizontal_spacing=20, vertical_spacing=20
        )

        score_widget = get_text_widget()
        score_widget.text = f"Ваш результат: {self.result}"

        self.grid.add(menu_button[0], 0, 1)
        self.grid.add(score_widget, 0, 0)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-80,
            child=self.grid
        )

        self.manager.enable()

    def on_hide_view(self) -> None:
        logger.debug(f"Выполнение метода on_hide_view")
        self.manager.disable()

    def on_update(self, delta_time: float) -> bool | None:
        self.interactive_components.update()

    def on_draw(self) -> bool | None:
        self.clear()

        for text in self.text_list:
            text.draw()

        # Draw the manager.
        self.manager.draw()

    def set_result(self, value: int):
        self.result = value

    def show_menu(self):
        self.main_menu_view.continue_enabled = False
        self.window.show_view(self.main_menu_view)

    def get_buttons(self) -> tuple[tuple[UIFlatButton, Callable], ...]:
        menu_button = arcade.gui.UIFlatButton(
            text="В меню",
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT
        )
        return (menu_button, self.show_menu),
