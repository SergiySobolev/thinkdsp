import copy
import numpy as np
import scipy
import thinkplot
from com.sbk.func.findindex.find_index import find_index


class _SpectrumParent:
    """Contains code common to Spectrum and DCT.
    """

    def __init__(self, hs, fs, framerate, full=False):
        """Initializes a spectrum.

        hs: array of amplitudes (real or complex)
        fs: array of frequencies
        framerate: frames per second
        full: boolean to indicate full or real FFT
        """
        self.hs = np.asanyarray(hs)
        self.fs = np.asanyarray(fs)
        self.framerate = framerate
        self.full = full

    @property
    def max_freq(self):
        """Returns the Nyquist frequency for this spectrum."""
        return self.framerate / 2

    @property
    def amps(self):
        """Returns a sequence of amplitudes (read-only property)."""
        return np.absolute(self.hs)

    @property
    def power(self):
        """Returns a sequence of powers (read-only property)."""
        return self.amps ** 2

    def copy(self):
        """Makes a copy.

        Returns: new Spectrum
        """
        return copy.deepcopy(self)

    def max_diff(self, other):
        """Computes the maximum absolute difference between spectra.

        other: Spectrum

        returns: float
        """
        assert self.framerate == other.framerate
        assert len(self) == len(other)

        hs = self.hs - other.hs
        return np.max(np.abs(hs))

    def ratio(self, denom, thresh=1, val=0):
        """The ratio of two spectrums.

        denom: Spectrum
        thresh: values smaller than this are replaced
        val: with this value

        returns: new Wave
        """
        ratio_spectrum = self.copy()
        ratio_spectrum.hs /= denom.hs
        ratio_spectrum.hs[denom.amps < thresh] = val
        return ratio_spectrum

    def invert(self):
        """Inverts this spectrum/filter.

        returns: new Wave
        """
        inverse = self.copy()
        inverse.hs = 1 / inverse.hs
        return inverse

    @property
    def freq_res(self):
        return self.framerate / 2 / (len(self.fs) - 1)

    def render_full(self, high=None):
        """Extracts amps and fs from a full spectrum.

        high: cutoff frequency

        returns: fs, amps
        """
        hs = np.fft.fftshift(self.hs)
        amps = np.abs(hs)
        fs = np.fft.fftshift(self.fs)
        i = 0 if high is None else find_index(-high, fs)
        j = None if high is None else find_index(high, fs) + 1
        return fs[i:j], amps[i:j]

    def plot(self, high=None, **options):
        """Plots amplitude vs frequency.

        Note: if this is a full spectrum, it ignores low and high

        high: frequency to cut off at
        """
        if self.full:
            fs, amps = self.render_full(high)
            thinkplot.plot(fs, amps, **options)
        else:
            i = None if high is None else find_index(high, self.fs)
            thinkplot.plot(self.fs[:i], self.amps[:i], **options)

    def plot_power(self, high=None, **options):
        """Plots power vs frequency.

        high: frequency to cut off at
        """
        if self.full:
            fs, amps = self.render_full(high)
            thinkplot.plot(fs, amps ** 2, **options)
        else:
            i = None if high is None else find_index(high, self.fs)
            thinkplot.plot(self.fs[:i], self.power[:i], **options)

    def estimate_slope(self):
        """Runs linear regression on log power vs log frequency.

        returns: slope, inter, r2, p, stderr
        """
        x = np.log(self.fs[1:])
        y = np.log(self.power[1:])
        t = scipy.stats.linregress(x, y)
        return t

    def peaks(self):
        """Finds the highest peaks and their frequencies.

        returns: sorted list of (amplitude, frequency) pairs
        """
        t = list(zip(self.amps, self.fs))
        t.sort(reverse=True)
        return t

