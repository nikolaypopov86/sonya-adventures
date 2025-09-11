import logging
import pprint

from arcade import SpriteList, Scene, TileMap

from entities.coin import CoinList
from base.engine import PhysicsEngine
from entities.fruit import FruitList
from entities.heart import HeartList
from entities.sprites import PlayerSprite
from misc.config import AppConfig
from misc.sound_player import SoundPlayer
from entities.minimap import MiniMap
from handlers import GameController
from controllers.keyboard import Keyboard
from base.camera import PlayerCamera

import arcade

from misc.timer import SimpleTimer
from views.components.game_ui import GameUI
from views.game_over_view import GameOverView

app_config = AppConfig()

from pyglet.event import EVENT_HANDLE_STATE

logger = logging.getLogger(__name__)


class GameView(arcade.View):
    """Main Window"""

    def __init__(
            self,
            window: arcade.Window = None,
            frm = None):
        super().__init__(window)

        self.__from = frm
        self.coin_textures = None
        self.cur_coin_texture: int | None = None
        self.coins_to_find: arcade.Text | None = None

        self.water_list: SpriteList | None = None
        self.foreground: SpriteList | None = None
        self.background: SpriteList | None = None

        # Player sprite
        self.player_sprite: PlayerSprite | None = None

        # Sprite Lists we need
        self.player_list: arcade.SpriteList | None = None
        self.wall_list: arcade.SpriteList | None = None
        self.item_list: arcade.SpriteList | None = None
        self.moving_sprites_list: arcade.SpriteList | None = None
        self.lvl_wall_list: arcade.SpriteList | None = None

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False

        # Physic engine
        self.physics_engine: PhysicsEngine | None = None

        self.music_is_playing: bool = False
        self.sound_player: SoundPlayer = SoundPlayer()

        self.scene: arcade.Scene | None = None
        self.end_of_map = None

        # Camera
        self.camera: PlayerCamera | None = None
        self.gui_camera: arcade.Camera2D | None = None

        # Score
        self.score: int = 0

        # Score text
        self.score_text: arcade.Text | None = None

        # Reset score
        self.reset_score: bool = True

        # Reset map
        self.reset_coin: bool = True

        # Max life points
        self.max_life_points: int = 7
        # Life points
        self.life_points: int = 5
        # Life text
        self.life_text: arcade.Text | None = None

        self.coin_list: CoinList | None = None
        self.coin_total: int | None = None
        self.coin_count: int = 0
        self.reset_coin_max: bool = True

        self.fruit_list: FruitList | None = None
        self.fruit_total: int | None = None
        self.fruit_count: int | None = None
        self.reset_fruit_max: int | None = None
        self.fruit_to_find = None

        self.heart_list: HeartList | None = None

        self.setup_called = False

        self.level: int = app_config.BASE_LVL
        self.level_text: str | None = None

        self.map_width: int | None = None
        self.map_height: int | None = None

        self.minimap: MiniMap | None = None

        self.game_ui = None

        self.timer: SimpleTimer | None = None
        self.timer_text: arcade.Text | None = None

        self.next_lvl: bool = True

        self.keyboard: Keyboard  | None = None
        self.main_controller: GameController | None = None


    def setup(self):
        """Set up everything with the game"""

        logger.debug("enter GameView method setup")

        self.setup_called = True

        self.keyboard = Keyboard()
        self.main_controller = GameController()

        # Create the sprite lists
        self.player_list = arcade.SpriteList()

        __coin_list = None
        __fruit_list = None
        __heart_list = None
        __item_list = None
        if self.scene is not None and "Coins" in self.scene:
            __coin_list = CoinList(self.coin_list)
        if self.scene is not None and "Fruits" in self.scene:
            __fruit_list = FruitList(self.fruit_list)
        if self.scene is not None and "Hearts" in self.scene:
            __heart_list = HeartList(self.heart_list)
        if self.scene is not None and "Items" in self.scene:
            __item_list = self.item_list

        layer_options = {
            "Platforms": {
                "use_spatial_hash": True
            },
            "Water": {
                "use_spatial_hash": True
            }
        }

        map_path = f":data:/maps/map_{self.level}.tmx"

        logger.info(f"map_path: {map_path}")

        # Load in TileMap
        tile_map: TileMap = arcade.load_tilemap(
            map_path,
            scaling=app_config.SPRITE_SCALING_TILES,
            layer_options=layer_options
        )

        logger.info(f"level: {self.level}")

        logger.info(f"map size: {self.map_width} X {self.map_height}")

        self.end_of_map = (tile_map.width * tile_map.tile_width) * tile_map.scaling

        # Pull the sprite layers out of the tile map
        self.scene: Scene = arcade.Scene.from_tilemap(tile_map)

        logger.debug(f"scene: {self.scene.__dict__}")


        self.map_width = tile_map.width * tile_map.tile_width * tile_map.scaling
        self.map_height = tile_map.height * tile_map.tile_height * tile_map.scaling

        if self.reset_coin:
            self.coin_list = CoinList(self.scene["Coins"])
            self.coin_total = len(self.coin_list.obj)
            self.fruit_list = FruitList(self.scene["Fruits"])
            self.fruit_total = len(self.fruit_list.obj)
            self.fruit_count = 0
            self.heart_list = HeartList(self.scene["Hearts"])

        for moving_sprite in self.scene["Moving Sprites"]:
            moving_sprite.boundary_left *= app_config.SPRITE_SCALING_TILES
            moving_sprite.boundary_right *= app_config.SPRITE_SCALING_TILES
            moving_sprite.boundary_top *= app_config.SPRITE_SCALING_TILES
            moving_sprite.boundary_bottom *= app_config.SPRITE_SCALING_TILES


        if not self.reset_coin and __coin_list is not None:
            self.scene.remove_sprite_list_by_name("Coins")
            self.scene.add_sprite_list_before(
                "Coins",
                "Foreground",
                use_spatial_hash=True,
                sprite_list=__coin_list.obj
            )

            self.scene.remove_sprite_list_by_name("Fruits")
            self.scene.add_sprite_list_before(
                "Fruits",
                "Coins",
                use_spatial_hash=True,
                sprite_list=__fruit_list.obj
            )

            self.scene.remove_sprite_list_by_name("Hearts")
            self.scene.add_sprite_list_before(
                "Hearts",
                "Foreground",
                use_spatial_hash=True,
                sprite_list=__heart_list.obj
            )

            logger.debug(pprint.pprint(self.scene.__dict__))
            self.scene.add_sprite_list_before("Items", "Foreground", sprite_list=__item_list)

            self.reset_coin = True

        # Create player sprite
        self.player_sprite = PlayerSprite()
        self.player_sprite.move_to_default_location()

        # Add to player sprite list
        self.player_list.append(self.player_sprite)
        self.scene.add_sprite_list_before("Player", "Foreground")
        self.scene.add_sprite("Player", self.player_sprite)

        # Pymunk Physics Engine Setup
        damping = app_config.DEFAULT_DUMPING
        gravity = (0, -app_config.GRAVITY)

        self.lvl_wall_list = self.scene["Lvl Wall"]

        self.camera = PlayerCamera(self.map_width, self.map_height, self.player_sprite)
        logger.debug(f"camera activate: {self.camera.width}, {self.camera.height}")

        self.gui_camera = arcade.Camera2D()
        logger.debug(f"gui_camera activate: {self.gui_camera.width}, {self.gui_camera.height}")

        self.physics_engine = PhysicsEngine(
            damping=damping,
            gravity=gravity
        )

        self.physics_engine.add_player(
            self.player_sprite
        )

        self.physics_engine.add_platforms(
            self.scene["Platforms"],
        )

        self.physics_engine.add_edges(
            self.scene["Edge"]
        )

        self.physics_engine.add_lvl_walls(
            self.scene["Lvl Wall"]
        )

        self.physics_engine.add_items(
            self.scene["Dynamic Items"],
        )

        self.physics_engine.add_moving_sprites(
            self.scene["Moving Sprites"],
        )

        self.timer = SimpleTimer()
        if self.next_lvl:
            self.timer.set_seconds(tile_map.properties.get("seconds"))
            self.timer.start()
            self.next_lvl = False
            self.coin_count = 0
            self.fruit_count = 0

        self.game_ui = GameUI()
        self.game_ui.init(
            self.score,
            self.life_points,
            self.coin_total,
            len(self.coin_list.obj),
            self.level,
            self.timer.left_text(),
            self.fruit_total,
            len(self.fruit_list.obj)
        )

        if self.reset_score:
            self.score = 0
        self.reset_score = True

        self.minimap = MiniMap()
        self.minimap.setup((self.map_width, self.map_height))

    def on_key_press(self, key, modifiers):
        self.keyboard.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.keyboard.on_key_release(key, modifiers)

    def on_update(self, delta_time):

        if not self.setup_called:
            self.setup()

        if self.main_controller.controls["map"]:
            self.minimap.minimap_on = not self.minimap.minimap_on
            self.main_controller.controls["map"] = False

        if self.main_controller.controls["select"]:
            logger.debug(f"select control's state is true. return to menu!")
            self._return_to_menu()


        if self.player_sprite.center_y < 16:
            if self.life_points <= 0:
                view = GameOverView(self.__from)
                view.set_result(self.score)
                self.sound_player.stop_playing_music()
                self.window.show_view(view)
            self.life_points -= 1
            self.reset_coin = False
            self.reset_score = False
            self.setup()

        if self.timer.is_up():
            view = GameOverView(self.__from)
            view.set_result(self.score)
            self.sound_player.stop_playing_music()
            self.window.show_view(view)

        if self.player_sprite.center_x >= self.end_of_map:
            self.reset_coin_max = True
            self.reset_score = False
            self.next_lvl = True
            self.level += 1
            self.reset_coin = True
            self.setup()

        delta_coin_score, need_coin_to_find, delta_coin_count = self.coin_list.remove_touched(self.player_sprite)
        self.score += delta_coin_score
        self.coin_count += delta_coin_count
        self.coin_list.check_or_update_pic()

        delta_fruit_score, need_fruit_to_find, delta_fruit_count = self.fruit_list.remove_touched(self.player_sprite)
        self.score += delta_fruit_score
        self.fruit_count += delta_fruit_count

        _, _, delta_life_points = self.heart_list.remove_touched(self.player_sprite)
        if self.life_points < self.max_life_points:
            self.life_points += delta_life_points

        self.game_ui.update(
            self.score,
            self.life_points,
            self.coin_total,
            self.coin_count,
            self.level,
            self.timer.left_text(),
            self.fruit_total,
            self.fruit_count
        )

        # TODO: сделать так, чтобы стена исчезала, когда фруктики собраны
        # logger.debug(f"fruit count: {self.fruit_count}, fruit total: {self.fruit_total}")
        if "Lvl Wall" in self.scene and self.fruit_count >= self.fruit_total:
            logger.debug(f"{pprint.pprint(self.scene.__dict__)}")
            logger.info("Lvl Wall removed !")
            self.physics_engine.remove_sprite(self.lvl_wall_list.sprite_list.pop())
            self.scene.remove_sprite_list_by_object(self.lvl_wall_list)
            logger.debug(f"{pprint.pprint(self.scene.__dict__)}")
            self.scene.update(delta_time)

        self.minimap.sprite_lists = tuple(self.scene[key] for key in app_config.MINIMAP_SPRITE_LISTS)
        self.minimap.update(self.player_sprite)

        self.physics_engine.move_player()

        self.camera.set_position()

        self.physics_engine.step()
        self.physics_engine.rotate_moving(delta_time)


    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> EVENT_HANDLE_STATE:
        """ Called whenever the mouse button is clicked. """
        pass

    def on_show_view(self) -> None:
        self.sound_player.play_music()
        if app_config.TIMER_ON and self.timer:
            self.timer.start()

    def on_hide_view(self) -> None:
        self.sound_player.stop_playing_music()
        self.timer.pause()
        self.main_controller.controls["select"] = False

    def on_draw(self):
        """Draw everything"""
        self.clear()

        with self.camera.activate():
            self.scene.draw()

        with self.gui_camera.activate():
            if self.minimap.minimap_on:
                self.minimap.draw()
                self.minimap.draw_outline()
            for widget in self.game_ui.widgets:
                widget.draw()

    def _return_to_menu(self):
        self.sound_player.music_playback.delete()
        self.__from.continue_enabled = True
        self.__from.save_game_state(self)
        self.window.show_view(self.__from)
        self.main_controller.controls["back"] = False
        self.main_controller.controls["start"] = False

    def clear_lists(self):
        self.coin_list = None
        self.player_list = None
        self.heart_list = None
        self.fruit_list = None
        self.lvl_wall_list = None
        self.wall_list = None
        self.item_list = None
