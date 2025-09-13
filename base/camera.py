from misc.config import AppConfig

import arcade

app_config = AppConfig()


class PlayerCamera(arcade.Camera2D):
    def __init__(
            self,
            map_width: float | None,
            map_height: float | None,
            player_sprite: arcade.Sprite | None = None
    ):
        super().__init__()

        self.camera_min_x = app_config.WINDOW_WIDTH // 2
        self.camera_max_x = map_width - (app_config.WINDOW_WIDTH // 2)
        self.camera_min_y = app_config.WINDOW_HEIGHT // 2
        self.camera_max_y = map_height - (app_config.WINDOW_HEIGHT // 2)

        self.player_sprite = player_sprite

    def set_position(self):
        camera_x: int
        camera_y: int

        player_x = self.player_sprite.position[0]
        player_y = self.player_sprite.position[1]

        if player_x < self.camera_min_x:
            camera_x = self.camera_min_x
        elif self.camera_min_x < player_x < self.camera_max_x:
            camera_x = player_x
        else:
            camera_x = self.camera_max_x

        if player_y < self.camera_min_y:
            camera_y = self.camera_min_y
        elif self.camera_min_y < player_y < self.camera_max_y:
            camera_y = player_y
        else:
            camera_y = self.camera_max_y

        self.position = camera_x, camera_y