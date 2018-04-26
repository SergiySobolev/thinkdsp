from abc import ABC, abstractmethod


class IWave(ABC):

    def __init__(self, ys, ts=None, framerate=None):
        """Initializes the wave.

        ys: wave array
        ts: array of times
        framerate: samples per second
        """

    @abstractmethod
    def max_diff(self, other):
        """Computes the maximum absolute difference between waves.

         other: Wave

         returns: float
         """
        pass;

    @abstractmethod
    def convolve(self, other):
        """Convolves two waves.

        Note: this operation ignores the timestamps; the result
        has the timestamps of self.

        other: Wave or NumPy array

        returns: Wave
        """
        pass

    @abstractmethod
    def diff(self):
        """Computes the difference between successive elements.

        returns: new Wave
        """
        pass

    @abstractmethod
    def cumsum(self):
        """Computes the cumulative sum of the elements.

        returns: new Wave
        """
        pass

    @abstractmethod
    def quantize(self, bound, dtype):
        """Maps the waveform to quanta.

        bound: maximum amplitude
        dtype: numpy data type or string

        returns: quantized signal
        """
        pass

    @abstractmethod
    def apodize(self, denom=20, duration=0.1):
        """Tapers the amplitude at the beginning and end of the signal.

        Tapers either the given duration of time or the given
        fraction of the total duration, whichever is less.

        denom: float fraction of the segment to taper
        duration: float duration of the taper in seconds
        """
        pass

    @abstractmethod
    def hamming(self):
        """Apply a Hamming window to the wave.
        """
        pass

    @abstractmethod
    def window(self, window):
        """Apply a window to the wave.

        window: sequence of multipliers, same length as self.ys
        """
        pass

    @abstractmethod
    def scale(self, factor):
        """Multplies the wave by a factor.

        factor: scale factor
        """
        pass

    @abstractmethod
    def shift(self, shift):
        """Shifts the wave left or right in time.

        shift: float time shift
        """

        pass

    @abstractmethod
    def roll(self, roll):
        """Rolls this wave by the given number of locations.
        """
        pass

    @abstractmethod
    def truncate(self, n):
        """Trims this wave to the given length.

        n: integer index
        """
        pass

    @abstractmethod
    def zero_pad(self, n):
        """Trims this wave to the given length.

        n: integer index
        """
        pass

    @abstractmethod
    def normalize(self, amp=1.0):
        """Normalizes the signal to the given amplitude.

        amp: float amplitude
        """
        pass

    @abstractmethod
    def unbias(self):
        """Unbiases the signal.
        """
        pass

    @abstractmethod
    def find_index(self, t):
        """Find the index corresponding to a given time."""
        pass

    @abstractmethod
    def segment(self, start=None, duration=None):
        """Extracts a segment.

        start: float start time in seconds
        duration: float duration in seconds

        returns: Wave
        """
        pass

    @abstractmethod
    def slice(self, i, j):
        """Makes a slice from a Wave.

        i: first slice index
        j: second slice index
        """
        pass

    @abstractmethod
    def make_spectrum(self, full=False):
        """Computes the spectrum using FFT.

        returns: Spectrum
        """
        pass

    @abstractmethod
    def make_dct(self):
        """Computes the DCT of this wave.
        """
        pass

    @abstractmethod
    def make_spectrogram(self, seg_length, win_flag=True):
        """Computes the spectrogram of the wave.

        seg_length: number of samples in each segment
        win_flag: boolean, whether to apply hamming window to each segment

        returns: Spectrogram
        """
        pass

    @abstractmethod
    def get_xfactor(self, options):
        pass

    @abstractmethod
    def plot(self, **options):
        """Plots the wave.

        """
        pass

    @abstractmethod
    def plot_vlines(self, **options):
        """Plots the wave with vertical lines for samples.

        """
        pass

    @abstractmethod
    def corr(self, other):
        """Correlation coefficient two waves.

        other: Wave

        returns: float coefficient of correlation
        """
        pass

    @abstractmethod
    def cov_mat(self, other):
        """Covariance matrix of two waves.

        other: Wave

        returns: 2x2 covariance matrix
        """
        pass

    @abstractmethod
    def cov(self, other):
        """Covariance of two unbiased waves.

        other: Wave

        returns: float
        """
        pass

    @abstractmethod
    def cos_cov(self, k):
        """Covariance with a cosine signal.

        freq: freq of the cosine signal in Hz

        returns: float covariance
        """
        pass

    @abstractmethod
    def cos_transform(self):
        """Discrete cosine transform.

        returns: list of frequency, cov pairs
        """
        pass

    @abstractmethod
    def write(self, filename='sound.wav'):
        """Write a wave file.

        filename: string
        """
        pass

    @abstractmethod
    def play(self, filename='sound.wav'):
        """Plays a wave file.

        filename: string
        """
        pass

    @abstractmethod
    def make_audio(self):
        """Makes an IPython Audio object.
        """
        pass
