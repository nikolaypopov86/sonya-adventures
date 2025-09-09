from typing import Tuple

import arcade
from arcade import PymunkPhysicsEngine, Sprite

from misc.config import AppConfig

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

        self.player_sprite: arcade.Sprite | None = None
        self.platform_list = None
        self.item_list = None
        self.moving_sprites_list = None
        self.edge_list = None
        self.lvl_walls = None

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
            sprite_list
    ) -> None:
        super().add_sprite_list(
            sprite_list,
            friction=app_config.WALL_FRICTION,
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
            self,
            left_pressed: bool,
            right_pressed: bool,
            # up_pressed: bool
    ) -> None:
        is_on_ground = self.is_on_ground(self.player_sprite)

        if left_pressed and not right_pressed:
            if is_on_ground:
                force = (-app_config.PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-app_config.PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.apply_force(self.player_sprite, force)
            self.set_friction(self.player_sprite, 0)
        elif right_pressed and not left_pressed:
            if is_on_ground:
                force = (app_config.PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (app_config.PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.apply_force(self.player_sprite, force)
            self.set_friction(self.player_sprite, 0)
        else:
            self.set_friction(self.player_sprite, 1.0)

        if self.player_sprite.left < 0:
            self.player_sprite.left = 0

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