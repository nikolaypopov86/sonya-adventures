import logging

from .components.checkbox import CheckboxGroupBuilder
from misc.config import AppConfig
from .components.interactive import InteractiveComponentTuple
from .game_view import GameView
from misc.sound_player import SoundPlayer
from misc.app_utils import singleton
from views.components.slider import SliderGroupBuilder

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
    def __init__(self, main_view):
        super().__init__()
        logger.debug("Выполнение функции __init__")

        self.interactive_components: InteractiveComponentTuple | None = None

        self.manager = arcade.gui.UIManager()

        self.sound_player = SoundPlayer()

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

        @timer_checkbox.event("on_change")
        def on_click_timer_checkbox(event = None):
            logger.debug(f"Вызов обработчика чекбокса таймера. Состояние чекбокса: {app_config.TIMER_ON}")
            app_config.TIMER_ON = not app_config.TIMER_ON
            timer_checkbox.value = not timer_checkbox.value
            logger.debug(f"Вызов обработчика чекбокса таймера. Новое состояние чекбокса: {app_config.TIMER_ON}")


        self.grid = arcade.gui.UIGridLayout(
            column_count=1, row_count=4, horizontal_spacing=5, vertical_spacing=30
        )

        self.interactive_components = InteractiveComponentTuple(
            (
                (sound_vol_slider[1], on_change_sound_vol),
                (music_vol_slider[1], on_change_music_vol),
                (timer_checkbox, on_click_timer_checkbox),
                (return_button, on_click_return_button)
            )
        )

        self.grid.add(sound_vol_slider[0], 0, 0)
        self.grid.add(music_vol_slider[0], 0, 1)
        self.grid.add(timer_checkbox_group, 0, 2)
        self.grid.add(return_button, 0, 3)

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
            y=app_config.WINDOW_HEIGHT / 3 * 2,
            color=arcade.csscolor.WHITE,
            font_size=app_config.WINDOW_HEIGHT//20,
            anchor_x="center"
        ),]

        for text in text_list:
            text.draw()
        # Draw the manager.
        self.manager.draw()

    def on_key_press(self, key: int, modifiers: int) -> bool | None:
        logger.debug(f"Выполнение функции on_key_press. Нажата клавиша {key} с модификаторами {modifiers}")
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()

            self.window.show_view(game_view)

    def on_update(self, delta_time: float) -> bool | None:
        self.interactive_components.update()
