from com.sbk.dsp.sbkdsp import Wave


class SbkWave(Wave):

    def __init__(self, ys=None, ts=None, frame_rate=None, wave=None):
        if wave is None:
            super().__init__(ys, ts, frame_rate)
        else:
            super().__init__(wave.ys, wave.ts, wave.frame_rate)

    @property
    def ts_duration(self):
        return self.end - self.start

    def stretch(self, stretch_factor):
        new_ts = self.ts * stretch_factor
        new_frame_rate = self.frame_rate / stretch_factor
        return SbkWave(ys=self.ys, ts=new_ts, frame_rate=new_frame_rate)
