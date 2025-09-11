import logging

from arcade import Camera2D

from base.camera import PlayerCamera
from entities.minimap import MiniMap
from views.components.game_ui import GameUI
from misc.config import AppConfig
from controllers.controller import GameController
from controllers.keyboard import Keyboard
from base.level import Level

import arcade
from pyglet.event import EVENT_HANDLE_STATE

app_config = AppConfig()
logger = logging.getLogger(__name__)


class GameView(arcade.View):
    """Main Window"""

    def __init__(
            self,
            window: arcade.Window = None,
            frm = None):
        super().__init__(window)

        self.__from = frm

        self.level = Level(window, frm, self)

        self.next_lvl: bool = True

        # Camera
        self.camera: PlayerCamera | None = None
        self.gui_camera: arcade.Camera2D | None = None

        self.keyboard: Keyboard  | None = None
        self.main_controller: GameController | None = None

        self.minimap: MiniMap | None = None

        self.game_ui: GameUI | None = None


    def setup(self):
        self.level.setup()

        logger.debug(f"!self.level={self.level}")

        self.minimap = MiniMap()
        self.minimap.setup((self.level.map_width, self.level.map_height))
        self.main_controller = GameController()
        self.keyboard = Keyboard()

        self.camera = PlayerCamera(self.level.map_width, self.level.map_height, self.level.player_sprite)
        self.gui_camera = Camera2D()

        self.game_ui = GameUI()
        self.game_ui.init(
            self.level.score,
            self.level.life_points,
            self.level.coin_total,
            self.level.coin_count,
            self.level.lvl,
            self.level.timer.left_text(),
            self.level.fruit_total,
            self.level.fruit_count
        )

    def on_key_press(self, key, modifiers):
        self.keyboard.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.keyboard.on_key_release(key, modifiers)

    def on_update(self, delta_time):

        if self.main_controller.controls["map"]:
            self.minimap.minimap_on = not self.minimap.minimap_on
            self.main_controller.controls["map"] = False

        if self.main_controller.controls["select"]:
            logger.info(f"select control's state is true. return to menu!")
            self._return_to_menu()

        self.level.update(delta_time)

        self.game_ui.update(
            self.level.score,
            self.level.life_points,
            self.level.coin_total,
            self.level.coin_count,
            self.level.lvl,
            self.level.timer.left_text(),
            self.level.fruit_total,
            self.level.fruit_count
        )

        self.minimap.sprite_lists = tuple(self.level.scene[key] for key in app_config.MINIMAP_SPRITE_LISTS)
        self.minimap.update(self.level.player_sprite)

        self.level.physics_engine.move_player()

        self.level.physics_engine.step()
        self.level.physics_engine.rotate_moving(delta_time)

        self.camera.set_position()


    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> EVENT_HANDLE_STATE:
        """ Called whenever the mouse button is clicked. """
        pass

    def on_show_view(self) -> None:
        if app_config.TIMER_ON and self.level.timer:
            self.level.timer.start()

    def on_hide_view(self) -> None:
        self.level.sound_player.stop_playing_music()
        if app_config.TIMER_ON and self.level.timer:
            self.level.timer.pause()
        self.main_controller.controls["select"] = False

    def on_draw(self):
        """Draw everything"""
        self.clear()

        with self.camera.activate():
            self.level.scene.draw()

        with self.gui_camera.activate():
            if self.minimap.minimap_on:
                self.minimap.draw()
                self.minimap.draw_outline()
            for widget in self.game_ui.widgets:
                widget.draw()

    def _return_to_menu(self):
        self.level.sound_player.music_playback.delete()
        self.__from.continue_enabled = True
        self.__from.save_game_state(self)
        self.window.show_view(self.__from)
        self.main_controller.controls["back"] = False
        self.main_controller.controls["start"] = False
