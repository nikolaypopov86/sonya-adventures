import logging

from misc.app_utils import singleton

logger = logging.getLogger(__name__)


class BaseController:
    def __init__(self):
        pass


@singleton
class GameController(BaseController):
    def __init__(self):
        super().__init__()

        self.controls = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "middle_up": False,
            "select": False,
            "start": False,
            "map": False
        }

    def set_control(self, name, value):
        self.controls[name] = value

    def get_control(self, name):
        return self.controls[name]
