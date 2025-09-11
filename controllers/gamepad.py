import logging

from misc.app_utils import singleton
from handlers import GameController

from pyglet.input import Controller, ControllerManager, DeviceOpenException
from pyglet.math import Vec2

logger = logging.getLogger(__name__)


@singleton
class Gamepad:
    def __init__(self):
        self.controller_manager: ControllerManager = ControllerManager()
        self.controller: Controller | None = None
        self.main_controller: GameController | None = GameController()


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

        def on_connect(c: Controller):
            self.controller = c
            self.controller.push_handlers(self.on_dpad_motion, self.on_button_press, self.on_button_release)
            try:
                self.controller.open()
            except DeviceOpenException as e:
                logger.error(f"{e}")
            logger.debug(f"detected: {c.name}, controller GUID: {c.guid}")

        def on_disconnect(c: Controller):
            logger.debug(f"no controllers detected")
            c.close()

        self.controller_manager.on_connect = on_connect
        self.controller_manager.on_disconnect = on_disconnect

        if self.controller is None:
            controllers = self.controller_manager.get_controllers()
            if controllers:
                on_connect(controllers[0])

    def on_dpad_motion(self, c: Controller, vector: Vec2):
        logger.debug(f"dpad_motion: {vector}")
        if vector.x < 0:
            self.main_controller.controls["right"] = False
            self.main_controller.controls["left"] = True
            logger.debug(f"left pressed on {c.name}")
        elif vector.x > 0:
            self.main_controller.controls["left"] = False
            self.main_controller.controls["right"] = True
            logger.debug(f"right pressed on {c.name}")
        else:
            self.main_controller.controls["left"] = False
            self.main_controller.controls["right"] = False
            logger.debug(f"horz release")

        if vector.y < 0:
            self.main_controller.controls["up"] = False
            self.main_controller.controls["down"] = True
            logger.debug(f"down pressed on {c.name}")
        elif vector.y > 0:
            self.main_controller.controls["down"] = False
            self.main_controller.controls["up"] = True
            logger.debug(f"up pressed on {c.name}")
        else:
            self.main_controller.controls["up"] = False
            self.main_controller.controls["down"] = False
            logger.debug(f"vert release")

    def on_button_press(self, c: Controller, button_name):
        logger.debug(f"button {button_name} pressed")
        control_name = map_button_name(button_name)
        if control_name in self.main_controller.controls:
            logger.debug(f"control {control_name} by {button_name} on {c.name} update to true")
            self.main_controller.set_control(control_name, True)

    def on_button_release(self, c, button_name):
        logger.debug(f"button {button_name} on {c.name} release")
        control_name = map_button_name(button_name)
        if control_name in self.main_controller.controls:
            logger.debug(f"control {control_name} by {button_name} on {c.name} update to false")
            self.main_controller.set_control(control_name, False)

    def release(self, button_name):
        button_name = map_button_name(button_name)
        self.controls[button_name] = False


def map_button_name(button_name):
    if button_name == "back": control_name = "back"
    elif button_name == "y": control_name = "map"
    elif button_name == "a": control_name = "up"
    else: control_name = button_name
    return control_name
