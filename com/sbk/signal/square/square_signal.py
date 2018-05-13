from com.sbk.dsp.constants import PI2
from com.sbk.func.unbias.unbias import unbias
from com.sbk.signal.sinusoid import Sinusoid

import numpy as np


class SquareSignal(Sinusoid):
    """Represents a square signal."""

    def evaluate(self, ts):
        """Evaluates the signal at the given times.

        ts: float array of times

        returns: float wave array
        """
        ts = np.asarray(ts)
        cycles = self.freq * ts + self.offset / PI2
        frac, _ = np.modf(cycles)
        ys = self.amp * np.sign(unbias(frac))
        return ys