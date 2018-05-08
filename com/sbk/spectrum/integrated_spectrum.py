import numpy as np

import thinkplot


class IntegratedSpectrum:
    """Represents the integral of a spectrum."""

    def __init__(self, cs, fs):
        """Initializes an integrated spectrum:

        cs: sequence of cumulative amplitudes
        fs: sequence of frequencies
        """
        self.cs = np.asanyarray(cs)
        self.fs = np.asanyarray(fs)

    def plot_power(self, low=0, high=None, expo=False, **options):
        """Plots the integrated spectrum.

        low: int index to start at
        high: int index to end at
        """
        cs = self.cs[low:high]
        fs = self.fs[low:high]

        if expo:
            cs = np.exp(cs)

        thinkplot.plot(fs, cs, **options)

    def estimate_slope(self, low=1, high=-12000):
        """Runs linear regression on log cumulative power vs log frequency.

        returns: slope, inter, r2, p, stderr
        """
        # print self.fs[low:high]
        # print self.cs[low:high]
        x = np.log(self.fs[low:high])
        y = np.log(self.cs[low:high])
        t = scipy.stats.linregress(x, y)
        return t