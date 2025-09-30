import logging
import os

from .components.checkbox import CheckboxGroupBuilder
from misc.config import AppConfig
from .components.interactive import InteractiveComponentTuple
from .game_view import GameView
from misc.sound_player import SoundPlayer
from misc.app_utils import singleton
from views.components.slider import SliderGroupBuilder
from controllers.controller import GameController
from controllers.keyboard import Keyboard

import arcade
import arcade.gui


app_config = AppConfig()

logger = logging.getLogger(__name__)

BUTTON_WIDTH = app_config.WINDOW_WIDTH//4
BUTTON_HEIGHT = app_config.WINDOW_HEIGHT//15
SLIDER_WIDTH = app_config.WINDOW_WIDTH//3.5
CHECKBOX_LABEL_WIDTH = 50
CHECKBOX_SIZE = (20,20)


@singleton
class PreferencesView(arcade.View):
    def __init__(self, w: arcade.Window = None,  main_view = None):
        super().__init__()

        self.window = w

        logger.debug("Выполнение функции __init__")

        self.interactive_components: InteractiveComponentTuple | None = None

        self.manager = arcade.gui.UIManager()

        self.sound_player = SoundPlayer()

        self.keyboard = Keyboard()
        self.controller = GameController()

        sound_vol_slider = SliderGroupBuilder().set_text_label(
            "Громкость эффектов"
        ).set_value_min(0).set_value_max(1).set_step(0.1).set_default_value(app_config.VOLUME_SOUND).build()

        music_vol_slider = SliderGroupBuilder().set_text_label(
            "Громкость музыки"
        ).set_value_min(0).set_value_max(1).set_step(0.1).set_default_value(app_config.VOLUME_MUSIC).build()

        timer_checkbox_group, timer_checkbox = CheckboxGroupBuilder().set_on_texture(
            "data/misc/grey_check.png"
        ).set_off_texture(
            "data/misc/empty.png"
        ).set_text_label(
            "Игра с таймером"
        ).set_value(
            app_config.TIMER_ON
        ).build()

        fullscreen_checkbox_group, fullscreen_checkbox = CheckboxGroupBuilder().set_on_texture(
            "data/misc/grey_check.png"
        ).set_off_texture(
            "data/misc/empty.png"
        ).set_text_label(
            "Полный экран"
        ).set_value(
            app_config.FULLSCREEN
        ).build()

        vsync_checkbox_group, vsync_checkbox = CheckboxGroupBuilder().set_on_texture(
            "data/misc/grey_check.png"
        ).set_off_texture(
            "data/misc/empty.png"
        ).set_text_label(
            "Вертикальная синхронизация"
        ).set_value(
            app_config.VSYNC
        ).build()

        @music_vol_slider[1].event("on_change")
        def on_change_music_vol(event = None):
            logger.debug(f"Изменено значение громкости музыки: {music_vol_slider[1].value}")
            self.sound_player.music_vol = music_vol_slider[1].value

        @sound_vol_slider[1].event("on_change")
        def on_change_sound_vol(event = None):
            logger.debug(f"Изменено значение громкости звуков: {sound_vol_slider[1].value}")
            self.sound_player.sound_vol = sound_vol_slider[1].value

        return_button = arcade.gui.UIFlatButton(text="Назад", width=BUTTON_WIDTH, height=BUTTON_HEIGHT)

        @return_button.event("on_click")
        def on_click_return_button(event = None):
            logger.debug("Нажата кнопка 'Назад'")
            self.window.show_view(main_view)

        @timer_checkbox.event("on_click")
        def on_click_timer_checkbox(event = None):
            logger.debug(f"Вызов обработчика чекбокса таймера. Состояние чекбокса: {app_config.TIMER_ON}")
            app_config.TIMER_ON = not app_config.TIMER_ON
            logger.debug(f"Вызов обработчика чекбокса таймера. Новое состояние чекбокса: {app_config.TIMER_ON}")

        @fullscreen_checkbox.event("on_click")
        def on_click_fullscreen_checkbox(event = None):
            if not self.window.fullscreen:
                app_config.WINDOW_WIDTH, app_config.WINDOW_HEIGHT = arcade.window_commands.get_display_size()
            self.window.set_fullscreen(not self.window.fullscreen, width=app_config.WINDOW_WIDTH, height=app_config.WINDOW_HEIGHT)
            if not self.window.fullscreen:
                app_config.WINDOW_WIDTH, app_config.WINDOW_HEIGHT = int(os.environ.get("WINDOW_WIDTH")), int(os.environ.get("WINDOW_HEIGHT"))
                self.window.set_size(
                    app_config.WINDOW_WIDTH,
                    app_config.WINDOW_HEIGHT
                )

        @vsync_checkbox.event("on_click")
        def on_click_vsync_checkbox(event=None):
            logger.debug(f"vsync current state: {self.window.vsync}")
            self.window.set_vsync(not self.window.vsync)
            logger.debug(f"vsync set to: {self.window.vsync}")

        def on_switch_timer_checkbox(event = None):
            on_click_timer_checkbox()
            timer_checkbox.value = not timer_checkbox.value

        def on_switch_fullscreen_checkbox(event = None):
            on_click_fullscreen_checkbox()
            fullscreen_checkbox.value = not fullscreen_checkbox.value

        def on_switch_vsync_checkbox(event = None):
            on_click_vsync_checkbox()
            vsync_checkbox.value = not vsync_checkbox.value

        self.grid = arcade.gui.UIGridLayout(
            column_count=1, row_count=6, horizontal_spacing=5, vertical_spacing=30
        )

        self.interactive_components = InteractiveComponentTuple(
            (
                (sound_vol_slider[1], on_change_sound_vol),
                (music_vol_slider[1], on_change_music_vol),
                (timer_checkbox, on_switch_timer_checkbox),
                (fullscreen_checkbox, on_switch_fullscreen_checkbox),
                (vsync_checkbox, on_switch_vsync_checkbox),
                (return_button, on_click_return_button)
            )
        )

        self.grid.add(sound_vol_slider[0], 0, 0)
        self.grid.add(music_vol_slider[0], 0, 1)
        self.grid.add(timer_checkbox_group, 0, 2)
        self.grid.add(fullscreen_checkbox_group, 0,3)
        self.grid.add(vsync_checkbox_group, 0, 4)
        self.grid.add(return_button, 0, 5)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-80,
            child=self.grid,
        )

        self.main_view = main_view


    def on_show_view(self) -> None:
        logger.debug("Выполнение функции on_show_view")
        self.window.background_color = app_config.MENU_BACKGROUND_COLOR
        self.manager.enable()

    def on_hide_view(self) -> None:
        logger.debug("Выполнение функции on_hide_view")
        self.manager.disable()

    def on_draw(self) -> bool | None:
        """Render the screen."""
        # Clear the screen
        self.clear()
        text_list = [arcade.Text(
            "Приключения кошки Сони",
            x=app_config.WINDOW_WIDTH / 2,
            y=app_config.WINDOW_HEIGHT / 4 * 3,
            color=arcade.csscolor.WHITE,
            font_size=app_config.WINDOW_HEIGHT//20,
            anchor_x="center"
        ),]

        for text in text_list:
            text.draw()
        # Draw the manager.
        self.manager.draw()

    def on_key_press(self, key: int, modifiers: int) -> bool | None:
        self.keyboard.on_key_press(key, modifiers)

    def on_update(self, delta_time: float) -> bool | None:
        self.interactive_components.update()
