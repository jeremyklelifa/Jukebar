from mixers.jukebar_mixer_abstract import JukebarMixerAbstract


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
