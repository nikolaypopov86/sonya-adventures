import uuid
import logging

from misc.config import AppConfig

import arcade

logger = logging.getLogger(__name__)
app_config = AppConfig()


class MiniMap():
    def __init__(self):
        self.sprite_list: arcade.SpriteList | None = None
        self.sprite_lists: tuple | None = None
        self.minimap_texture: arcade.Texture | None = None
        self.sprite: arcade.Sprite | None = None
        self.minimap_on: bool | None = None
        self.minimap_size: Size | None = None
        self.map_size: Size | None = None
        self.rect: arcade.Rect | None = None

    def setup(self, map_size: tuple[float, float]):
        self.map_size = Size(*map_size)

        minimap_size_x = int(app_config.WINDOW_WIDTH * app_config.MINIMAP_WIDTH_PART)
        self.minimap_size = Size(
            minimap_size_x,
            int(minimap_size_x / (self.map_size.x / self.map_size.y))
        )

        logger.info(f"minimap {self.minimap_size}")

        self.minimap_texture = arcade.Texture.create_empty(
            str(uuid.uuid4()), self.minimap_size.get_tuple
        )
        self.sprite = arcade.Sprite(
            self.minimap_texture,
            center_x=self.minimap_size.x,
            center_y=self.minimap_size.y
        )

        self.sprite.position = self.get_coord()

        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.sprite)

        self.rect = arcade.shape_list.create_rectangle_outline(
            self.sprite.position[0],
            self.sprite.position[1],
            width=self.minimap_size.x,
            height=self.minimap_size.y,
            color=(0,0,0,255)
        )

    def get_coord(self) -> tuple[int, int]:
        return (
            app_config.WINDOW_WIDTH - self.minimap_size.x / 2 if app_config.MINIMAP_POS_X else self.minimap_size.x // 2,
            app_config.WINDOW_HEIGHT * 7 // 8 - self.minimap_size.y / 2 if app_config.MINIMAP_POS_Y else self.minimap_size.y // 2
        )


    def update(self, player_sprite):
        proj = 0, self.map_size.x, 0, self.map_size.y
        atlas: arcade.texture_atlas.TextureAtlasBase = self.sprite_list.atlas
        with atlas.render_into(self.minimap_texture, projection=proj) as fbo:
            fbo.clear(color=app_config.MENU_BACKGROUND_COLOR)
            for sprite_list in self.sprite_lists:
                logger.debug(sprite_list)
                sprite_list.draw()
            arcade.draw_point(
                player_sprite.position[0],
                player_sprite.position[1] - 32,
                color=arcade.csscolor.MAGENTA,
                size=50
            )

    def draw(self):
        self.sprite_list.draw()

    def draw_outline(self):
        self.rect.draw()

class Size:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def get_tuple(self):
        return self.x, self.y

    def __str__(self):
        return f"size {self.x} X {self.y}"

