import arcade

from entities.gatherable import Gatherable

HEART_SCORE_COEFFICIENT = 0


class HeartList(Gatherable):
    def __init__(self, obj):
        super().__init__(obj, HEART_SCORE_COEFFICIENT)
        self.obj: arcade.SpriteList = obj
