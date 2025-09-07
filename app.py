import logging
import os

import pyglet
from dotenv import load_dotenv

from misc.config import AppConfig
from views.main_view import MainView

import arcade

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL"),
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s"
)

logger = logging.getLogger(__name__)
logger.info(f"Запуск приложения")

arcade.resources.add_resource_handle("data", f"{os.getcwd()}/data")

app_config = AppConfig()
logger.debug(f"app config: {app_config.__dict__}")

app_config.load_fonts()

logger.debug(f"Запуск приложения")
logger.info(f"{pyglet.gl.gl_info._gl_info.__dict__}")
window = arcade.Window(app_config.WINDOW_WIDTH, app_config.WINDOW_HEIGHT, app_config.SCREEN_TITLE)
logger.info(f"windows size: {app_config.WINDOW_WIDTH} X {app_config.WINDOW_HEIGHT}")
logger.info(f"sprite image size: {app_config.SPRITE_IMAGE_SIZE}")
logger.info(f"scaling: {app_config.SPRITE_SCALING_TILES}")
view = MainView()
window.show_view(view)
arcade.run()