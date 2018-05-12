import numpy as np

from com.sbk.signal.sinusoid import Sinusoid


class SbkTriangleSignal(Sinusoid):

    # TODO implement generation of triangle wave
    def evaluate(self, ts):
        ts = np.asarray(ts)
        a = self.amp
        p = self.period

        half_p = -np.arange(start=-a, stop=a)
        v1 = ts % (2 * p)
        v2 = v1 - p
        v3 = abs(v2)
        v4 = p - v3
        ys = (a / p) * (p - abs(ts % (2 * p) - p))
        return ys