from com.sbk.signal.signal import Signal

import numpy as np

class SilentSignal(Signal):
    """Represents silence."""

    def evaluate(self, ts):
        """Evaluates the signal at the given times.

        ts: float array of times

        returns: float wave array
        """
        return np.zeros(len(ts))