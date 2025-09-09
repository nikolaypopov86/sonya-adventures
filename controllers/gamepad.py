import logging

from misc.app_utils import singleton
from handlers import ControllerHandler

from pyglet.input import Controller, ControllerManager, DeviceOpenException

logger = logging.getLogger(__name__)


@singleton
class Gamepad:
    def __init__(self):
        self.controller_manager: ControllerManager = ControllerManager()
        self.controller: Controller | None = None
        self.handler: ControllerHandler | None = ControllerHandler()

        def on_connect(c: Controller):
            self.controller = c
            self.controller.push_handlers(self.handler)
            try:
                self.controller.open()
            except DeviceOpenException as e:
                logger.error(f"{e}")
            logger.debug(f"detected: {c.name}, controller GUID: {c.guid}")

        def on_disconnect(c: Controller):
            logger.debug(f"no controllers detected")
            self.controller.close()

        self.controller_manager.on_connect = on_connect
        self.controller_manager.on_disconnect = on_disconnect

        if self.controller is None:
            controllers = self.controller_manager.get_controllers()
            if controllers:
                on_connect(controllers[0])
