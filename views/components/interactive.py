from typing import Union, Tuple, Callable
import logging

from controllers.controller import GameController
from arcade.gui import UIFlatButton, UITextureToggle, UISlider

logger = logging.getLogger(__name__)


class InteractiveComponentTuple:
    def __init__(
            self,
            components_list: Tuple[Tuple[Union[UIFlatButton, UITextureToggle, UISlider], Callable], ...] | Tuple
    ):
        self.main_controller = GameController()
        self.components_list = components_list
        self.focused: int = 0

        logger.debug(f"given component tuple: {components_list}")

        self.components_list[0][0].focused = True
        self.focused = 0

    def update(self):
        if self.main_controller.controls["up"] and self.focused > 0:
            self.components_list[self.focused][0].focused = False
            self.focused -= 1
            self.components_list[self.focused][0].focused = True
            self.main_controller.controls["up"] = False
        elif self.main_controller.controls["down"] and self.focused < len(self.components_list) - 1:
            self.components_list[self.focused][0].focused = False
            self.focused += 1
            self.components_list[self.focused][0].focused = True
            self.main_controller.controls["down"] = False
        elif self.main_controller.controls["start"]:
            logger.debug("start pressed")
            self.main_controller.controls["start"] = False
            logger.debug(f"вызов функции {self.components_list[self.focused]}")
            self.components_list[self.focused][1]()
        elif self.main_controller.controls["left"] and isinstance(self.components_list[self.focused][0], UISlider):
            logger.debug("left pressed on dpad at slider")
            slider: UISlider = self.components_list[self.focused][0]
            if slider.value >= slider.step: slider.value -= slider.step
            self.main_controller.controls["left"] = False
            self.components_list[self.focused][1]()
        elif self.main_controller.controls["right"] and isinstance(self.components_list[self.focused][0], UISlider):
            logger.debug("right pressed on dpad at slider")
            slider: UISlider = self.components_list[self.focused][0]
            if slider.value <= (slider.max_value - slider.step):
                slider.value += slider.step
            self.main_controller.controls["right"] = False
            self.components_list[self.focused][1]()
