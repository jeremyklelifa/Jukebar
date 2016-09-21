"""
Base mixer class with simple mixer actions.
"""


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
        # psutil is not available on Android
        import psutil
        current_pid = psutil.Process().pid
        self.unmute_pid(current_pid)
