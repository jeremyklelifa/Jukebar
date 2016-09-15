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
from pycaw.pycaw import AudioUtilities


musics = []
MUSIC_DIRECTORY = "interrupt_songs"

def load_mp3_files():
    """
    Creates the mp3 list from what is found in the directory.
    """
    files = os.listdir(MUSIC_DIRECTORY)
    global musics
    musics.extend(files)

def unmute_myself():
    """
    Unmute the current running process.
    """
    current_pid = psutil.Process().pid
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session.SimpleAudioVolume
        if session.Process and session.Process.pid == current_pid:
            volume.SetMute(0, None)

def mute_all(mute=True):
    """
    Mutes or unmutes all session depending on the mute parameter.
    """
    sessions = AudioUtilities.GetAllSessions()
    mute_int = 1 if mute else 0
    for session in sessions:
        volume = session.SimpleAudioVolume
        volume.SetMute(mute_int, None)

def unmute_all():
    mute_all(False)

def play_music(title):
    title_path = os.path.join(MUSIC_DIRECTORY, title)
    print "playing title: %s" % title_path
    #sleep(3) # simulates the music is playing
    #return
    mixer.init()
    mixer.music.load(title_path)
    mixer.music.play()
    unmute_myself()
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
    unmute_all()

def fade_down_main_track():
    """
    Mutes song of main track.
    """
    print "fading main track down"
    mute_all()

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
