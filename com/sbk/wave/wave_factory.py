from com.sbk.wave.iwave_factory import IWaveFactory
from com.sbk.wave.wave import Wave


class WaveFactory(IWaveFactory):

    def create_wave(self, ys, ts=None, frame_rate=None):
        return Wave(ys, ts, frame_rate)

    def create_wave_sbk(self, ys, ts=None, frame_rate=None):
        return Wave(ys, ts, frame_rate)