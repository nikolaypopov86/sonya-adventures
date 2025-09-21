from typing import Tuple

import arcade

from misc.config import AppConfig
import misc.app_utils as utils
from controllers.controller import GameController

# Constants
# Facing
LEFT_FACING = 1
RIGHT_FACING = 0

app_config = AppConfig()


class PlayerSprite(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):
        """Init"""
        # Let parent initialize
        super().__init__(scale=app_config.SPRITE_SCALING_PLAYER)

        main_path = f"data/tilesets/{app_config.PLAYER_SPRITE}/{app_config.PLAYER_SPRITE}"

        # Load textures for jump, and fall states
        jump_texture = arcade.load_texture(f"{main_path}_walk0.png")
        fall_texture = arcade.load_texture(f"{main_path}_walk1.png")
        # Make pairs of textures facing left and right
        self.jump_texture_pair = jump_texture, jump_texture.flip_left_right()
        self.fall_texture_pair = fall_texture, fall_texture.flip_left_right()

        self.idle_textures = []

        for i in range(app_config.IDLE_SPRITE_COUNT):
            texture = arcade.load_texture(f"{main_path}_idle{i}.png")
            self.idle_textures.append((texture, texture.flip_left_right()))

        # Load textures for walking and make pairs of textures facing left and right
        self.walk_textures = []
        for i in range(app_config.WALK_SPRITE_COUNT):
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

        self.controller = GameController()



    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """Handle being moved by the pymunk engine"""
        # Figure out if we need to face left or right
        if dx < -app_config.DEAD_ZONE and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif dx > app_config.DEAD_ZONE and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Are we on the ground?
        is_on_ground = physics_engine.is_on_ground(self)

        # Add to the odometer how far we've moved
        self.x_odometer += dx

        # Jumping animation
        if not is_on_ground:
            if dy > app_config.DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -app_config.DEAD_ZONE:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                return

        # Idle animation
        if abs(dx) <= app_config.DEAD_ZONE:
            self.cur_idle_texture += 1
            if self.cur_idle_texture >= app_config.IDLE_SPRITE_COUNT * app_config.IDLE_PIC_COUNTER_COEF:
                self.cur_idle_texture = 0
            self.texture = self.idle_textures[self.cur_idle_texture // app_config.IDLE_PIC_COUNTER_COEF][self.character_face_direction]
            return

        # Have we moved far enough to change the texture?
        if (self.controller.get_control("left") or self.controller.get_control("right")) and abs(self.x_odometer) > app_config.DISTANCE_TO_CHANGE_TEXTURE:
            # Reset the odometer
            self.x_odometer = 0

            # Advance the walking animation
            self.cur_walk_texture += 1
            if self.cur_walk_texture > app_config.WALK_SPRITE_COUNT-1:
                self.cur_walk_texture = 0
            self.texture = self.walk_textures[self.cur_walk_texture][self.character_face_direction]

    def move_to_default_location(self, default_position: str | None) -> None:
        if default_position is None:
            default_position = app_config.PLAYER_SPRITE_DEFAULT_POSITION
        else:
            default_position = utils.str_to_tuple(default_position, int)
        grid_x, grid_y = default_position

        self.center_x = app_config.SPRITE_SIZE * grid_x + app_config.SPRITE_SIZE / 2
        self.center_y = app_config.SPRITE_SIZE * grid_y + app_config.SPRITE_SIZE / 2
        self.update()
