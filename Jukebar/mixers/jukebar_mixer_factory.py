"""
Uses the correct mixer depending on platform.
"""
from kivy.utils import platform


class JukebarMixerFactory(object):
    """
    Uses the correct mixer depending on platform.
    """

    @staticmethod
    def create():
        if platform == "win":
            from mixers.jukebar_mixer_windows import JukebarMixerWindows
            jukebar_mixer = JukebarMixerWindows()
        elif platform == "linux":
            from mixers.jukebar_mixer_linux import JukebarMixerLinux
            jukebar_mixer = JukebarMixerLinux()
        elif platform == "android":
            from mixers.jukebar_mixer_android import JukebarMixerAndroid
            jukebar_mixer = JukebarMixerAndroid()
        return jukebar_mixer
