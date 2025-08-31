import os

import arcade


class SoundPlayer:
    def __init__(self):
        # volume levels
        self.music_volume = float(os.environ.get("VOLUME_MUSIC"))
        self.sound_volume = float(os.environ.get("VOLUME_SOUND"))

        # load music data
        self.music = arcade.load_sound(":data:/sounds/time_for_adventure.mp3")
        self.jump_sound = arcade.load_sound(":data:/sounds/jump.wav")

    def play_music(
            self
    ):
        arcade.play_sound(
            self.music,
            volume=self.music_volume,
            loop=True
        )

    def sound_jump(
            self
    ):
        arcade.play_sound(
            self.jump_sound,
            volume=self.sound_volume
        )

    @property
    def music_vol(self):
        return self.music_volume

    @music_vol.setter
    def music_vol(self, value):
        self.music_volume = value

    @property
    def sound_vol(self):
        return self.sound_volume

    @sound_vol.setter
    def sound_vol(self, value):
        self.sound_volume = value
