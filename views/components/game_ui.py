from typing import Tuple

import arcade

from misc.config import AppConfig
from views.components.game_ui_text import GameUIText

app_config = AppConfig()

EMOJI_FONT_NAME = "Segoe UI Emoji"
TEXT_COLOR = arcade.csscolor.BLACK

class GameUI:
    def __init__(self):
        self.score_text: arcade.Text | None = None
        self.life_text: arcade.Text | None = None
        self.coins_to_find: arcade.Text | None = None
        self.coin_symb: arcade.Text | None = None
        self.level_text: arcade.Text | None = None
        self.timer_text: arcade.Text | None = None
        self.fruit_symb: arcade.Text | None = None
        self.fruit_to_find: arcade.Text | None = None

        self.widgets: Tuple[arcade.Text] | None = None

    def init(
            self,
            score: int,
            life_points: int,
            coin_total: int,
            coin_remained: int,
            level: int,
            timer_left: str,
            fruit_total: int,
            fruit_remained: int
    ):
        self.score_text = GameUIText(
            text=f"Score: {score}",
            x=app_config.WINDOW_WIDTH * 7 // 40,
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            color=TEXT_COLOR
        )

        self.life_text = GameUIText(
            text=f"{' ♥' * life_points}",
            x=app_config.WINDOW_WIDTH - (app_config.WINDOW_WIDTH // 200),
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            color=(255, 0, 0),
            font_name=EMOJI_FONT_NAME,
            font_size=app_config.WINDOW_HEIGHT // 28,
            align="right",
            anchor_x="right"
        )

        self.coins_to_find = GameUIText(
            text=f"{coin_total - coin_remained}/{coin_total}",
            x=app_config.WINDOW_WIDTH * 4 // 42,
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            color=TEXT_COLOR,
            font_name=app_config.FONT_NAME,
        )

        self.coin_symb = GameUIText(
            text="🟡",
            x=app_config.WINDOW_WIDTH // 48,
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            color=(255, 215, 0),
            font_name=EMOJI_FONT_NAME,
            font_size=app_config.WINDOW_HEIGHT // 30
        )

        self.fruit_symb = GameUIText(
            "🍉",
            x=app_config.WINDOW_WIDTH // 66,
            y=app_config.WINDOW_HEIGHT * 85 // 100,
            font_name=EMOJI_FONT_NAME,
            font_size=app_config.WINDOW_HEIGHT // 25
        )

        self.fruit_to_find = GameUIText(
            f"{fruit_total - fruit_remained}/{fruit_total}",
            x=app_config.WINDOW_WIDTH * 4 // 42,
            y=app_config.WINDOW_HEIGHT * 86 // 100,
            color=TEXT_COLOR,
            font_name=app_config.FONT_NAME,
        )

        self.timer_text = GameUIText(
            f"{timer_left}",
            x=app_config.WINDOW_WIDTH * 22 // 40,
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            anchor_x="center",
            color=TEXT_COLOR
        )

        self.level_text = GameUIText(
            f"Lvl: {level}",
            x=app_config.WINDOW_WIDTH * 16 // 40,
            y=app_config.WINDOW_HEIGHT * 93 // 100,
            anchor_x="center",
            color=TEXT_COLOR,
            font_name=app_config.FONT_NAME,
            font_size=app_config.WINDOW_HEIGHT * 2 // 100
        )

        self.widgets = (
            self.score_text,
            self.life_text,
            self.coins_to_find,
            self.coin_symb,
            self.level_text,
            self.timer_text,
            self.fruit_symb,
            self.fruit_to_find
        )

    def update(
            self,
            score: int,
            life_points,
            coin_total,
            coin_count,
            level,
            timer_left,
            fruit_total,
            fruit_count
    ):
        self.score_text.text = f"Score: {score}"
        self.life_text.text = f"{' ♥' * life_points}"
        self.coins_to_find.text = f"{coin_count}/{coin_total}"
        self.level_text.text = f"Lvl: {level}"
        self.timer_text.text = f"{timer_left}"
        self.fruit_to_find.text = f"{fruit_count}/{fruit_total}"

    def get_widgets(self):
        return self.widgets
