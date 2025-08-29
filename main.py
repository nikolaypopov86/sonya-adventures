"""
Example of Pymunk Physics Engine Platformer
"""

import arcade

SCREEN_TITLE = "PyMunk Platformer"
SPRITE_IMAGE_SIZE = 128

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_TILES = 0.5

SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SCREEN_GRID_WIDTH = 25
SCREEN_GRID_HEIGHT = 15

SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

class GameWindow(arcade.Window):
    """Main Window"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Player sprite
        self.player_sprite: arcade.Sprite | None = None

        # Sprite Lists we need
        self.player_list: arcade.SpriteList | None = None
        self.wall_list: arcade.SpriteList | None = None
        self.bullet_list: arcade.SpriteList | None = None
        self.item_list: arcade.SpriteList | None = None

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False

        # Set background color


    def setup(self):
        pass

    def on_key_press(self, key, modifiers):
        pass

    def on_key_release(self, key, modifiers):
        pass

    def on_update(self, delta_time):
        pass

    def on_draw(self):
        self.clear()


def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()