import numpy as np


def zero_pad(self, n):
    """Trims this wave to the given length.

    n: integer index
    """
    self.ys = zero_pad(self.ys, n)
    self.ts = self.start + np.arange(n) / self.framerate