from views.components.labeled import Labeled
from misc.config import AppConfig

import arcade
import arcade.gui

app_config = AppConfig()


class SliderGroupBuilder(Labeled):
    def __init__(self):
        super().__init__()

        self.width = 256
        self.height = 30

        self.value_min: float = 0
        self.value_max: float = 1
        self.default_value: float = 1
        self.step = 0.1
        self.event = None

    def get_value_min(self):
        return self.value_min

    def set_value_min(self, value):
        self.value_min = value
        return self

    def get_value_max(self):
        return self.value_max

    def set_value_max(self, value):
        self.value_max = value
        return self

    def get_default_value(self):
        return self.default_value

    def set_default_value(self, value):
        self.default_value = value
        return self

    def get_step(self):
        return self.step

    def set_step(self, value):
        self.step = value
        return self

    def build(self):
        label = self.build_label(self.text_label)

        label_min = self.build_label(f"{int(self.value_min/self.step)}")
        label_max = self.build_label(f"{int(self.value_max/self.step)}")

        slider = arcade.gui.UISlider(
            value=self.default_value,
            min_value=self.value_min,
            max_value=self.value_max,
            width=self.width,
            step=self.step
        )

        group_inner = arcade.gui.UIBoxLayout(
            vertical=False,
            space_between=10
        )

        group_inner.add(label_min)
        group_inner.add(slider)
        group_inner.add(label_max)

        group_outer = arcade.gui.UIBoxLayout(
            vertical=True,
            space_between=10
        )

        group_outer.add(label)
        group_outer.add(group_inner)

        return group_outer


