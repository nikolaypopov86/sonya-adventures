from itertools import count
from typing import Any, Tuple

import arcade
from arcade import SpriteList, Sprite

from entities.gatherable import Gatherable
from misc.app_utils import Counter

MAIN_PATH = "data/tilesets/coins"
SPRITE_COUNT = 12
TICK_SCALING = 20
COIN_SCORE_COEFFICIENT = 50

c = Counter((SPRITE_COUNT-1) * TICK_SCALING)

class CoinList(Gatherable):
    def __init__(self, obj):
        super().__init__(obj, COIN_SCORE_COEFFICIENT)
        self.obj: SpriteList[Sprite]= obj
        self.coin_textures = []
        for i in range(12):
            texture = arcade.load_texture(f"{MAIN_PATH}/coin_{i}.png")
            self.coin_textures.append(texture)

    def check_or_update_pic(self):
        n = c.tick()
        for coin in self.obj:
            coin.texture = self.coin_textures[n//20]
