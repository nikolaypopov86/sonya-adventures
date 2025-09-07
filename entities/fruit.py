from typing import Tuple

import arcade

from entities.gatherable import Gatherable

FRUIT_SCORE_COEFFICIENT = 100


class FruitList(Gatherable):
    def __init__(self, obj):
        super().__init__(obj, FRUIT_SCORE_COEFFICIENT)
        self.obj: arcade.SpriteList = obj
