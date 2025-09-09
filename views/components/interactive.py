from typing import Union, Tuple, Callable
import logging

from controllers.gamepad import Gamepad

from handlers import ControllerHandler
from arcade.gui import UIFlatButton, UITextureToggle, UISlider

logger = logging.getLogger(__name__)


class InteractiveComponentTuple:
    def __init__(
            self,
            components_list: Tuple[Tuple[Union[UIFlatButton, UITextureToggle, UISlider], Callable], ...] | Tuple
    ):
        self.gamepad: Gamepad = Gamepad()
        self.components_list = components_list
        self.focused: int = 0

        logger.debug(f"given component tuple: {components_list}")

        if self.gamepad.controller is not None:
            self.components_list[0][0].focused = True
            self.focused = 0
            self.controller_handler = ControllerHandler()
            self.gamepad.controller.push_handlers(self.controller_handler)

    def update(self):
        if self.gamepad.controller is not None:
            if self.controller_handler.controls["up"] and self.focused > 0:
                self.components_list[self.focused][0].focused = False
                self.focused -= 1
                self.components_list[self.focused][0].focused = True
                self.controller_handler.controls["up"] = False
            elif self.controller_handler.controls["down"] and self.focused < len(self.components_list) - 1:
                self.components_list[self.focused][0].focused = False
                self.focused += 1
                self.components_list[self.focused][0].focused = True
                self.controller_handler.controls["down"] = False
            elif self.controller_handler.controls["start"] or self.controller_handler.controls["select"]:
                self.controller_handler.controls["start"] = False
                self.controller_handler.controls["select"] = False
                self.components_list[self.focused][1]()
            elif self.controller_handler.controls["left"] and isinstance(self.components_list[self.focused][0], UISlider):
                logger.debug("left pressed on dpad at slider")
                slider: UISlider = self.components_list[self.focused][0]
                if slider.value >= slider.step: slider.value -= slider.step
                self.controller_handler.controls["left"] = False
                self.components_list[self.focused][1]()
            elif self.controller_handler.controls["right"] and isinstance(self.components_list[self.focused][0], UISlider):
                logger.debug("right pressed on dpad at slider")
                slider: UISlider = self.components_list[self.focused][0]
                if slider.value <= (slider.max_value - slider.step):
                    slider.value += slider.step
                self.controller_handler.controls["right"] = False
        
        