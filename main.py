"""
Example of Pymunk Physics Engine Platformer
"""
import os.path

import arcade

SCREEN_TITLE = "PyMunk Platformer"
SPRITE_IMAGE_SIZE = 16

SPRITE_SCALING_PLAYER = 3
SPRITE_SCALING_TILES = 3

SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SCREEN_GRID_WIDTH = 30
SCREEN_GRID_HEIGHT = 20

SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

class GameWindow(arcade.Window):
    """Main Window"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.background = None
        arcade.resources.add_resource_handle("data", f"{os.path.abspath('.')}/data")

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
        """Set up everything with the game"""

        # Create the sprite lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # Map name
        map_name = ":data:pymunk.tmx"

        # Load in TileMap
        tile_map = arcade.load_tilemap(map_name, SPRITE_SCALING_TILES)

        # Pull the sprite layers out of the tile map
        self.wall_list = tile_map.sprite_lists["Platforms"]
        self.item_list = tile_map.sprite_lists["Dynamic Items"]
        self.background = tile_map.sprite_lists["Background"]
        self.foreground = tile_map.sprite_lists["Foreground"]

        # Create player sprite
        self.player_sprite = arcade.Sprite(
            ":data:knight.png",
            SPRITE_SCALING_PLAYER,
        )
        # Set player location
        grid_x = 1
        grid_y = 3.3
        self.player_sprite.center_x = SPRITE_SIZE * grid_x + SPRITE_SIZE / 2
        self.player_sprite.center_y = SPRITE_SIZE * grid_y + SPRITE_SIZE / 2
        # Add to player sprite list
        self.player_list.append(self.player_sprite)


    def on_key_press(self, key, modifiers):
        pass

    def on_key_release(self, key, modifiers):
        pass

    def on_update(self, delta_time):
        pass

    def on_draw(self):
        """Draw everything"""
        self.clear()
        self.background.draw()
        self.wall_list.draw()
        self.bullet_list.draw()
        self.item_list.draw()
        self.player_list.draw()
        self.foreground.draw()



def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()