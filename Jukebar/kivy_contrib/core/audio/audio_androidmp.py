'''
Audio Android MediaPlayer
===============
Implementation of Sound with the android.media.MediaPlayer
using pyjnius.
https://developer.android.com/reference/android/media/MediaPlayer.html
'''

from jnius import autoclass, PythonJavaClass, java_method
from kivy.core.audio import Sound, SoundLoader


class OnCompletionListener(PythonJavaClass):
    __javainterfaces__ = ('android.media.MediaPlayer$OnCompletionListener',)

    def __init__(self, sound):
        super(OnCompletionListener, self).__init__()
        self.sound = sound

    @java_method('(Landroid/media/MediaPlayer;)V')
    def onCompletion(self, mp):
        print 'onCompletion() called', mp
        # makes sure the sound.state gets updated
        self.sound.stop()


class SoundAndroidMp(Sound):

    @staticmethod
    def extensions():
        """
        https://developer.android.com/guide/appendix/media-formats.html
        """
        return (
                '3gp', 'mp4', 'm4a', 'aac', 'flac', 'mp3', 'mid', 'xmf',
                'mxmf', 'rtttl', 'rtx', 'ota', 'imy', 'ogg', 'wav', 'mkv',
                'webm')

    def __init__(self, **kwargs):
        MediaPlayer = autoclass('android.media.MediaPlayer')
        self._media_player = MediaPlayer()
        self.completion_listener = OnCompletionListener(self)
        self._media_player.setOnCompletionListener(self.completion_listener)
        super(SoundAndroidMp, self).__init__(**kwargs)

    def play(self):
        if self._media_player is None:
            return
        self._media_player.start()
        super(SoundAndroidMp, self).play()

    def stop(self):
        if self._media_player is None:
            return
        self._media_player.stop()
        super(SoundAndroidMp, self).stop()

    def load(self):
        if self._media_player is None:
            return
        if self.filename is None:
            return
        self._media_player.setDataSource(self.filename)
        self._media_player.prepare()

    def unload(self):
        pass

    def seek(self, position):
        if self._media_player is None:
            return
        msec = position * 1000
        self._media_player.seekTo(msec)

    def get_pos(self):
        if self._media_player is None:
            return
        msec = self._media_player.getCurrentPosition()
        position_seconds = msec / 1000.0
        return position_seconds

    def on_volume(self, instance, volume):
        if self._media_player is None:
            return
        left_volume = volume
        right_volume = volume
        self._media_player.setVolume(left_volume, right_volume)

    def _get_length(self):
        if self._media_player is None:
            return super(SoundAndroidMp, self)._get_length()
        duration_msec = self._media_player.getDuration()
        duration_sec = duration_msec / 1000.0
        return duration_sec


SoundLoader.register(SoundAndroidMp)
