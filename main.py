"""
Example of Pymunk Physics Engine Platformer
"""
import math
import os.path

import arcade
from pyglet.event import EVENT_HANDLE_STATE

SCREEN_TITLE = "PyMunk Platformer"
SPRITE_IMAGE_SIZE = 16

SPRITE_SCALING_PLAYER = 3
SPRITE_SCALING_TILES = 3

SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SCREEN_GRID_WIDTH = 30
SCREEN_GRID_HEIGHT = 20

SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

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

BULLET_MOVE_FORCE = 4500
BULLET_MASS = 0.1
BULLET_GRAVITY = 300


class PlayerSprite(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):
        """Init"""
        # Let parent initialize
        super().__init__(scale=SPRITE_SCALING_PLAYER)

        main_path = ":data:/knight/knight"

        # Load textures for jump, and fall states
        jump_texture = arcade.load_texture(f"{main_path}_walk0.png")
        fall_texture = arcade.load_texture(f"{main_path}_walk1.png")
        # Make pairs of textures facing left and right
        self.jump_texture_pair = jump_texture, jump_texture.flip_left_right()
        self.fall_texture_pair = fall_texture, fall_texture.flip_left_right()

        self.idle_textures = []
        for i in range(4):
            texture = arcade.load_texture(f"{main_path}_idle{i}.png")
            self.idle_textures.append((texture, texture.flip_left_right()))

        # Load textures for walking and make pairs of textures facing left and right
        self.walk_textures = []
        for i in range(16):
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
            if self.cur_idle_texture >= 200:
                self.cur_idle_texture = 0
            self.texture = self.idle_textures[self.cur_idle_texture // 50][self.character_face_direction]
            return

        # Have we moved far enough to change the texture?
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
            # Reset the odometer
            self.x_odometer = 0

            # Advance the walking animation
            self.cur_walk_texture += 1
            if self.cur_walk_texture > 15:
                self.cur_walk_texture = 0
            self.texture = self.walk_textures[self.cur_walk_texture][self.character_face_direction]


class BulletSprite(arcade.SpriteSolidColor):
    def pymunk_moved(self, physics_engine, dx: float, dy: float, d_angle: float) -> None:
        if self.center_y < -100:
            self.remove_from_sprite_lists()



class GameWindow(arcade.Window):
    """Main Window"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

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
        self.bullet_list: arcade.SpriteList | None = None
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


    def setup(self):
        """Set up everything with the game"""

        # Create the sprite lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # Map name
        map_name = ":data:pymunk.tmx"

        # Load in TileMap
        tile_map = arcade.load_tilemap(map_name, SPRITE_SCALING_TILES)

        # Pull the sprite layers out of the tile map
        self.wall_list = tile_map.sprite_lists["Platforms"]
        self.item_list = tile_map.sprite_lists["Dynamic Items"]
        self.water_list = tile_map.sprite_lists["Water"]
        self.background = tile_map.sprite_lists["Background"]
        self.foreground = tile_map.sprite_lists["Foreground"]
        self.moving_sprites_list = tile_map.sprite_lists["Moving Sprites"]

        # Create player sprite
        self.player_sprite = PlayerSprite()

        # Set player location
        grid_x = 1
        grid_y = 3.3
        self.player_sprite.center_x = SPRITE_SIZE * grid_x + SPRITE_SIZE / 2
        self.player_sprite.center_y = SPRITE_SIZE * grid_y + SPRITE_SIZE / 2
        # Add to player sprite list
        self.player_list.append(self.player_sprite)

        # Pymunk Physics Engine Setup
        damping = DEFAULT_DUMPING
        gravity = (0, -GRAVITY)

        self.physics_engine = arcade.PymunkPhysicsEngine(
            damping=damping,
            gravity=gravity
        )

        def wall_hit_handler(bullet_sprite: BulletSprite, _wall_sprite: arcade.Sprite, _arbiter, _space, _data):
            bullet_sprite.remove_from_sprite_lists()
        self.physics_engine.add_collision_handler("bullet", "wall", post_handler=wall_hit_handler)

        def item_hit_handler(bullet_sprite: BulletSprite, item_sprite: arcade.Sprite, _arbiter, _space, _data):
            bullet_sprite.remove_from_sprite_lists()
            item_sprite.remove_from_sprite_lists()
        self.physics_engine.add_collision_handler("bullet", "item", post_handler=item_hit_handler)



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
            self.wall_list,
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

        self.physics_engine.add_sprite_list(
            self.item_list,
            friction=DYNAMIC_ITEM_FRICTION,
            collision_type="item"
        )

        self.physics_engine.add_sprite_list(
            self.moving_sprites_list,
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.KINEMATIC
        )

        if not self.music_is_playing:
            arcade.play_sound(self.music, loop=True)
            self.music_is_playing = True


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.setup()
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
                arcade.play_sound(self.jump_sound)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def on_update(self, delta_time):
        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)

        if self.player_sprite.center_y < 16:
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

        self.physics_engine.step()

        for moving_sprite in self.moving_sprites_list:
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

        bullet = BulletSprite(width=20, height=5, color=arcade.color.DARK_YELLOW)

        self.bullet_list.append(bullet)

        # Position the bullet at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y

        bullet.position = self.player_sprite.position

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.

        dest_x = x
        dest_y = y

        # Do math to calculate how to get the bullet to the destination
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.

        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # What is the 1/2 size of this sprite, so we can figure out how far
        # away to spawn the bullet
        size = max(self.player_sprite.width, self.player_sprite.height) / 2

        # Use angle to spawn bullet away from player in proper direction
        bullet.center_x += size * math.cos(angle)
        bullet.center_y += size * math.sin(angle)

        # Set angle of bullet
        bullet.angle = math.degrees(angle)

        # Gravity to use for the bullet
        # If we don't use custom gravity, bullet drops too fast, or we have
        # to make it go too fast.

        # Force is in relation to bullet's angle.
        bullet_gravity = (0, -BULLET_GRAVITY)

        # Add the sprite. This needs to be done AFTER setting the fields above.
        self.physics_engine.add_sprite(
            bullet,
            mass=BULLET_MASS,
            damping=1.0,
            friction=0.6,
            collision_type="bullet",
            gravity=bullet_gravity,
            elasticity=0.9
        )

        # Add force to bullet
        force = (BULLET_MOVE_FORCE, 0)

        self.physics_engine.apply_force(bullet, force)

    def on_draw(self):
        """Draw everything"""
        self.clear()
        self.background.draw()
        self.wall_list.draw()
        self.moving_sprites_list.draw()
        self.bullet_list.draw()
        self.water_list.draw()
        self.item_list.draw()
        self.player_list.draw()
        self.foreground.draw()




def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()