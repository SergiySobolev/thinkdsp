import abc


class IWaveFactory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_wave(self, ys, ts=None, frame_rate=None):
        pass

    @abc.abstractmethod
    def create_wave_sbk(self, ys, ts=None, frame_rate=None):
        pass
