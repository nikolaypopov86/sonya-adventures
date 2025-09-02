from itertools import count
from typing import Any, Tuple

import arcade
from arcade import SpriteList, Sprite

from misc.app_utils import Counter

MAIN_PATH = ":data:/coins"
SPRITE_COUNT = 12
TICK_SCALING = 20

c = Counter((SPRITE_COUNT-1) * TICK_SCALING)

class CoinList:
    def __init__(self, obj, **kwargs: Any):
        self.obj: SpriteList[Sprite]= obj
        self.coin_textures = []
        for i in range(12):
            texture = arcade.load_texture(f"{MAIN_PATH}/coin_{i}.png")
            self.coin_textures.append(texture)

    def check_or_update_pic(self):
        n = c.tick()
        for coin in self.obj:
            coin.texture = self.coin_textures[n//20]

    def remove_touched(
            self,
            player_sprite: Sprite
    ) -> tuple[int, int, int]:

        coin_hit_list: list[arcade.Sprite] = arcade.check_for_collision_with_list(
            player_sprite, self.obj
        )

        delta_coin_count = 0
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            delta_coin_count += 1

        return delta_coin_count * 50, len(self.obj), delta_coin_count

    def draw(
            self,
            *,
            filter: int | Tuple[int, int] | None = None,
            pixelated: bool | None = None,
            blend_function: tuple[int, int] | tuple[int, int, int, int] | None = None
    ):
        self.obj.draw(filter=filter, pixelated=pixelated, blend_function=blend_function)