import logging
import os

from dotenv import load_dotenv

from config import AppConfig
from main_view import MainView

import arcade

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL"),
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s"
)

logger = logging.getLogger(__name__)
logger.info(f"Запуск приложения")

app_config = AppConfig()
logger.debug(f"app config: {app_config.__dict__}")

arcade.resources.add_resource_handle("data", f"{os.path.abspath('.')}/data")


if __name__ == '__main__':
    logger.debug(f"Запуск приложения")
    window = arcade.Window(app_config.WINDOW_WIDTH, app_config.WINDOW_HEIGHT, app_config.SCREEN_TITLE)
    view = MainView()
    window.show_view(view)
    arcade.run()