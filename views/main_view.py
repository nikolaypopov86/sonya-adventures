import logging

from arcade.gui import UIFlatButton

from .game_view import GameView
from .pref_view import PreferencesView
from misc.config import AppConfig

import arcade
import arcade.gui

app_config = AppConfig()

BUTTON_WIDTH = app_config.WINDOW_WIDTH//4
BUTTON_HEIGHT = app_config.WINDOW_HEIGHT//15

logger = logging.getLogger(__name__)

def get_buttons() -> tuple[UIFlatButton, UIFlatButton, UIFlatButton, UIFlatButton]:
    preferences_button = arcade.gui.UIFlatButton(text="Настройки", width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
    new_game_button = arcade.gui.UIFlatButton(text="Новая игра", width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
    continue_button = arcade.gui.UIFlatButton(text="Продолжить", width=BUTTON_WIDTH,height=BUTTON_HEIGHT)
    exit_button = arcade.gui.UIFlatButton(text="Выход", width=BUTTON_WIDTH,height=BUTTON_HEIGHT)

    return (
        preferences_button,
        new_game_button,
        continue_button,
        exit_button
    )



class MainView(arcade.View):
    def __init__(self, _from: arcade.View = None):
        self.continue_enabled = False
        logger.debug(f"Выполнение метода __init__. __from: {_from}")
        super().__init__()
        self._from = _from
        self.manager = arcade.gui.UIManager()
        self.grid: arcade.gui.UIGridLayout | None = None
        self.anchor: arcade.gui.UIAnchorLayout | None = None
        self.game_state: arcade.View | None = None

    def on_show_view(self):
        """This is run once when we switch to this view"""
        logger.debug(f"Выполнение метода on_show_view")
        arcade.set_background_color(app_config.MENU_BACKGROUND_COLOR)

        if self.anchor is not None:
            self.anchor.clear()

        preferences_button, new_game_button, continue_button, exit_button = get_buttons()

        @preferences_button.event("on_click")
        def on_click_preferences_button(event):
            """On click handler"""
            pref_view = PreferencesView(self)
            self.window.show_view(pref_view)

        @new_game_button.event("on_click")
        def on_click_new_game(event):
            """On click handler"""
            self.game_state = None
            game_view = GameView(self.window, self)
            game_view.level = app_config.BASE_LVL
            self.window.show_view(game_view)

        @continue_button.event("on_click")
        def on_click_continue(event):
            self.window.show_view(self.game_state)

        @exit_button.event("on_click")
        def on_click_exit(event):
            self.window.close()

        # Use the anchor to position the button on the screen.
        self.grid = arcade.gui.UIGridLayout(
            x=app_config.WINDOW_WIDTH // 3,
            y=app_config.WINDOW_HEIGHT // 2,
            column_count=1, row_count=4, horizontal_spacing=20, vertical_spacing=20
        )

        self.grid.add(new_game_button, 0, 1)
        self.grid.add(preferences_button, 0, 2)
        self.grid.add(exit_button, 0, 3)

        logger.debug(f"MainView.continue_enabled={self.continue_enabled}")

        if self.continue_enabled:
            self.grid.add(continue_button, 0, 0)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-80,
            child=self.grid,
        )
        # Enable the UIManager when the view is showm.
        self.manager.enable()

    def on_hide_view(self):
        # Disable the UIManager when the view is hidden.
        logger.debug(f"Выполнение метода on_hide_view")
        self.manager.disable()

    def on_draw(self):
        """Render the screen."""
        # Clear the screen
        # logger.debug(f"Выполнение метода on_draw")
        self.clear()
        text_list = [arcade.Text(
            "Приключения кошки Сони",
            x=app_config.WINDOW_WIDTH / 2,
            y=app_config.WINDOW_HEIGHT / 3 * 2,
            color=arcade.csscolor.WHITE,
            font_size=app_config.WINDOW_HEIGHT // 20,
            anchor_x="center"
        ),]

        for text in text_list:
            text.draw()

        # Draw the manager.
        self.manager.draw()

    def save_game_state(self, state: arcade.View):
        self.game_state = state
        logger.debug("Game state saved")

    def enable_continue_button(self, enable: bool=True):
        self.continue_enabled = enable
        logger.debug(f"Continue button {"enabled" if enable else "disabled"}")
