import os
import time

import pyglet

# TODO: использовать pyglet или иной плеер с поддержкой паузы треков
class SoundPlayer:
    def __init__(self):

        self.m_player = pyglet.media.Player()
        self.m_player.loop = True
        self.s_player = pyglet.media.Player()

        self.m_player.volume = 0.2 #float(os.environ.get("VOLUME_MUSIC"))
        self.s_player.volume = 1 # float(os.environ.get("VOLUME_SOUND"))

        # load music data
        self.music = pyglet.media.load("data/sounds/time_for_adventure.mp3")
        self.m_player.queue(self.music)

        self.jump_sound = pyglet.media.load("data/sounds/jump.wav")

    def music_volume(self, value):
        self.m_player.volume = value

    def sound_volume(self, value):
        self.s_player.volume = value

    def play_music(self):
        self.m_player.play()

    def play_sound(self):
        pass

if __name__ == '__main__':
    p = SoundPlayer()
    p.play_music()
    p.music_volume(0.5)
    p.play_music()