import abc

from misc.config import AppConfig

import arcade.csscolor
import arcade.gui

app_config = AppConfig()


class Labeled:
    def __init__(self):
        self.text_label = ""
        self.text_color = arcade.csscolor.WHITE
        self.bold = True

    def get_text_label(self):
        return self.text_label

    def set_text_label(self, value):
        self.text_label = value
        return self

    def set_text_color(self, value):
        self.text_color = value
        return self

    def build_label(self, text):
        return arcade.gui.UILabel(
            text=text,
            text_color=self.text_color,
            font_size=app_config.MENU_FONT_SIZE,
            font_name=app_config.MENU_FONT_NAMES,
            bold=self.bold
        )


    @abc.abstractmethod
    def build(self):
        raise NotImplemented("Not implemented")
