import logging

from controllers.gamepad import Gamepad
from .game_view import GameView
from .pref_view import PreferencesView
from misc.config import AppConfig
from views.components.interactive import InteractiveComponentTuple

import arcade
import arcade.gui
from arcade.gui import UIFlatButton

app_config = AppConfig()

BUTTON_WIDTH = app_config.WINDOW_WIDTH//4
BUTTON_HEIGHT = app_config.WINDOW_HEIGHT//15

logger = logging.getLogger(__name__)


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
        self.gamepad: Gamepad | None = None
        self.interactive_components: InteractiveComponentTuple | None = None
        self.button_focused: int = 0

    def on_show_view(self):
        if self.gamepad is None:
            self.gamepad = Gamepad()

        """This is run once when we switch to this view"""
        logger.debug(f"Выполнение метода on_show_view")
        arcade.set_background_color(app_config.MENU_BACKGROUND_COLOR)

        if self.anchor is not None:
            self.anchor.clear()

        button_list = self.get_buttons()

        continue_button = None
        if self.continue_enabled:
            continue_button = button_list[0]
        new_game_button = button_list[0 + 1 * self.continue_enabled]
        preferences_button = button_list[1 + 1 * self.continue_enabled]
        exit_button = button_list[2 + 1 * self.continue_enabled]

        self.interactive_components = InteractiveComponentTuple(button_list)

        if continue_button is not None:
            @continue_button[0].event("on_click")
            def on_click_continue(event):
                self.on_click_continue()

        @new_game_button[0].event("on_click")
        def on_click(event):
            self.on_click_new_game()

        @preferences_button[0].event("on_click")
        def on_click(event):
            self.on_click_preferences()

        @exit_button[0].event("on_click")
        def on_click_close(event):
            self.on_click_close()

        # Use the anchor to position the button on the screen.
        self.grid = arcade.gui.UIGridLayout(
            x=app_config.WINDOW_WIDTH // 3,
            y=app_config.WINDOW_HEIGHT // 2,
            column_count=1, row_count=4, horizontal_spacing=20, vertical_spacing=20
        )

        for index, button in enumerate(button_list):
            self.grid.add(button[0], 0, row=index)

        logger.debug(f"MainView.continue_enabled={self.continue_enabled}")

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-80,
            child=self.grid,
        )
        # Enable the UIManager when the view is showm.
        self.manager.enable()

    def on_update(self, delta_time: float) -> bool | None:
        self.interactive_components.update()


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

    def on_click_preferences(self):
        """On click handler"""
        pref_view = PreferencesView(self)
        self.window.show_view(pref_view)

    def on_click_new_game(self):
        """On click handler"""
        self.game_state = None
        game_view = GameView(self.window, self)
        game_view.setup()
        self.window.show_view(game_view)

    def on_click_continue(self):
        self.window.show_view(self.game_state)

    def on_click_close(self):
        self.window.close()

    def get_buttons(self) -> tuple[
        tuple[UIFlatButton, None], ...
    ]:
        preferences_button = arcade.gui.UIFlatButton(text="Настройки", width=BUTTON_WIDTH, height=BUTTON_HEIGHT), self.on_click_preferences
        new_game_button = arcade.gui.UIFlatButton(text="Новая игра", width=BUTTON_WIDTH, height=BUTTON_HEIGHT), self.on_click_new_game
        continue_button = arcade.gui.UIFlatButton(text="Продолжить", width=BUTTON_WIDTH, height=BUTTON_HEIGHT), self.on_click_continue if self.continue_enabled else None
        exit_button = arcade.gui.UIFlatButton(text="Выход", width=BUTTON_WIDTH, height=BUTTON_HEIGHT), self.on_click_close

        buttons = (
            continue_button,
            new_game_button,
            preferences_button,
            exit_button
        )

        return buttons if self.continue_enabled else buttons[1:]
