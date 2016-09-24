"""
The Jukebar library.
"""

import os
import threading
from random import randint
from time import sleep
from kivy.utils import platform
# from kivy.config import Config
from kivy.core.audio import SoundLoader
from mixers.jukebar_mixer_factory import JukebarMixerFactory


MUSIC_DIRECTORY = "interrupt_songs"
# Config.set('kivy', 'log_level', 'trace')
jukebar_mixer = JukebarMixerFactory.create()


class Jukebar(object):

    def __init__(self, stop_event=None):
        """
        Args:
            stop_event (threading.Event): Used to stop the worker.
        """
        self._stop_event = stop_event

    def play_music(self, title):
        title_path = os.path.join(MUSIC_DIRECTORY, title)
        print "playing title: %s" % title_path
        sound = SoundLoader.load(title_path)
        # explicitly unmuting seems required on Windows
        if platform == "win":
            jukebar_mixer.unmute_current_pid()
        sound.play()
        while sound.state == 'play':
            if self.should_stop():
                sound.stop()
            else:
                sleep(1)

    def play_next_random(self):
        title_random_index = randint(0, len(self._musics)-1)
        title = self._musics[title_random_index]
        self.play_music(title)

    def play_next(self):
        self.play_next_random()

    def fade_up_main_track(self):
        """
        Unmutes song of main track.
        """
        jukebar_mixer.unmute_all()

    def fade_down_main_track(self):
        """
        Mutes song of main track.
        """
        jukebar_mixer.mute_all()

    def interup(self):
        self.fade_down_main_track()
        self.play_next()
        self.fade_up_main_track()

    def should_stop(self):
        if self._stop_event is None:
            return False
        return self._stop_event.is_set()

    def run(self, musics, min_sleep_time=1, max_sleep_time=10):
        """
        Starts the application for testing
        """
        self._musics = musics
        while not self.should_stop():
            random_time = randint(min_sleep_time, max_sleep_time)
            sleep(random_time)
            self.interup()


class JukebarThread(threading.Thread):

    def __init__(self, musics, min_sleep_time, max_sleep_time):
        super(JukebarThread, self).__init__()
        self._stop_event = threading.Event()
        self._musics = musics
        self._min_sleep_time = min_sleep_time
        self._max_sleep_time = max_sleep_time
        self.jukebar = Jukebar(stop_event=self._stop_event)

    def run(self):
        self.jukebar.run(
                min_sleep_time=self._min_sleep_time,
                max_sleep_time=self._max_sleep_time)

    def stop(self):
        """
        Stops the thread.
        """
        self._stop_event.set()

    def stop_requested(self):
        """
        Returns True if the thread was requested to stop.
        """
        return self._stop_event.isSet()
