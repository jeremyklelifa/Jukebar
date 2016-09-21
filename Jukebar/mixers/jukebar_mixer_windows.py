from mixers.jukebar_mixer_abstract import JukebarMixerAbstract


class JukebarMixerWindows(JukebarMixerAbstract):
    """
    Windows mixer class implementation.
    """

    def __init__(self):
        from pycaw.pycaw import AudioUtilities
        self.AudioUtilities = AudioUtilities

    def get_all_sessions(self):
        """
        CoInitialize() must be called before creating COM objects on a thread,
        see: http://stackoverflow.com/a/3246562
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
