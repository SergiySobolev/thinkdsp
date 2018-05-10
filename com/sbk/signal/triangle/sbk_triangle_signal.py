import numpy as np

from com.sbk.signal.sinusoid import Sinusoid


class SbkTriangleSignal(Sinusoid):

    def evaluate(self, ts):
        ts = np.asarray(ts)
        a = self.amp
        p = self.period
        ys = (a / p) * (p - abs(ts % (2 * p) - p))
        return ys