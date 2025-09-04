from math import floor
from time import monotonic

from misc.app_utils import singleton
from misc.config import AppConfig

app_config = AppConfig()


@singleton
class SimpleTimer:
    def __init__(self):
        self.is_ticking = False
        self.time_start: float | None = None
        self.seconds: int | None = None
        self.timer_on: bool = True

    def get_seconds(self):
        return self.seconds

    def set_seconds(self, value: int):
        self.seconds = value

    def start(self):
        self.time_start = monotonic()
        self.is_ticking = True

    def pause(self):
        self.seconds -= (monotonic() - self.time_start)
        self.is_ticking = False

    def is_up(self):
        if not app_config.TIMER_ON or not self.is_ticking:
            return False
        if monotonic() - (self.time_start + self.seconds) >= 0:
            self.is_ticking = False
            return True

    def left(self):
        if app_config.TIMER_ON:
            return floor(self.time_start + self.seconds - monotonic())
        else:
            return 0


    # TODO: решить проблему - установка времени при отключении / включении таймера
    def left_text(self):
        if app_config.TIMER_ON:
            l = int(self.time_start + self.seconds - monotonic())
            return "{:02d}:{:02d}".format(l // 60, l % 60)
        return "--:--"
