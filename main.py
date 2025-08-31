"""
Example of Pymunk Physics Engine Platformer
"""
import os.path

from sprites import PlayerSprite
from config import AppConfig

import arcade
from pyglet.event import EVENT_HANDLE_STATE

app_config = AppConfig()


class GameWindow(arcade.Window):
    """Main Window"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.coin_textures = None
        self.cur_coin_texture = None
        print(f"screen size: {app_config.SCREEN_WIDTH} X {app_config.SCREEN_HEIGHT}\nscaling: {app_config.SPRITE_SCALING_TILES}")

        self.water_list = None
        self.foreground = None
        self.background = None
        arcade.resources.add_resource_handle("data", f"{os.path.abspath('.')}/data")

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
        self.physics_engine: arcade.PymunkPhysicsEngine | None = None

        self.music = arcade.load_sound(":data:/sounds/time_for_adventure.mp3")
        self.music_is_playing = False
        self.jump_sound = arcade.load_sound(":data:/sounds/jump.wav")

        self.scene = None

        # Score
        self.score = 0

        # Score text
        self.score_text = None

        # Reset score
        self.reset_score = True

        # Reset map
        self.reset_coin = True

        # Max life points
        self.max_life_points = 5
        # Life points
        self.life_points = 5
        # Life text
        self.life_text = None


    def setup(self):
        """Set up everything with the game"""

        # Create the sprite lists
        self.player_list = arcade.SpriteList()

        __coin_list = None
        if self.scene is not None and "Coins" in self.scene:
            __coin_list = self.scene["Coins"]

        # Map name
        map_name = ":data:pymunk.tmx"

        # Load in TileMap
        tile_map = arcade.load_tilemap(map_name, app_config.SPRITE_SCALING_TILES)

        # Pull the sprite layers out of the tile map
        self.scene = arcade.Scene.from_tilemap(tile_map)

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
                sprite_list=__coin_list
            )
            self.reset_coin = True

        # Create player sprite
        self.player_sprite = PlayerSprite()

        # Set player location
        grid_x = 1
        grid_y = 3.3
        self.player_sprite.center_x = app_config.SPRITE_SIZE * grid_x + app_config.SPRITE_SIZE / 2
        self.player_sprite.center_y = app_config.SPRITE_SIZE * grid_y + app_config.SPRITE_SIZE / 2
        # Add to player sprite list
        self.player_list.append(self.player_sprite)
        self.scene.add_sprite_list_before("Player", "Foreground")
        self.scene.add_sprite("Player", self.player_sprite)


        # Pymunk Physics Engine Setup
        damping = app_config.DEFAULT_DUMPING
        gravity = (0, -app_config.GRAVITY)

        self.physics_engine = arcade.PymunkPhysicsEngine(
            damping=damping,
            gravity=gravity
        )



        self.physics_engine.add_sprite(
            self.player_sprite,
            friction=app_config.PLAYER_FRICTION,
            mass=app_config.PLAYER_MASS,
            moment_of_inertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
            collision_type="player",
            max_horizontal_velocity=app_config.PLAYER_MAX_HORIZONTAL_SPEED,
            max_vertical_velocity=app_config.PLAYER_MAX_VERTICAL_SPEED,
        )

        self.physics_engine.add_sprite_list(
            self.scene["Platforms"],
            friction=app_config.WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

        self.physics_engine.add_sprite_list(
            self.scene["Dynamic Items"],
            friction=app_config.DYNAMIC_ITEM_FRICTION,
            collision_type="item"
        )

        self.physics_engine.add_sprite_list(
            self.scene["Moving Sprites"],
            friction=app_config.WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.KINEMATIC
        )

        if app_config.VOLUME_MUSIC > 0 and not self.music_is_playing:
            arcade.play_sound(self.music, loop=True, volume=app_config.VOLUME_MUSIC)
            self.music_is_playing = True

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

        main_path = ":data:/coins"

        self.coin_textures = []
        for i in range(12):
            texture = arcade.load_texture(f"{main_path}/coin_{i}.png")
            self.coin_textures.append(texture)

        self.cur_coin_texture = 0


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.reset_coin = False
            self.setup()
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, app_config.PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
                arcade.play_sound(self.jump_sound, volume=app_config.VOLUME_SOUND)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def on_update(self, delta_time):
        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)

        if self.player_sprite.center_y < 16:
            self.life_points -= 1
            self.reset_coin = False
            self.reset_score = False
            self.setup()

        if self.left_pressed and not self.right_pressed:
            if is_on_ground:
                force = (-app_config.PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-app_config.PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            if is_on_ground:
                force = (app_config.PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (app_config.PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            self.physics_engine.set_friction(self.player_sprite, 1.0)

        coin_hit_list: list[arcade.Sprite] = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            # TODO: add sound
            self.score += 50
            self.score_text.text = f"Score: {self.score}"

        for coin in self.scene["Coins"]:
            self.cur_coin_texture += 1
            if self.cur_coin_texture > 11 * 200:
                self.cur_coin_texture = 0
            coin.texture = self.coin_textures[self.cur_coin_texture//200]

        self.physics_engine.step()

        for moving_sprite in self.scene["Moving Sprites"]:
            if moving_sprite.boundary_right and \
                    moving_sprite.change_x > 0 and \
                    moving_sprite.right > moving_sprite.boundary_right:
                moving_sprite.change_x *= -1
            elif moving_sprite.boundary_left and \
                    moving_sprite.change_x < 0 and \
                    moving_sprite.left < moving_sprite.boundary_left:
                moving_sprite.change_x *= -1
            if moving_sprite.boundary_top and \
                    moving_sprite.change_y > 0 and \
                    moving_sprite.top > moving_sprite.boundary_top:
                moving_sprite.change_y *= -1
            elif moving_sprite.boundary_bottom and \
                    moving_sprite.change_y < 0 and \
                    moving_sprite.bottom < moving_sprite.boundary_bottom:
                moving_sprite.change_y *= -1

            velocity = (moving_sprite.change_x * 1 / delta_time, moving_sprite.change_y * 1 / delta_time)
            self.physics_engine.set_velocity(moving_sprite, velocity)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> EVENT_HANDLE_STATE:
        """ Called whenever the mouse button is clicked. """
        pass

    def on_draw(self):
        """Draw everything"""
        self.clear()
        self.scene.draw()
        self.score_text.draw()
        self.life_text.draw()


def main():
    window = GameWindow(app_config.SCREEN_WIDTH, app_config.SCREEN_HEIGHT, app_config.SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()