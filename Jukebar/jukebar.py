﻿"""
The Jukebar library.
"""

import os
import threading
from random import randint
from time import sleep
from kivy import kivy_options
from kivy.core import core_register_libs
from kivy.utils import platform
from kivy.config import Config
from kivy.core.audio import SoundLoader


musics = []
MUSIC_DIRECTORY = "interrupt_songs"
Config.set('kivy', 'log_level', 'trace')



def load_audio_androidmp():
    """
    Loads the audio_androidmp implementation,
    it supports a lot of media formats.
    """
    kivy_options['audio'] += ('androidmp',)
    additional_audio_libs = [('androidmp', 'audio_androidmp')]
    base = 'kivy_contrib.core'
    libs_loaded = core_register_libs('audio', additional_audio_libs, base)

def load_jnius_nih():
    """
    Creates org.jnius.NativeInvocationHandler once in the main thread
    to wordaround the error:
    JavaException: Class not found 'org/jnius/NativeInvocationHandler'
    see:
      - https://github.com/kivy/pyjnius/issues/137
      - https://github.com/kivy/pyjnius/issues/223
      - http://stackoverflow.com/a/27943091/185510
    """
    from jnius import autoclass
    autoclass('org.jnius.NativeInvocationHandler')

if platform == "android":
    load_audio_androidmp()
    load_jnius_nih()


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
        import psutil
        current_pid = psutil.Process().pid
        self.unmute_pid(current_pid)


class JukebarMixerWindows(JukebarMixerAbstract):
    """
    Windows mixer class implementation.
    """

    def __init__(self):
        from pycaw.pycaw import AudioUtilities
        self.AudioUtilities = AudioUtilities

    def get_all_sessions(self):
        """
        CoInitialize() must be called before creating COM objects on a thread
        http://stackoverflow.com/a/3246562
        """
        import comtypes
        comtypes.CoInitialize()
        sessions = self.AudioUtilities.GetAllSessions()
        return sessions

    def set_mute_all(self, mute=True):
        sessions = self.get_all_sessions()
        mute_int = 1 if mute else 0
        for session in sessions:
            volume = session.SimpleAudioVolume
            volume.SetMute(mute_int, None)

    def set_mute_pid(self, mute, pid):
        sessions = self.get_all_sessions()
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


class JukebarMixerAndroid(JukebarMixerAbstract):
    """
    Android mixer class implementation.
    """

    def __init__(self):
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        self.activity = PythonActivity.mActivity

    def _music_service_command(self, command):
        """
        Broadcasts musicservicecommand.
        Gives 2 tries:
            1) via com.android.music.musicservicecommand
            2) via com.sec.android.app.music.musicservicecommand
        """
        from jnius import autoclass
        Intent = autoclass('android.content.Intent')
        # 1) try via com.android.music.musicservicecommand
        intent = Intent(
                "com.android.music.musicservicecommand." + command)
        intent.putExtra("command", command)
        self.activity.sendBroadcast(intent)
        # 2) try via com.sec.android.app.music.musicservicecommand
        intent = Intent(
                "com.sec.android.app.music.musicservicecommand." + command)
        intent.putExtra("command", command)
        self.activity.sendBroadcast(intent)

    def _pause_music_player(self):
        """
        Pauses the default music player.
        """
        self._music_service_command("pause")

    def _play_music_player(self):
        self._music_service_command("play")

    def _set_mute_music_channel(self, mute):
        """
        Actually only (un)mutes the music "channel", since it will be
        the background music.
        On Android there're different "channels":
            - music
            - notification
            - alarm
            - ring
            - system
        """
        from jnius import autoclass, cast
        Context = autoclass('android.content.Context')
        AudioManager = autoclass('android.media.AudioManager')
        self.audio_manager = cast(
            'android.media.AudioManager',
            self.activity.getSystemService(Context.AUDIO_SERVICE))
        self.audio_manager.setStreamMute(AudioManager.STREAM_MUSIC, mute)

    def set_mute_all(self, mute):
        """
        Play/Pause the default music player rather than unmute/mute.
        """
        if mute:
            self._pause_music_player()
        else:
            self._play_music_player()


class JukebarMixerFactory(JukebarMixerAbstract):
    """
    Uses the correct mixer depending on platform.
    """

    @staticmethod
    def create():
        if platform == "win":
            jukebar_mixer = JukebarMixerWindows()
        elif platform == "linux":
            jukebar_mixer = JukebarMixerLinux()
        elif platform == "android":
            jukebar_mixer = JukebarMixerAndroid()
        return jukebar_mixer


jukebar_mixer = JukebarMixerFactory.create()


class Jukebar(object):

    def __init__(self, stop_event=None):
        """
        Args:
            stop_event (threading.Event): Used to stop the worker.
        """
        self._stop_event = stop_event

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

    def should_stop(self):
        if self._stop_event is None:
            return False
        return self._stop_event.is_set()

    def run(self, min_sleep_time=1, max_sleep_time=10):
        """
        Starts the application for testing
        """
        print "Jukebar.run() begin"
        self.load_mp3_files()
        print "min_sleep_time:", min_sleep_time
        print "max_sleep_time:", max_sleep_time
        while not self.should_stop():
            random_time = randint(min_sleep_time, max_sleep_time)
            sleep(random_time)
            self.interup()
        print "Jukebar.run() end"


class JukebarThread(threading.Thread):

    def __init__(self, min_sleep_time, max_sleep_time):
        super(JukebarThread, self).__init__()
        self._stop_event = threading.Event()
        self._min_sleep_time = min_sleep_time
        self._max_sleep_time = max_sleep_time
        self.jukebar = Jukebar(stop_event=self._stop_event)

    def run(self):
        print "JukebarThread.run() begin"
        self.jukebar.run(
                min_sleep_time=self._min_sleep_time,
                max_sleep_time=self._max_sleep_time)
        print "JukebarThread.run() end"

    def stop(self):
        """
        Stops the thread.
        """
        print "JukebarThread.stop()"
        self._stop_event.set()

    def stop_requested(self):
        """
        Returns True if the thread was requested to stop.
        """
        return self._stop_event.isSet()
