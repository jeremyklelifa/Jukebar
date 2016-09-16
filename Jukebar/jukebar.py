"""
The Jukebar library.
"""

import os
from random import randint
from time import sleep
import psutil
from pygame import mixer
import platform


musics = []
MUSIC_DIRECTORY = "interrupt_songs"


class JukebarMixerAbstract(object):
    """
    Base mixer class with simple mixer actions.
    """

    def set_mute_all(self, mute):
        """
        Mutes or unmutes all session depending on the mute parameter.
        """
        raise NotImplementedError

    def set_mute_pid(self, mute, pid):
        raise NotImplementedError

    def mute_all(self):
        """
        Mutes all sources.
        """
        mute = True
        self.set_mute_all(mute)

    def unmute_all(self):
        """
        Unmutes all sources.
        """
        mute = False
        self.set_mute_all(mute)

    def mute_pid(self, pid):
        """
        Mutes the audio for the given pid.
        """
        mute = True
        self.set_mute_pid(mute, pid)

    def unmute_pid(self, pid):
        """
        Unmutes the audio for the given pid.
        """
        mute = False
        self.set_mute_pid(mute, pid)

    def unmute_current_pid(self):
        """
        Unmutes the current running process.
        """
        current_pid = psutil.Process().pid
        self.unmute_pid(current_pid)


class JukebarMixerWindows(JukebarMixerAbstract):
    """
    Windows mixer class implementation.
    """

    def __init__(self):
        from pycaw.pycaw import AudioUtilities
        self.AudioUtilities = AudioUtilities

    def set_mute_all(self, mute=True):
        sessions = self.AudioUtilities.GetAllSessions()
        mute_int = 1 if mute else 0
        for session in sessions:
            volume = session.SimpleAudioVolume
            volume.SetMute(mute_int, None)

    def set_mute_pid(self, mute, pid):
        sessions = self.AudioUtilities.GetAllSessions()
        mute_int = 1 if mute else 0
        for session in sessions:
            volume = session.SimpleAudioVolume
            if session.Process and session.Process.pid == pid:
                volume.SetMute(mute_int, None)


class JukebarMixerLinux(JukebarMixerAbstract):
    """
    Linux mixer class implementation.
    """

    def __init__(self):
        from pulsectl import Pulse
        self.pulse = Pulse('client1')

    def set_mute_all(self, mute):
        sink_input_list = self.pulse.sink_input_list()
        for sink in sink_input_list:
            self.pulse.mute(sink, mute)

    def set_mute_pid(self, mute, pid):
        sink_input_list = self.pulse.sink_input_list()
        for sink in sink_input_list:
            proplist = sink.proplist
            # for some reason sometimes the value is a string
            if proplist.get('application.process.id') in [pid, str(pid)]:
                self.pulse.mute(sink, mute)


class JukebarMixerFactory(JukebarMixerAbstract):
    """
    Uses the correct mixer depending on platform.
    """

    @staticmethod
    def create():
        if platform.system() == "Windows":
            jukebar_mixer = JukebarMixerWindows()
        else:
            jukebar_mixer = JukebarMixerLinux()
        return jukebar_mixer


jukebar_mixer = JukebarMixerFactory.create()


class Jukebar(object):

    def load_mp3_files(self):
        """
        Creates the mp3 list from what is found in the directory.
        """
        files = os.listdir(MUSIC_DIRECTORY)
        global musics
        musics.extend(files)

    def play_music(self, title):
        title_path = os.path.join(MUSIC_DIRECTORY, title)
        print "playing title: %s" % title_path
        mixer.init()
        mixer.music.load(title_path)
        mixer.music.play()
        jukebar_mixer.unmute_current_pid()
        while mixer.music.get_busy():
            sleep(1)

    def play_next_random(self):
        title_random_index = randint(0, len(musics)-1)
        title = musics[title_random_index]
        self.play_music(title)

    def play_next(self):
        self.play_next_random()

    """
    def start_rand_timer():
        t = Timer(1.0, stop_current_and_play_next)
    """

    def fade_up_main_track(self):
        """
        Unmutes song of main track.
        """
        print "fading main track back up"
        jukebar_mixer.unmute_all()

    def fade_down_main_track(self):
        """
        Mutes song of main track.
        """
        print "fading main track down"
        jukebar_mixer.mute_all()

    def interup(self):
        self.fade_down_main_track()
        self.play_next()
        self.fade_up_main_track()

    def run(self, min_sleep_time=1, max_sleep_time=10):
        """
        Starts the application for testing
        """
        self.load_mp3_files()
        count = 3
        print "min_sleep_time:", min_sleep_time
        print "max_sleep_time:", max_sleep_time
        while count > 0:
            random_time = randint(min_sleep_time, max_sleep_time)
            sleep(random_time)
            self.interup()
            count -= 1
