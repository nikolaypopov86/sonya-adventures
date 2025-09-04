from components.labeled import Labeled
from misc.config import AppConfig

from PIL import Image
import arcade
import arcade.gui

app_config = AppConfig()


class CheckboxGroupBuilder(Labeled):
    def __init__(self):
        super().__init__()

        self.width = 20
        self.height = 20

        self.on_texture: arcade.Texture | None = None
        self.off_texture: arcade.Texture | None = None

        self.event =  None

    def get_on_texture(self):
        return self.on_texture

    def set_on_texture(self, path):
        self.on_texture = arcade.Texture(Image.open(path).convert("RGBA"))
        return self

    def get_off_texture(self):
        return self.off_texture

    def set_off_texture(self, path):
        self.off_texture = arcade.Texture(Image.open(path).convert("RGBA"))
        return self

    def build(self):
        label = self.build_label(self.text_label)

        checkbox = arcade.gui.UITextureToggle(
            on_texture=self.on_texture,
            off_texture=self.off_texture,
            width=20,
            height=20
        )

        self.event = checkbox.event

        checkbox_group = arcade.gui.UIBoxLayout(
            vertical=False,
            space_between=10
        )

        checkbox_group.add(label)
        checkbox_group.add(checkbox)

        return checkbox_group
