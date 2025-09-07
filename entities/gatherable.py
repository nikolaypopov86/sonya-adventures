import logging
from typing import Tuple

import arcade

logger = logging.getLogger(__name__)


class Gatherable:
    def __init__(self, obj, score_coef):
        self.obj: arcade.SpriteList[arcade.Sprite] = obj
        self.score_coef: int = score_coef

    def remove_touched(
            self,
            player_sprite: arcade.Sprite
    ) -> tuple[int, int, int]:
        hit_list: list[arcade.Sprite] = arcade.check_for_collision_with_list(
            player_sprite, self.obj
        )

        delta_count = 0
        for item in hit_list:
            item.remove_from_sprite_lists()
            logger.debug(f"item {item.properties.get('name')}:{item.properties} removed")
            delta_count += 1

        return delta_count * self.score_coef, len(self.obj), delta_count

    def draw(
            self,
            *,
            filter: int | Tuple[int, int] | None = None,
            pixelated: bool | None = None,
            blend_function: tuple[int, int] | tuple[int, int, int, int] | None = None
    ):
        self.obj.draw(filter=filter, pixelated=pixelated, blend_function=blend_function)
