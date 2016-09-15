"""
Mutes the volume of all processes, but unmutes chrome.exe process.
"""
from examples import audio_endpoint_volume_example
from pycaw.pycaw import AudioUtilities

"""

def main():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session.SimpleAudioVolume
        if session.Process and session.Process.name() == "chrome.exe":
            print "Chrome found"
            volume.SetMute(0, None)
        else:
            volume.SetMute(1, None)

"""
def print_list():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process:
            print "session.Process.name():", session.Process.name()
        else:
            print "session.DisplayName:", session.DisplayName


def main():
    audio_endpoint_volume_example.main()
    print_list()

if __name__ == "__main__":
    main()
