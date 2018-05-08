import copy
import math
import warnings
import scipy

import numpy as np
from IPython.lib.display import Audio

import thinkplot
from com.sbk.func.apodize.apodize import apodize
from com.sbk.func.findindex.find_index import find_index
from com.sbk.func.normalize.normalize import normalize
from com.sbk.func.playwave.play_wave import play_wave
from com.sbk.func.quantize.quantize import quantize
from com.sbk.func.truncate.truncate import truncate
from com.sbk.func.unbias.unbias import unbias
from com.sbk.func.zeropad.zero_pad import zero_pad
from com.sbk.spectrum.spectrum import Spectrum
from com.sbk.spectrum.spectrum_parent import _SpectrumParent
from com.sbk.wave.iwave import IWave
from wave import open as open_wave


class Wave(IWave):
    """Represents a discrete-time waveform.

    """

    def __init__(self, ys, ts=None, frame_rate=None):
        """Initializes the wave.

        ys: wave array
        ts: array of times
        frame_rate: samples per second
        """
        super().__init__(ys, ts, frame_rate)
        self.ys = np.asanyarray(ys)
        self.frame_rate = frame_rate if frame_rate is not None else 11025

        if ts is None:
            self.ts = np.arange(len(ys)) / self.frame_rate
        else:
            self.ts = np.asanyarray(ts)

    def copy(self):
        """Makes a copy.

        Returns: new Wave
        """
        return copy.deepcopy(self)

    def __len__(self):
        return len(self.ys)

    @property
    def start(self):
        return self.ts[0]

    @property
    def end(self):
        return self.ts[-1]

    @property
    def duration(self):
        """Duration (property).

        returns: float duration in seconds
        """
        return len(self.ys) / self.frame_rate

    def __add__(self, other):
        """Adds two waves elementwise.

        other: Wave

        returns: new Wave
        """
        if other == 0:
            return self

        assert self.frame_rate == other.framerate

        # make an array of times that covers both waves
        start = min(self.start, other.start)
        end = max(self.end, other.end)
        n = int(round((end - start) * self.frame_rate)) + 1
        ys = np.zeros(n)
        ts = start + np.arange(n) / self.frame_rate

        def add_ys(wave):
            i = find_index(wave.start, ts)

            # make sure the arrays line up reasonably well
            diff = ts[i] - wave.start
            dt = 1 / wave.framerate
            if (diff / dt) > 0.1:
                warnings.warn("Can't add these waveforms; their "
                              "time arrays don't line up.")

            j = i + len(wave)
            ys[i:j] += wave.ys

        add_ys(self)
        add_ys(other)

        return Wave(ys, ts, self.frame_rate)

    __radd__ = __add__

    def __or__(self, other):
        """Concatenates two waves.

        other: Wave

        returns: new Wave
        """
        if self.frame_rate != other.framerate:
            raise ValueError('Wave.__or__: framerates do not agree')

        ys = np.concatenate((self.ys, other.ys))
        # ts = np.arange(len(ys)) / self.framerate
        return Wave(ys, frame_rate=self.frame_rate)

    def __mul__(self, other):
        """Multiplies two waves elementwise.

        Note: this operation ignores the timestamps; the result
        has the timestamps of self.

        other: Wave

        returns: new Wave
        """
        # the spectrums have to have the same framerate and duration
        assert self.frame_rate == other.framerate
        assert len(self) == len(other)

        ys = self.ys * other.ys
        return Wave(ys, self.ts, self.frame_rate)

    def max_diff(self, other):
        """Computes the maximum absolute difference between waves.

        other: Wave

        returns: float
        """
        assert self.frame_rate == other.framerate
        assert len(self) == len(other)

        ys = self.ys - other.ys
        return np.max(np.abs(ys))

    def convolve(self, other):
        """Convolves two waves.

        Note: this operation ignores the timestamps; the result
        has the timestamps of self.

        other: Wave or NumPy array

        returns: Wave
        """
        if isinstance(other, Wave):
            assert self.frame_rate == other.frame_rate
            window = other.ys
        else:
            window = other

        ys = np.convolve(self.ys, window, mode='full')
        # ts = np.arange(len(ys)) / self.framerate
        return Wave(ys, frame_rate=self.frame_rate)

    def diff(self):
        """Computes the difference between successive elements.

        returns: new Wave
        """
        ys = np.diff(self.ys)
        ts = self.ts[1:].copy()
        return Wave(ys, ts, self.frame_rate)

    def cumsum(self):
        """Computes the cumulative sum of the elements.

        returns: new Wave
        """
        ys = np.cumsum(self.ys)
        ts = self.ts.copy()
        return Wave(ys, ts, self.frame_rate)

    def quantize(self, bound, dtype):
        """Maps the waveform to quanta.

        bound: maximum amplitude
        dtype: numpy data type or string

        returns: quantized signal
        """
        return quantize(self.ys, bound, dtype)

    def apodize(self, denom=20, duration=0.1):
        """Tapers the amplitude at the beginning and end of the signal.

        Tapers either the given duration of time or the given
        fraction of the total duration, whichever is less.

        denom: float fraction of the segment to taper
        duration: float duration of the taper in seconds
        """
        self.ys = apodize(self.ys, self.frame_rate, denom, duration)

    def hamming(self):
        """Apply a Hamming window to the wave.
        """
        self.ys *= np.hamming(len(self.ys))

    def window(self, window):
        """Apply a window to the wave.

        window: sequence of multipliers, same length as self.ys
        """
        self.ys *= window

    def scale(self, factor):
        """Multplies the wave by a factor.

        factor: scale factor
        """
        self.ys *= factor

    def shift(self, shift):
        """Shifts the wave left or right in time.

        shift: float time shift
        """
        # TODO: track down other uses of this function and check them
        self.ts += shift

    def roll(self, roll):
        """Rolls this wave by the given number of locations.
        """
        self.ys = np.roll(self.ys, roll)

    def truncate(self, n):
        """Trims this wave to the given length.

        n: integer index
        """
        self.ys = truncate(self.ys, n)
        self.ts = truncate(self.ts, n)

    def zero_pad(self, n):
        """Trims this wave to the given length.

        n: integer index
        """
        self.ys = zero_pad(self.ys, n)
        self.ts = self.start + np.arange(n) / self.frame_rate

    def normalize(self, amp=1.0):
        """Normalizes the signal to the given amplitude.

        amp: float amplitude
        """
        self.ys = normalize(self.ys, amp=amp)

    def unbias(self):
        """Unbiases the signal.
        """
        self.ys = unbias(self.ys)

    def find_index(self, t):
        """Find the index corresponding to a given time."""
        n = len(self)
        start = self.start
        end = self.end
        i = round((n - 1) * (t - start) / (end - start))
        return int(i)

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
        return Wave(ys, ts, self.frame_rate)

    def make_spectrum(self, full=False):
        """Computes the spectrum using FFT.

        returns: Spectrum
        """
        n = len(self.ys)
        d = 1 / self.frame_rate

        if full:
            hs = np.fft.fft(self.ys)
            fs = np.fft.fftfreq(n, d)
        else:
            hs = np.fft.rfft(self.ys)
            fs = np.fft.rfftfreq(n, d)

        return Spectrum(hs, fs, self.frame_rate, full)

    def make_dct(self):
        """Computes the DCT of this wave.
        """
        N = len(self.ys)
        hs = scipy.fftpack.dct(self.ys, type=2)
        fs = (0.5 + np.arange(N)) / 2
        return Dct(hs, fs, self.frame_rate)

    def make_spectrogram(self, seg_length, win_flag=True):
        """Computes the spectrogram of the wave.

        seg_length: number of samples in each segment
        win_flag: boolean, whether to apply hamming window to each segment

        returns: Spectrogram
        """
        if win_flag:
            window = np.hamming(seg_length)
        i, j = 0, seg_length
        step = seg_length // 2

        # map from time to Spectrum
        spec_map = {}

        while j < len(self.ys):
            segment = self.slice(i, j)
            if win_flag:
                segment.window(window)

            # the nominal time for this segment is the midpoint
            t = (segment.start + segment.end) / 2
            spec_map[t] = segment.make_spectrum()

            i += step
            j += step

        return Spectrogram(spec_map, seg_length)

    def get_xfactor(self, options):
        try:
            xfactor = options['xfactor']
            options.pop('xfactor')
        except KeyError:
            xfactor = 1
        return xfactor

    def plot(self, **options):
        """Plots the wave.

        """
        xfactor = self.get_xfactor(options)
        thinkplot.plot(self.ts * xfactor, self.ys, **options)

    def plot_vlines(self, **options):
        """Plots the wave with vertical lines for samples.

        """
        xfactor = self.get_xfactor(options)
        thinkplot.vlines(self.ts * xfactor, 0, self.ys, **options)

    def corr(self, other):
        """Correlation coefficient two waves.

        other: Wave

        returns: float coefficient of correlation
        """
        corr = np.corrcoef(self.ys, other.ys)[0, 1]
        return corr

    def cov_mat(self, other):
        """Covariance matrix of two waves.

        other: Wave

        returns: 2x2 covariance matrix
        """
        return np.cov(self.ys, other.ys)

    def cov(self, other):
        """Covariance of two unbiased waves.

        other: Wave

        returns: float
        """
        total = sum(self.ys * other.ys) / len(self.ys)
        return total

    def cos_cov(self, k):
        """Covariance with a cosine signal.

        freq: freq of the cosine signal in Hz

        returns: float covariance
        """
        n = len(self.ys)
        factor = math.pi * k / n
        ys = [math.cos(factor * (i + 0.5)) for i in range(n)]
        total = 2 * sum(self.ys * ys)
        return total

    def cos_transform(self):
        """Discrete cosine transform.

        returns: list of frequency, cov pairs
        """
        n = len(self.ys)
        res = []
        for k in range(n):
            cov = self.cos_cov(k)
            res.append((k, cov))

        return res

    def write(self, filename='sound.wav'):
        """Write a wave file.

        filename: string
        """
        print('Writing', filename)
        wfile = WavFileWriter(filename, self.frame_rate)
        wfile.write(self)
        wfile.close()

    def play(self, filename='sound.wav'):
        """Plays a wave file.

        filename: string
        """
        self.write(filename)
        play_wave(filename)

    def make_audio(self):
        """Makes an IPython Audio object.
        """
        audio = Audio(data=self.ys.real, rate=self.frame_rate)
        return audio


class WavFileWriter:
    """Writes wav files."""

    def __init__(self, filename='sound.wav', framerate=11025):
        """Opens the file and sets parameters.

        filename: string
        framerate: samples per second
        """
        self.filename = filename
        self.framerate = framerate
        self.nchannels = 1
        self.sampwidth = 2
        self.bits = self.sampwidth * 8
        self.bound = 2 ** (self.bits - 1) - 1

        self.fmt = 'h'
        self.dtype = np.int16

        self.fp = open_wave(self.filename, 'w')
        self.fp.setnchannels(self.nchannels)
        self.fp.setsampwidth(self.sampwidth)
        self.fp.setframerate(self.framerate)

    def write(self, wave):
        """Writes a wave.

        wave: Wave
        """
        zs = wave.quantize(self.bound, self.dtype)
        self.fp.writeframes(zs.tostring())

    def close(self, duration=0):
        """Closes the file.

        duration: how many seconds of silence to append
        """
        if duration:
            self.write(rest(duration))

        self.fp.close()


class Dct(_SpectrumParent):
    """Represents the spectrum of a signal using discrete cosine transform."""

    @property
    def amps(self):
        """Returns a sequence of amplitudes (read-only property).

        Note: for DCTs, amps are positive or negative real.
        """
        return self.hs

    def __add__(self, other):
        """Adds two DCTs elementwise.

        other: DCT

        returns: new DCT
        """
        if other == 0:
            return self

        assert self.framerate == other.framerate
        hs = self.hs + other.hs
        return Dct(hs, self.fs, self.framerate)

    __radd__ = __add__

    def make_wave(self):
        """Transforms to the time domain.

        returns: Wave
        """
        N = len(self.hs)
        ys = scipy.fftpack.idct(self.hs, type=2) / 2 / N
        # NOTE: whatever the start time was, we lose it when
        # we transform back
        # ts = self.start + np.arange(len(ys)) / self.framerate
        return Wave(ys, frame_rate=self.frame_rate)


class Spectrogram:
    """Represents the spectrum of a signal."""

    def __init__(self, spec_map, seg_length):
        """Initialize the spectrogram.

        spec_map: map from float time to Spectrum
        seg_length: number of samples in each segment
        """
        self.spec_map = spec_map
        self.seg_length = seg_length

    def any_spectrum(self):
        """Returns an arbitrary spectrum from the spectrogram."""
        index = next(iter(self.spec_map))
        return self.spec_map[index]

    @property
    def time_res(self):
        """Time resolution in seconds."""
        spectrum = self.any_spectrum()
        return float(self.seg_length) / spectrum.framerate

    @property
    def freq_res(self):
        """Frequency resolution in Hz."""
        return self.any_spectrum().freq_res

    def times(self):
        """Sorted sequence of times.

        returns: sequence of float times in seconds
        """
        ts = sorted(iter(self.spec_map))
        return ts

    def frequencies(self):
        """Sequence of frequencies.

        returns: sequence of float freqencies in Hz.
        """
        fs = self.any_spectrum().fs
        return fs

    def plot(self, high=None, **options):
        """Make a pseudocolor plot.

        high: highest frequency component to plot
        """
        fs = self.frequencies()
        i = None if high is None else find_index(high, fs)
        fs = fs[:i]
        ts = self.times()

        # make the array
        size = len(fs), len(ts)
        array = np.zeros(size, dtype=np.float)

        # copy amplitude from each spectrum into a column of the array
        for j, t in enumerate(ts):
            spectrum = self.spec_map[t]
            array[:, j] = spectrum.amps[:i]

        thinkplot.pcolor(ts, fs, array, **options)

    def make_wave(self):
        """Inverts the spectrogram and returns a Wave.

        returns: Wave
        """
        res = []
        for t, spectrum in sorted(self.spec_map.items()):
            wave = spectrum.make_wave()
            n = len(wave)

            window = 1 / np.hamming(n)
            wave.window(window)

            i = wave.find_index(t)
            start = i - n // 2
            end = start + n
            res.append((start, end, wave))

        starts, ends, waves = zip(*res)
        low = min(starts)
        high = max(ends)

        ys = np.zeros(high - low, np.float)
        for start, end, wave in res:
            ys[start:end] = wave.ys

        # ts = np.arange(len(ys)) / self.framerate
        return Wave(ys, frame_rate=wave.frame_rate)


def rest(duration):
    """Makes a rest of the given duration.

    duration: float seconds

    returns: Wave
    """
    # signal = SilentSignal()
    # wave = signal.make_wave(duration)
    # return wave
    pass