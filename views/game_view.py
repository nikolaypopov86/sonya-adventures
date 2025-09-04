import logging

from arcade import SpriteList, Scene, TileMap

from entities.coin import CoinList
from engine import PhysicsEngine
from entities.fruit import FruitList
from entities.sprites import PlayerSprite
from misc.config import AppConfig
from misc.sound_player import SoundPlayer
from entities.minimap import MiniMap

import arcade

from misc.timer import SimpleTimer
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
        self.camera: arcade.Camera2D | None = None
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
        self.max_life_points: int = 5
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

        self.setup_called = False

        self.level: int = app_config.BASE_LVL
        self.level_text: str | None = None

        self.map_width: int | None = None
        self.map_height: int | None = None

        self.minimap: MiniMap | None = None

        self.widgets = None

        self.timer: SimpleTimer | None = None
        self.timer_text: arcade.Text | None = None

        self.next_lvl: bool = True


    def setup(self):
        """Set up everything with the game"""

        self.setup_called = True

        # Create the sprite lists
        self.player_list = arcade.SpriteList()

        __coin_list = None
        __fruit_list = None
        if self.scene is not None and "Coins" in self.scene:
            __coin_list = CoinList(self.coin_list)
            __fruit_list = FruitList(self.fruit_list)

        layer_options = {
            "Platforms": {
                "use_spatial_hash": True
            }
        }

        # Load in TileMap
        tile_map: TileMap = arcade.load_tilemap(
            f":data:/maps/map_{self.level}.tmx",
            scaling=app_config.SPRITE_SCALING_TILES,
            layer_options=layer_options
        )

        logger.info(f"level: {self.level}")

        self.map_width = tile_map.width * tile_map.tile_width * tile_map.scaling
        self.map_height = tile_map.height * tile_map.tile_height * tile_map.scaling

        logger.info(f"map size: {self.map_width} X {self.map_height}")

        self.end_of_map = (tile_map.width * tile_map.tile_width) * tile_map.scaling

        # Pull the sprite layers out of the tile map
        self.scene: Scene = arcade.Scene.from_tilemap(tile_map)

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        if self.reset_coin:
            self.coin_list = CoinList(self.scene["Coins"])
            self.coin_total = len(self.coin_list.obj)
            self.fruit_list = FruitList(self.scene["Fruits"])
            self.fruit_total = len(self.fruit_list.obj)

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

        self.physics_engine.add_items(
            self.scene["Dynamic Items"],
        )

        self.physics_engine.add_moving_sprites(
            self.scene["Moving Sprites"],
        )

        path_to_font_file = ":data:/fonts/PixelOperator8.ttf"
        arcade.load_font(path_to_font_file)

        self.timer = SimpleTimer()
        if self.next_lvl:
            self.timer.set_seconds(tile_map.properties.get("seconds"))
            self.timer.start()
            self.next_lvl = False
            self.coin_count = 0

        self.score_text = arcade.Text(
            f"Score: {self.score}",
            x=app_config.WINDOW_WIDTH * 7 // 40,
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            color=(0, 0, 0),
            font_name=app_config.FONT_NAME,
            font_size=app_config.WINDOW_HEIGHT * 2 // 100
        )
        self.coin_symb = arcade.Text(
            "🟡",
            x=app_config.WINDOW_WIDTH // 48,
            y=app_config.WINDOW_HEIGHT * 93 // 100, # 37 // 40,
            color=(255, 215, 0),
            font_name="Segoe UI Emoji",
            font_size=app_config.WINDOW_HEIGHT // 30
        )
        self.fruit_symb = arcade.Text(
            "🍉",
            x=app_config.WINDOW_WIDTH // 66,
            y=app_config.WINDOW_HEIGHT * 85 // 100,  # 37 // 40,
            color=(255, 215, 0),
            font_name="Segoe UI Emoji",
            font_size=app_config.WINDOW_HEIGHT // 25
        )
        self.fruit_to_find = arcade.Text(
            f"{self.fruit_total - len(self.fruit_list.obj)}/{self.fruit_total}",
            x=app_config.WINDOW_WIDTH * 4 // 42,
            y=app_config.WINDOW_HEIGHT * 86 // 100,  # 37 // 40,
            color=(0, 0, 0),
            font_name=app_config.FONT_NAME,
            font_size=app_config.WINDOW_HEIGHT * 2 // 100,
            align="right"
        )
        self.coins_to_find = arcade.Text(
            f"{self.coin_total - len(self.coin_list.obj)}/{self.coin_total}",
            x=app_config.WINDOW_WIDTH * 4 // 42,
            y=app_config.WINDOW_HEIGHT * 93 // 100, #37 // 40,
            color=(0, 0, 0),
            font_name=app_config.FONT_NAME,
            font_size=app_config.WINDOW_HEIGHT * 2 // 100,
            align="right"
        )

        self.life_text = arcade.Text(
            f"{' ♥' * self.life_points} ",
            x=app_config.WINDOW_WIDTH - (app_config.WINDOW_WIDTH // 200),
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            color=(255, 0, 0),
            font_size=app_config.WINDOW_HEIGHT // 28,
            font_name="Segoe UI Emoji",
            align="right",
            anchor_x="right"
        )

        self.level_text = arcade.Text(
            f"Lvl: {self.level}",
            x=app_config.WINDOW_WIDTH * 20 // 40,
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            anchor_x="center",
            color=(0, 0, 0),
            font_name=app_config.FONT_NAME,
            font_size=app_config.WINDOW_HEIGHT * 2 // 100
        )

        self.timer_text = arcade.Text(
            f"{self.timer.left_text()}",
            x=app_config.WINDOW_WIDTH * 26 // 40,
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            anchor_x="center",
            color=(0, 0, 0),
            font_name=app_config.FONT_NAME,
            font_size=app_config.WINDOW_HEIGHT * 2 // 100
        )

        self.widgets = (
            self.score_text,
            self.life_text,
            self.coins_to_find,
            self.coin_symb,
            self.level_text,
            self.timer_text,
            self.fruit_symb,
            self.fruit_to_find
        )

        if self.reset_score:
            self.score = 0
        self.reset_score = True

        self.minimap = MiniMap()
        self.minimap.setup((self.map_width, self.map_height))

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.sound_player.music_playback.delete()
            self.__from.continue_enabled = True
            self.__from.save_game_state(self)
            self.window.show_view(self.__from)
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, app_config.PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
                self.sound_player.sound_jump()
        elif key == arcade.key.N:
            self.minimap.minimap_on = not self.minimap.minimap_on
        logger.debug(f"key {key} pressed, minimap_on: {self.minimap.minimap_on}")

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def on_update(self, delta_time):

        if not self.setup_called:
            self.setup()

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
        self.coins_to_find.text = f"{self.coin_count}/{self.coin_total}"

        self.level_text.text = f"Lvl: {self.level}"
        self.timer_text.text = f"{self.timer.left_text()}"
        self.coin_list.check_or_update_pic()

        delta_fruit_score, need_fruit_to_find, delta__count = self.fruit_list.remove_touched(self.player_sprite)
        self.score += delta_fruit_score
        fruit_count = self.fruit_total - len(self.fruit_list.obj)
        self.fruit_to_find.text = f"{fruit_count}/{self.fruit_total}"

        self.score_text.text = f"Score: {self.score}"

        if "Lvl Wall" in self.scene and fruit_count >= self.fruit_total:
            self.scene.remove_sprite_list_by_name("Lvl Wall")

        self.minimap.sprite_lists = tuple(self.scene[key] for key in app_config.MINIMAP_SPRITE_LISTS)
        self.minimap.update(self.player_sprite)

        self.physics_engine.move_player(self.left_pressed, self.right_pressed)
        camera_min_x = app_config.WINDOW_WIDTH // 2
        camera_max_x = self.map_width  - (app_config.WINDOW_WIDTH // 2)
        camera_min_y = app_config.WINDOW_HEIGHT // 2
        camera_max_y = self.map_height  - (app_config.WINDOW_HEIGHT // 2)

        camera_x: int = 0
        camera_y: int = 0

        player_x = self.player_sprite.position[0]
        player_y = self.player_sprite.position[1]

        if player_x < camera_min_x:
            camera_x = camera_min_x
        elif camera_min_x < player_x < camera_max_x:
            camera_x = player_x
        else:
            camera_x = camera_max_x

        if player_y < camera_min_y:
            camera_y = camera_min_y
        elif camera_min_y < player_y < camera_max_y:
            camera_y = player_y
        else:
            camera_y = camera_max_y

        self.camera.position = camera_x, camera_y
        self.physics_engine.step()
        self.physics_engine.rotate_moving(delta_time)


    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> EVENT_HANDLE_STATE:
        """ Called whenever the mouse button is clicked. """
        pass

    def on_show_view(self) -> None:
        self.sound_player.play_music()
        if self.timer:
            self.timer.start()

    def on_hide_view(self) -> None:
        self.timer.pause()

    def on_draw(self):
        """Draw everything"""
        self.clear()

        with self.camera.activate():
            self.scene.draw()

        with self.gui_camera.activate():
            if self.minimap.minimap_on:
                self.minimap.draw()
                self.minimap.draw_outline()
            for widget in self.widgets:
                widget.draw()
