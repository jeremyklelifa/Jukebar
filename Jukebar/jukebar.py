"""
Was installing pygame and then trying to play the songs with it.
Finished installing hg, next up is to install pygame really and see if it's playing.
sudo pip install hg+http://bitbucket.org/pygame/pygame
Also take a look at pyglet python module for playing mp3.
"""

import os
from random import randint
from time import sleep
import psutil
import wave
from pygame import mixer # Load the required library
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
        mute = True
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

    def set_mute_all(self, mute=True):
        sessions = AudioUtilities.GetAllSessions()
        mute_int = 1 if mute else 0
        for session in sessions:
            volume = session.SimpleAudioVolume
            volume.SetMute(mute_int, None)

    def set_mute_pid(self, mute, pid):
        sessions = AudioUtilities.GetAllSessions()
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
        sink_list = self.pulse.sink_list()
        for sink in sink_list:
            self.pulse.mute(sink, mute)

    def set_mute_pid(self, mute, pid):
        sink_input_list = self.pulse.sink_input_list()
        for sink in sink_input_list:
            proplist = sink.proplist
            if proplist.get('application.process.id') == pid:
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


def load_mp3_files():
    """
    Creates the mp3 list from what is found in the directory.
    """
    files = os.listdir(MUSIC_DIRECTORY)
    global musics
    musics.extend(files)

def play_music(title):
    title_path = os.path.join(MUSIC_DIRECTORY, title)
    print "playing title: %s" % title_path
    #sleep(3) # simulates the music is playing
    #return
    mixer.init()
    mixer.music.load(title_path)
    mixer.music.play()
    jukebar_mixer.unmute_current_pid()
    while mixer.music.get_busy():
        sleep(1)

def play_next_random():
    title_random_index = randint(0, len(musics)-1) # TODO verify lower bound inclusion
    title = musics[title_random_index]
    play_music(title)

def play_next():
    play_next_random()

"""
def start_rand_timer():
    t = Timer(1.0, stop_current_and_play_next)
"""

def fade_up_main_track():
    """
    Unmutes song of main track.
    """
    print "fading main track back up"
    jukebar_mixer.unmute_all()

def fade_down_main_track():
    """
    Mutes song of main track.
    """
    print "fading main track down"
    jukebar_mixer.mute_all()

def interup():
    fade_down_main_track()
    play_next()
    fade_up_main_track()

def run_jukebar():
    """ 
    Starts the application for testing
    """
    load_mp3_files()
    MAX_SLEEP_TIME = 10
    count = 3
    while count > 0:
        random_time = randint(1, MAX_SLEEP_TIME)
        sleep(random_time)
        interup()
        count -= 1
