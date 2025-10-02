from typing import Tuple

from misc.config import AppConfig
from controllers.controller import GameController
from misc.sound_player import SoundPlayer

import arcade
from arcade import PymunkPhysicsEngine, Sprite

app_config = AppConfig()


class PhysicsEngine(PymunkPhysicsEngine):
    """
    Game engine
    """
    def __init__(
            self,
            damping: float,
            gravity: Tuple[int, float]
    ):
        super().__init__(
            damping=damping,
            gravity=gravity,
        )

        self.main_controller = GameController()

        self.sound_player = SoundPlayer()

        self.player_sprite: arcade.Sprite | None = None
        self.platform_list = None
        self.item_list = None
        self.moving_sprites_list = None
        self.edge_list = None
        self.lvl_walls = None
        self.bee_list = None

    def add_player(
            self,
            sprite: Sprite
    ) -> None:
        self.player_sprite = sprite
        super().add_sprite(
            sprite,
            friction=app_config.PLAYER_FRICTION,
            mass=app_config.PLAYER_MASS,
            moment_of_inertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
            collision_type="player",
            max_horizontal_velocity=app_config.PLAYER_MAX_HORIZONTAL_SPEED,
            max_vertical_velocity=app_config.PLAYER_MAX_VERTICAL_SPEED,
        )

    def add_edges(
            self,
            sprite_list
    ) -> None:
        super().add_sprite_list(
            sprite_list,
            friction=app_config.WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

        self.edge_list = sprite_list

    def add_platforms(
            self,
            sprite_list,
            friction: float | None = None
    ) -> None:
        if friction is None:
            friction = app_config.WALL_FRICTION
        super().add_sprite_list(
            sprite_list,
            friction=friction,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

        self.platform_list = sprite_list

    def add_lvl_walls(
            self,
            sprite_list
    ):
        super().add_sprite_list(
            sprite_list,
            friction=app_config.WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

        self.lvl_walls = sprite_list

    def add_items(
            self,
            sprite_list
    ) -> None:
        super().add_sprite_list(
            sprite_list,
            friction=app_config.DYNAMIC_ITEM_FRICTION,
            collision_type="item"
        )

        self.item_list = sprite_list

    def add_moving_sprites(
            self,
            sprite_list
    ) -> None:
        super().add_sprite_list(
            sprite_list,
            friction=app_config.WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.KINEMATIC
        )

        self.moving_sprites_list = sprite_list

    def move_player(
            self
    ) -> None:
        is_on_ground = self.is_on_ground(self.player_sprite)

        if self.main_controller.controls["left"] and not self.main_controller.controls["right"]:
            if is_on_ground:
                force = (-app_config.PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-app_config.PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.apply_force(self.player_sprite, force)
            self.set_friction(self.player_sprite, 0)
        elif self.main_controller.controls["right"] and not self.main_controller.controls["left"]:
            if is_on_ground:
                force = (app_config.PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (app_config.PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.apply_force(self.player_sprite, force)
            self.set_friction(self.player_sprite, 0)
        else:
            self.set_friction(self.player_sprite, 1.0)

        if self.main_controller.controls["up"]:
            if self.is_on_ground(self.player_sprite):
                impulse = (0, app_config.PLAYER_JUMP_IMPULSE)
                self.apply_impulse(self.player_sprite, impulse)
                self.sound_player.sound_jump()
        elif self.main_controller.controls["middle_up"]:
            if self.is_on_ground(self.player_sprite):
                impulse = (0, app_config.PLAYER_JUMP_IMPULSE//7)
                self.apply_impulse(self.player_sprite, impulse)
                self.sound_player.sound_jump()


    def rotate_moving(self, delta_time):
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
            self.set_velocity(moving_sprite, velocity)
