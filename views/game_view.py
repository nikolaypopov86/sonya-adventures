from arcade import SpriteList, Scene, TileMap

from entities.coin import CoinList
from engine import PhysicsEngine
from entities.sprites import PlayerSprite
from config import AppConfig
from sound_player import SoundPlayer

import arcade

app_config = AppConfig()

from pyglet.event import EVENT_HANDLE_STATE



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
        print(f"screen size: {app_config.SCREEN_WIDTH} X {app_config.SCREEN_HEIGHT}\nscaling: {app_config.SPRITE_SCALING_TILES}")

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

        self.setup_called = False


    def setup(self):
        """Set up everything with the game"""

        self.setup_called = True

        # Create the sprite lists
        self.player_list = arcade.SpriteList()

        __coin_list = None
        if self.scene is not None and "Coins" in self.scene:
            __coin_list = CoinList(self.coin_list)

        # Map name
        map_name = ":data:pymunk.tmx"

        # Load in TileMap
        tile_map: TileMap = arcade.load_tilemap(map_name, app_config.SPRITE_SCALING_TILES)

        # Pull the sprite layers out of the tile map
        self.scene: Scene = arcade.Scene.from_tilemap(tile_map)

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        if self.reset_coin:
            self.coin_list = CoinList(self.scene["Coins"])

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
        self.score_text = arcade.Text(
            f"Score: {self.score}",
            x=7 * app_config.SPRITE_SCALING_TILES,
            y=293 * app_config.SPRITE_SCALING_TILES,
            color=(0, 0, 0),
            font_name="Pixel Operator 8",
            font_size=10 * app_config.SPRITE_SCALING_TILES
        )
        self.life_text = arcade.Text(
            f"{' ♥' * self.life_points} ",
            x=480 * app_config.SPRITE_SCALING_TILES,
            y=293 * app_config.SPRITE_SCALING_TILES,
            color=(255, 0, 0),
            font_size=24 * app_config.SPRITE_SCALING_TILES,
            font_name="Arial",
            align="right",
            anchor_x="right"
        )

        if self.reset_score:
            self.score = 0
        self.reset_score = True


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

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def on_update(self, delta_time):

        if not self.setup_called:
            self.setup()

        if self.player_sprite.center_y < 16:
            self.life_points -= 1
            self.reset_coin = False
            self.reset_score = False
            self.setup()

        delta_score = self.coin_list.remove_touched(self.player_sprite)
        self.score += delta_score
        self.score_text.text = f"Score: {self.score}"
        self.coin_list.check_or_update_pic()

        self.physics_engine.move_player(self.left_pressed, self.right_pressed)
        camera_min_x = app_config.WINDOW_WIDTH // 2
        camera_max_x = app_config.SCREEN_WIDTH  - (app_config.WINDOW_WIDTH // 2)
        camera_min_y = app_config.WINDOW_HEIGHT // 2
        camera_max_y = app_config.SCREEN_HEIGHT  - (app_config.WINDOW_HEIGHT // 2)

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

    def on_hide_view(self) -> None:
        pass

    def on_draw(self):
        """Draw everything"""
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()
        self.score_text.draw()
        self.life_text.draw()
