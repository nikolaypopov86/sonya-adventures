"""
Example of Pymunk Physics Engine Platformer
"""
import os.path

from dotenv import load_dotenv
import arcade
from pyglet.event import EVENT_HANDLE_STATE

load_dotenv()

SCREEN_TITLE = "PyMunk Platformer"
SPRITE_IMAGE_SIZE = 16

SPRITE_SCALING_PLAYER = 3
SPRITE_SCALING_TILES = 3

SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SCREEN_GRID_WIDTH = 30
SCREEN_GRID_HEIGHT = 20

SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

# Player sprite
PLAYER_SPRITE = os.environ.get("PLAYER_SPRITE")

# Sprite numbers
WALK_SPRITE_COUNT = 0
IDLE_SPRITE_COUNT = 0
if PLAYER_SPRITE == "knight":
    WALK_SPRITE_COUNT = 16
    IDLE_SPRITE_COUNT = 4
elif PLAYER_SPRITE == "cat":
    WALK_SPRITE_COUNT = 32
    IDLE_SPRITE_COUNT = 16

# Change idle pic counter coefficient
IDLE_PIC_COUNTER_COEF = 50


# --- Physics forces. Higher number, faster accelerating

# Gravity
GRAVITY = 1500

# Damping - Amount of speed lost per second
DEFAULT_DUMPING = 1.0
PLAYER_DUMPING = 0.4

# Friction between objects
PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.7
DYNAMIC_ITEM_FRICTION = 0.6

# Mass (defaults to 1)
PLAYER_MASS = 1.0

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 250
PLAYER_MAX_VERTICAL_SPEED = 450

# Force applied while on ground
PLAYER_MOVE_FORCE_ON_GROUND = 8000

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 900

# strength of a jump
PLAYER_JUMP_IMPULSE = 1800

# Player animations
DEAD_ZONE = 0.1

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 20

# Music and sound
VOLUME_MUSIC = float(os.environ.get("VOLUME_MUSIC"))
VOLUME_SOUND = float(os.environ.get("VOLUME_SOUND"))


class PlayerSprite(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):
        """Init"""
        # Let parent initialize
        super().__init__(scale=SPRITE_SCALING_PLAYER)

        main_path = f":data:/{PLAYER_SPRITE}/{PLAYER_SPRITE}"

        # Load textures for jump, and fall states
        jump_texture = arcade.load_texture(f"{main_path}_walk0.png")
        fall_texture = arcade.load_texture(f"{main_path}_walk1.png")
        # Make pairs of textures facing left and right
        self.jump_texture_pair = jump_texture, jump_texture.flip_left_right()
        self.fall_texture_pair = fall_texture, fall_texture.flip_left_right()

        self.idle_textures = []

        for i in range(IDLE_SPRITE_COUNT):
            texture = arcade.load_texture(f"{main_path}_idle{i}.png")
            self.idle_textures.append((texture, texture.flip_left_right()))

        # Load textures for walking and make pairs of textures facing left and right
        self.walk_textures = []
        for i in range(WALK_SPRITE_COUNT):
            texture = arcade.load_texture(f"{main_path}_walk{i}.png")
            self.walk_textures.append((texture, texture.flip_left_right()))

        # Set the initial texture
        self.texture = self.idle_textures[0][0]

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Index of our current walk texture
        self.cur_walk_texture = 0

        # Index of our current idle texture
        self.cur_idle_texture = 0

        # How far have we traveled horizontally since changing the texture
        self.x_odometer = 0


    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """Handle being moved by the pymunk engine"""
        # Figure out if we need to face left or right
        if dx < -DEAD_ZONE and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif dx > DEAD_ZONE and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Are we on the ground?
        is_on_ground = physics_engine.is_on_ground(self)

        # Add to the odometer how far we've moved
        self.x_odometer += dx

        # Jumping animation
        if not is_on_ground:
            if dy > DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -DEAD_ZONE:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                return

        # Idle animation
        if abs(dx) <= DEAD_ZONE:
            self.cur_idle_texture += 1
            if self.cur_idle_texture >= IDLE_SPRITE_COUNT * IDLE_PIC_COUNTER_COEF:
                self.cur_idle_texture = 0
            self.texture = self.idle_textures[self.cur_idle_texture // IDLE_PIC_COUNTER_COEF][self.character_face_direction]
            return

        # Have we moved far enough to change the texture?
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
            # Reset the odometer
            self.x_odometer = 0

            # Advance the walking animation
            self.cur_walk_texture += 1
            if self.cur_walk_texture > WALK_SPRITE_COUNT-1:
                self.cur_walk_texture = 0
            self.texture = self.walk_textures[self.cur_walk_texture][self.character_face_direction]



class GameWindow(arcade.Window):
    """Main Window"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.coin_textures = None
        self.cur_coin_texture = None
        print(f"screen size: {SCREEN_WIDTH} X {SCREEN_HEIGHT}\nscaling: {SPRITE_SCALING_TILES}")

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
        tile_map = arcade.load_tilemap(map_name, SPRITE_SCALING_TILES)

        # Pull the sprite layers out of the tile map
        self.scene = arcade.Scene.from_tilemap(tile_map)

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
        self.player_sprite.center_x = SPRITE_SIZE * grid_x + SPRITE_SIZE / 2
        self.player_sprite.center_y = SPRITE_SIZE * grid_y + SPRITE_SIZE / 2
        # Add to player sprite list
        self.player_list.append(self.player_sprite)
        self.scene.add_sprite_list_before("Player", "Foreground")
        self.scene.add_sprite("Player", self.player_sprite)


        # Pymunk Physics Engine Setup
        damping = DEFAULT_DUMPING
        gravity = (0, -GRAVITY)

        self.physics_engine = arcade.PymunkPhysicsEngine(
            damping=damping,
            gravity=gravity
        )



        self.physics_engine.add_sprite(
            self.player_sprite,
            friction=PLAYER_FRICTION,
            mass=PLAYER_MASS,
            moment_of_inertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
            collision_type="player",
            max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
            max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED,
        )

        self.physics_engine.add_sprite_list(
            self.scene["Platforms"],
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

        self.physics_engine.add_sprite_list(
            self.scene["Dynamic Items"],
            friction=DYNAMIC_ITEM_FRICTION,
            collision_type="item"
        )

        self.physics_engine.add_sprite_list(
            self.scene["Moving Sprites"],
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.KINEMATIC
        )

        if VOLUME_MUSIC > 0 and not self.music_is_playing:
            arcade.play_sound(self.music, loop=True, volume=VOLUME_MUSIC)
            self.music_is_playing = True

        path_to_font_file = ":data:/fonts/PixelOperator8.ttf"
        arcade.load_font(path_to_font_file)
        self.score_text = arcade.Text(f"Score: {self.score}", x=20, y=880, color=(0, 0, 0), font_name="Pixel Operator 8", font_size=30)
        self.life_text = arcade.Text(f"{' ♥' * self.life_points} ", x=1440, y=880, color=(255, 0, 0), font_size=70, font_name="Arial", align="right", anchor_x="right")

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
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
                arcade.play_sound(self.jump_sound, volume=VOLUME_SOUND)

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
                force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            if is_on_ground:
                force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (PLAYER_MOVE_FORCE_IN_AIR, 0)
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
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()