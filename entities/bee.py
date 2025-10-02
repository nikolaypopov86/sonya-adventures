import random

import arcade


class BeeAnimation:
    def __init__(self):
        self.textures = dict()

        self.states = ["Idle_1", "Idle_2", "Idle_3", "Idle_4", "Idle_5"]
        self.directions = ["R", "L"]

        for state in self.states:
            for direction in self.directions:
                key = f"{state}_{direction}"
                self.textures[key] = []
                for i in range(1, 5):
                    texture = arcade.load_texture(f"data/tilesets/bee/{state}/{state}_{direction}_{i}.png")
                    self.textures[key].append(texture)


    def get_random_textures(self):
        return self.textures[f"{random.choice(self.states)}_{random.choice(["R", "L"])}"]
