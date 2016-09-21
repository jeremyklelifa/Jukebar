from kivy import kivy_options
from kivy.core import core_register_libs
from jnius import autoclass, cast
from mixers.jukebar_mixer_abstract import JukebarMixerAbstract


def load_audio_androidmp():
    """
    Loads the audio_androidmp implementation,
    it supports a lot of media formats.
    """
    kivy_options['audio'] += ('androidmp',)
    additional_audio_libs = [('androidmp', 'audio_androidmp')]
    base = 'kivy_contrib.core'
    core_register_libs('audio', additional_audio_libs, base)


def load_jnius_nih():
    """
    Creates org.jnius.NativeInvocationHandler from the main thread
    to wordaround the error:
    JavaException: Class not found 'org/jnius/NativeInvocationHandler'
    see:
      - https://github.com/kivy/pyjnius/issues/137
      - https://github.com/kivy/pyjnius/issues/223
      - http://stackoverflow.com/a/27943091/185510
    """
    autoclass('org.jnius.NativeInvocationHandler')


class JukebarMixerAndroid(JukebarMixerAbstract):
    """
    Android mixer class implementation.
    """

    def __init__(self):
        load_audio_androidmp()
        load_jnius_nih()
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        self.activity = PythonActivity.mActivity

    def _music_service_command(self, command):
        """
        Broadcasts musicservicecommand.
        Gives 2 tries:
            1) via com.android.music.musicservicecommand
            2) via com.sec.android.app.music.musicservicecommand
        """
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
