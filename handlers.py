import logging
from doctest import debug

from misc.app_utils import singleton

from pyglet.input import Controller
from pyglet.math import Vec2

logger = logging.getLogger(__name__)


class BaseHandler:
    def __init__(self):
        pass


@singleton
class ControllerHandler(BaseHandler):
    def __init__(self):
        super().__init__()

        self.controls = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "select": False,
            "start": False,
            "a": False,
            "b": False,
            "x": False,
            "y": False
        }

    def on_dpad_motion(self, c: Controller, vector: Vec2):
        logger.debug(f"dpad_motion: {vector}")
        if vector.x < 0:
            self.controls["right"] = False
            self.controls["left"] = True
            logger.debug(f"left pressed")
        elif vector.x > 0:
            self.controls["left"] = False
            self.controls["right"] = True
            logger.debug(f"right pressed")
        else:
            self.controls["left"] = False
            self.controls["right"] = False
            logger.debug(f"horz release")

        if vector.y < 0:
            self.controls["up"] = False
            self.controls["down"] = True
            logger.debug(f"down pressed")
        elif vector.y > 0:
            self.controls["down"] = False
            self.controls["up"] = True
            logger.debug(f"up pressed")
        else:
            self.controls["up"] = False
            self.controls["down"] = False
            logger.debug(f"vert release")

    def on_button_press(self, c: Controller, button_name):
        logger.debug(f"button {button_name} pressed")
        button_name = map_button_name(button_name)
        if button_name in self.controls:
            logger.debug(f"control {button_name} update to true")
            self.controls[button_name] = True

    def on_button_release(self, c, button_name):
        logger.debug(f"button {button_name} release")
        button_name = map_button_name(button_name)
        self.controls[button_name] = False

    def release(self, button_name):
        button_name = map_button_name(button_name)
        self.controls[button_name] = False

def map_button_name(button_name):
    if button_name == "back": button_name = "select"
    return button_name

