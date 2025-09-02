import logging

from config import AppConfig
from .game_view import GameView
from sound_player import SoundPlayer

import arcade
import arcade.gui


app_config = AppConfig()

logger = logging.getLogger(__name__)

BUTTON_WIDTH = app_config.WINDOW_WIDTH//4
BUTTON_HEIGHT = app_config.WINDOW_HEIGHT//15
SLIDER_WIDTH = app_config.WINDOW_WIDTH//3.5


class PreferencesView(arcade.View):
    def __init__(self, main_view):
        super().__init__()
        logger.debug("Выполнение функции __init__")

        self.manager = arcade.gui.UIManager()

        self.sound_player = SoundPlayer()

        sound_vol_slider_label = arcade.gui.UILabel(
            text="Громкость эффектов",
            width=BUTTON_WIDTH,
            text_color=(255,255,255),
            font_size=6 * app_config.SPRITE_SCALING_TILES
        )
        sound_vol_slider = arcade.gui.UISlider(
            value=self.sound_player.sound_vol,
            min_value=0,
            max_value=1,
            width=SLIDER_WIDTH,
            step=0.1
        )

        music_vol_slider_label = arcade.gui.UILabel(
            text="Громкость музыки",
            width=BUTTON_WIDTH,
            text_color=(255, 255, 255),
            font_size=6 * app_config.SPRITE_SCALING_TILES
        )
        music_vol_slider = arcade.gui.UISlider(
            value=self.sound_player.music_vol,
            min_value=0,
            max_value=1,
            width=SLIDER_WIDTH,
            step=0.1
        )

        @music_vol_slider.event("on_change")
        def on_change_music_vol(event):
            logger.debug(f"Изменено значение громкости музыки: {music_vol_slider.value}")
            self.sound_player.music_vol = music_vol_slider.value

        @sound_vol_slider.event("on_change")
        def on_change_sound_vol(event):
            logger.debug(f"Изменено значение громкости звуков: {sound_vol_slider.value}")
            self.sound_player.sound_vol = sound_vol_slider.value

        return_button = arcade.gui.UIFlatButton(text="Назад", width=BUTTON_WIDTH, height=BUTTON_HEIGHT)

        @return_button.event("on_click")
        def on_click_return_button(event):
            logger.debug("Нажата кнопка 'Назад'")
            self.window.show_view(main_view)

        self.grid = arcade.gui.UIGridLayout(
            column_count=1, row_count=5, horizontal_spacing=20, vertical_spacing=20
        )

        self.grid.add(music_vol_slider_label, 0, 0)
        self.grid.add(music_vol_slider, 0, 1)
        self.grid.add(sound_vol_slider_label, 0, 2)
        self.grid.add(sound_vol_slider, 0, 3)
        self.grid.add(return_button, 0, 4)

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
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
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

