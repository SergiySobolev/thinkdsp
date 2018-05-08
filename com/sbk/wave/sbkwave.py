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

    def segment(self, start=None, duration=None):
        """Extracts a segment.

        start: float start time in seconds
        duration: float duration in seconds

        returns: Wave
        """
        if start is None:
            start = self.ts[0]
            i = 0
        else:
            i = self.find_index(start)

        j = None if duration is None else self.find_index(start + duration)
        return self.slice(i, j)

    def slice(self, i, j):
        """Makes a slice from a Wave.

        i: first slice index
        j: second slice index
        """
        ys = self.ys[i:j].copy()
        ts = self.ts[i:j].copy()
        return SbkWave(ys, ts, self.frame_rate)
