import logging

from controllers.controller import GameController
from misc.app_utils import singleton

import arcade

logger = logging.getLogger(__name__)


@singleton
class Keyboard:
    def __init__(self):
        self.main_controller = GameController()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE :
            self.main_controller.set_control("select", True)
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.main_controller.set_control("left", value=True)
            self.main_controller.set_control("right", value=False)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.main_controller.set_control("right", True)
            self.main_controller.set_control("left", value=False)
        elif key == arcade.key.UP or key == arcade.key.W:
            self.main_controller.set_control("up", True)
            self.main_controller.set_control("down", False)
            self.main_controller.set_control("middle_up", False)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.main_controller.set_control("down", True)
            self.main_controller.set_control("up", False)
            self.main_controller.set_control("middle_up", False)
        elif key == arcade.key.SPACE:
            self.main_controller.set_control("middle_up", True)
            self.main_controller.set_control("down", False)
            self.main_controller.set_control("up", False)
        elif key == arcade.key.N:
            self.main_controller.set_control("map", True)
        elif key == arcade.key.ENTER:
            self.main_controller.set_control("start", True)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.main_controller.set_control("left", False)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.main_controller.set_control("right", False)
        elif key == arcade.key.UP or key == arcade.key.W:
            self.main_controller.set_control("up", False)
        elif key == arcade.key.SPACE:
            self.main_controller.set_control("middle_up", False)
