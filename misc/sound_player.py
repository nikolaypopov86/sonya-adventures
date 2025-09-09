import logging
import os
from .app_utils import singleton

import arcade
from pyglet.media import Player

logger = logging.getLogger(__name__)

@singleton
class SoundPlayer:
    def __init__(self):
        # volume levels
        self.music_volume = float(os.environ.get("VOLUME_MUSIC"))
        self.sound_volume = float(os.environ.get("VOLUME_SOUND"))

        # load music data
        self.music = arcade.load_sound("data/sounds/time_for_adventure.mp3")
        self.jump_sound = arcade.load_sound("data/sounds/jump.wav")
        self.music_playback: Player | None = None

    def play_music(
            self
    ) -> None:
        logger.debug(f"start playing music: vol={self.music_volume}")
        self.music_playback = arcade.play_sound(
            self.music,
            volume=self.music_volume,
            loop=True
        )

    def sound_jump(
            self
    ) -> Player:
        return arcade.play_sound(
            self.jump_sound,
            volume=self.sound_volume
        )

    @property
    def music_vol(self):
        return self.music_volume

    @music_vol.setter
    def music_vol(self, value: float):
        logger.debug(f"music vol set to: {value}")
        self.music_volume = value

    @property
    def sound_vol(self):
        return self.sound_volume

    @sound_vol.setter
    def sound_vol(self, value: float):
        logger.debug(f"sound vol set to: {value}")
        self.sound_volume = value

    def stop_playing_music(self):
        logger.debug(f"stop playing music")
        self.music_playback.delete()
        logger.debug(f"music playback={self.music_playback}")
