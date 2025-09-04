import os

import arcade.color
from dotenv import load_dotenv
load_dotenv()

from .app_utils import singleton

@singleton
class AppConfig:
    def __init__(self):
        self.SCREEN_TITLE = "My adventures"
        self.SPRITE_IMAGE_SIZE = float(os.environ.get("SPRITE_IMAGE_SIZE"))
        self.SPRITE_SCALING_PLAYER = float(os.environ.get("SPRITE_SCALING_PLAYER"))
        self.SPRITE_SCALING_TILES = float(os.environ.get("SPRITE_SCALING_TILES"))
        self.SPRITE_SIZE = int(self.SPRITE_IMAGE_SIZE * self.SPRITE_SCALING_TILES)

#        self.SCREEN_GRID_WIDTH = int(os.environ.get("SCREEN_GRID_WIDTH"))
#        self.SCREEN_GRID_HEIGHT = int(os.environ.get("SCREEN_GRID_HEIGHT"))

#        self.SCREEN_WIDTH = self.SPRITE_SIZE * self.SCREEN_GRID_WIDTH
#        self.SCREEN_HEIGHT = self.SPRITE_SIZE * self.SCREEN_GRID_HEIGHT

        self.WINDOW_WIDTH = int(os.environ.get("WINDOW_WIDTH"))
        self.WINDOW_HEIGHT = int(os.environ.get("WINDOW_HEIGHT"))

        # Player sprite
        self.PLAYER_SPRITE = os.environ.get("PLAYER_SPRITE")

        # Sprite numbers
        self.WALK_SPRITE_COUNT = 0
        self.IDLE_SPRITE_COUNT = 0
        if self.PLAYER_SPRITE == "knight":
            self.WALK_SPRITE_COUNT = 16
            self.IDLE_SPRITE_COUNT = 4
        elif self.PLAYER_SPRITE == "cat":
            self.WALK_SPRITE_COUNT = 32
            self.IDLE_SPRITE_COUNT = 16

        # Change idle pic counter coefficient
        self.IDLE_PIC_COUNTER_COEF = 50

        # --- Physics forces. Higher number, faster accelerating

        # Gravity
        self.GRAVITY = float(os.environ.get("GRAVITY_CONST")) * self.SPRITE_SCALING_TILES

        # Damping - Amount of speed lost per second
        self.DEFAULT_DUMPING = float(os.environ.get("DEFAULT_DUMPING"))
        self.PLAYER_DUMPING = float(os.environ.get("PLAYER_DUMPING"))

        # Friction between objects
        self.PLAYER_FRICTION = 1.0
        self.WALL_FRICTION = 0.7
        self.DYNAMIC_ITEM_FRICTION = 0.6

        # Mass (defaults to 1)
        self.PLAYER_MASS = 2.0

        # Keep player from going too fast
        self.PLAYER_MAX_HORIZONTAL_SPEED = int(83 * self.SPRITE_SCALING_PLAYER)
        self.PLAYER_MAX_VERTICAL_SPEED = int(150 * self.SPRITE_SCALING_TILES)

        # Force applied while on ground
        self.PLAYER_MOVE_FORCE_ON_GROUND = 2500 * self.SPRITE_SCALING_TILES

        # Force applied when moving left/right in the air
        self.PLAYER_MOVE_FORCE_IN_AIR = 300 * self.SPRITE_SCALING_TILES

        # strength of a jump
        self.PLAYER_JUMP_IMPULSE = 1800 * self.SPRITE_SCALING_TILES

        # Player animations
        self.DEAD_ZONE = 0.1

        # How many pixels to move before we change the texture in the walking animation
        self.DISTANCE_TO_CHANGE_TEXTURE = 7 * self.SPRITE_SCALING_TILES

        # Music and sound
        self.VOLUME_MUSIC = float(os.environ.get("VOLUME_MUSIC"))
        self.VOLUME_SOUND = float(os.environ.get("VOLUME_SOUND"))

        self.BASE_LVL = int(os.environ.get("BASE_LVL"))

        self.MENU_BACKGROUND_COLOR = tuple(map(lambda x: int(x), os.environ.get("MENU_BACKGROUND_COLOR").split(",")))

        self.MINIMAP_BACKGROUND_COLOR = tuple(map(lambda x: int(x), os.environ.get("MINIMAP_BACKGROUNG_COLOR").split(",")))
        self.MINIMAP_WIDTH_PART = float(os.environ.get("MINIMAP_WIDTH_PART"))
        self.MINIMAP_SPRITE_LISTS: list[str] = os.environ.get("MINIMAP_SPRITE_LISTS").split(",")

        self.MINIMAP_POS_X = int(os.environ.get("MINIMAP_POS_X"))
        self.MINIMAP_POS_Y = int(os.environ.get("MINIMAP_POS_Y"))

        self.TIMER_SECONDS = int(os.environ.get("TIMER_SECONDS"))

        self.TIMER_ON = int(os.environ.get("TIMER_ON"))
