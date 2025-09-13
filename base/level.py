import logging
import pprint
from typing import Tuple

from entities.gatherable import Gatherable
from base.engine import PhysicsEngine
from entities.sprites import PlayerSprite
from misc.sound_player import SoundPlayer
from entities.fruit import FruitList
from entities.coin import CoinList
from entities.heart import HeartList
from misc.timer import SimpleTimer
from entities.minimap import MiniMap
from misc.config import AppConfig
from views.game_over_view import GameOverView

import arcade
from arcade import SpriteList, TileMap, Scene

app_config = AppConfig()
logger = logging.getLogger(__name__)

LAYER_OPTIONS = {
    "Platforms": {
        "use_spatial_hash": True
    },
    "Water": {
        "use_spatial_hash": True
    }
}


class Level:
    def __init__(self, window: arcade.Window, main_menu, game_view):

        self.window = window
        self.main_menu_view = main_menu
        self.game_view = game_view

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

        # Score
        self.score: int = 0

        # Score text
        self.score_text: arcade.Text | None = None

        # Reset score
        self.reset_score: bool = True

        # Reset map
        self.reset_coin: bool = True

        self.ui_text_color: Tuple[int, int, int, int] | None = None

        # Max life points
        self.max_life_points: int = 7
        # Life points
        self.life_points: int = app_config.BASE_LIFE_POINTS
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

        self.lvl: int = app_config.BASE_LVL
        self.level_text: str | None = None

        self.map_width: int | None = None
        self.map_height: int | None = None

        self.minimap: MiniMap | None = None

        self.game_ui = None

        self.timer: SimpleTimer | None = None
        self.timer_text: arcade.Text

    def setup(self):
        logger.debug(f"enter Level method setup")

        self.player_list = arcade.SpriteList()

        map_path = f":data:/maps/map_{self.lvl}.tmx"

        logger.info(f"map_path: {map_path}")

        tile_map: TileMap = arcade.load_tilemap(
            map_path,
            scaling=app_config.SPRITE_SCALING_TILES,
            layer_options=LAYER_OPTIONS
        )

        self.ui_text_color = tile_map.properties["text_color"]

        logger.info(f"level: {self.lvl}")

        logger.info(f"map size: {self.map_width} X {self.map_height}")

        self.end_of_map = (tile_map.width * tile_map.tile_width) * tile_map.scaling

        # Pull the sprite layers out of the tile map
        self.scene: Scene = arcade.Scene.from_tilemap(tile_map)

        logger.debug(f"scene: {self.scene.__dict__}")


        self.map_width = tile_map.width * tile_map.tile_width * tile_map.scaling
        self.map_height = tile_map.height * tile_map.tile_height * tile_map.scaling

        for moving_sprite in self.scene["Moving Sprites"]:
            moving_sprite.boundary_left *= app_config.SPRITE_SCALING_TILES
            moving_sprite.boundary_right *= app_config.SPRITE_SCALING_TILES
            moving_sprite.boundary_top *= app_config.SPRITE_SCALING_TILES
            moving_sprite.boundary_bottom *= app_config.SPRITE_SCALING_TILES

        self.player_sprite = PlayerSprite()
        self.player_sprite.move_to_default_location()

        # Add to player sprite list
        self.player_list.append(self.player_sprite)
        self.scene.add_sprite_list_before("Player", "Foreground")
        self.scene.add_sprite("Player", self.player_sprite)

        self.lvl_wall_list = self.scene["Lvl Wall"]
        self.setup_engine()

        self.timer = SimpleTimer()
        self.timer.start()
        self.timer.set_seconds(tile_map.properties["seconds"])

        self.coin_list = CoinList(self.scene["Coins"])
        self.coin_total = len(self.coin_list.obj)
        self.coin_count = 0
        self.fruit_list = FruitList(self.scene["Fruits"])
        self.fruit_total = len(self.fruit_list.obj)
        self.fruit_count = 0
        self.heart_list = HeartList(self.scene["Hearts"])

        self.reset_score = True

        if not self.sound_player.is_playing:
            self.sound_player.play_music()

    def player_spawn(self):
        pass

    def setup_engine(self):
        # Pymunk Physics Engine Setup
        damping = app_config.DEFAULT_DUMPING
        gravity = (0, -app_config.GRAVITY)

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

    def _game_over(self):
        view = GameOverView(self.main_menu_view)
        view.set_result(self.score)
        self.sound_player.stop_playing_music()
        self.window.show_view(view)

    def update(self, delta_time):
        if app_config.TIMER_ON and not self.timer.timer_on:
            self.timer.start()

        if self.player_sprite.center_y < 16:
            logger.info(f"кошечка упала =(")
            if self.life_points <= 0:
                self._game_over()
            self.life_points -= 1
            self.physics_engine.remove_sprite(self.player_sprite)
            self.player_sprite.move_to_default_location()
            self.physics_engine.add_player(self.player_sprite)

        if self.timer.is_up():
            self._game_over()

        if self.player_sprite.center_x >= self.end_of_map:
            self.lvl += 1
            self.game_view.setup()

        delta_coin_score, need_coin_to_find, delta_coin_count = self.coin_list.remove_touched(self.player_sprite)
        self.score += delta_coin_score
        self.coin_count += delta_coin_count

        delta_fruit_score, need_fruit_to_find, delta_fruit_count = self.fruit_list.remove_touched(self.player_sprite)
        self.score += delta_fruit_score
        self.fruit_count += delta_fruit_count

        _, _, delta_life_points = self.heart_list.remove_touched(self.player_sprite)
        if self.life_points < self.max_life_points:
            self.life_points += delta_life_points

        self.coin_list.check_or_update_pic()

        if "Lvl Wall" in self.scene and self.fruit_count >= self.fruit_total:
            logger.debug(f"{pprint.pprint(self.scene.__dict__)}")
            logger.info("Lvl Wall removed !")
            self.physics_engine.remove_sprite(self.lvl_wall_list.sprite_list.pop())
            self.scene.remove_sprite_list_by_object(self.lvl_wall_list)
            logger.debug(f"{pprint.pprint(self.scene.__dict__)}")
            self.scene.update(delta_time)
