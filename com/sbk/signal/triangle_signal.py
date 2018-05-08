from com.sbk.dsp.sbkdsp import Sinusoid,  PI2

import numpy as np

from com.sbk.func.normalize.normalize import normalize
from com.sbk.func.unbias.unbias import unbias


class TriangleSignal(Sinusoid):
    """Represents a triangle signal."""

    def evaluate(self, ts):
        """Evaluates the signal at the given times.

        ts: float array of times

        returns: float wave array
        """
        ts = np.asarray(ts)
        cycles = self.freq * ts + self.offset / PI2
        frac, _ = np.modf(cycles)
        ys = np.abs(frac - 0.5)
        ys = normalize(unbias(ys), self.amp)
        return ys