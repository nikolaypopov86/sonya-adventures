from misc.config import AppConfig
import arcade

app_config = AppConfig()


class GameUIText(arcade.Text):
    def __init__(self, text: str, x: float, y: float, **kwargs):
        super().__init__(text, x, y, **kwargs)

        if "font_name" in kwargs:
            self.font_name = kwargs["font_name"]
        else:
            self.font_name: str = app_config.FONT_NAME

        if "font_size" in kwargs:
            self.font_size: int = kwargs["font_size"]
        else:
            self.font_size: int = app_config.WINDOW_HEIGHT * 2 // 100

