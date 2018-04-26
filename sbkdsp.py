from __future__ import print_function, division

import math
import subprocess
import warnings
from wave import open as open_wave

import numpy as np
import scipy
import scipy.fftpack
import scipy.stats

import thinkplot
from com.sbk.wave.IWave import IWave
from com.sbk.wave.IWaveFactory import IWaveFactory

try:
    from IPython.display import Audio
except:
    warnings.warn("Can't import Audio from IPython.display; "
                  "Wave.make_audio() will not work.")

PI2 = math.pi * 2


class Signal:
    """Represents a time-varying signal."""

    def __init__(self):
        self.wave_factory = WaveFactory()

    def __add__(self, other):
        """Adds two signals.

        other: Signal

        returns: Signal
        """
        if other == 0:
            return self
        return SumSignal(self, other)

    __radd__ = __add__

    @property
    def period(self):
        """Period of the signal in seconds (property).

        Since this is used primarily for purposes of plotting,
        the default behavior is to return a value, 0.1 seconds,
        that is reasonable for many signals.

        returns: float seconds
        """
        return 0.1

    def plot(self, framerate=11025, periods=3):
        """Plots the signal.

        The default behavior is to plot three periods.

        framerate: samples per second
        """
        duration = self.period * periods
        wave = self.make_wave(duration, start=0, frame_rate=framerate)
        wave.plot()

    def make_wave(self, duration=1, start=0, frame_rate=11025):
        """Makes a Wave object.

        duration: float seconds
        start: float seconds
        framerate: int frames per second

        returns: Wave
        """
        n = round(duration * frame_rate)
        ts = start + np.arange(n) / frame_rate
        ys = self.evaluate(ts)
        return self.wave_factory.create_wave(ys, ts, frame_rate=frame_rate)


class SumSignal(Signal):
    """Represents the sum of signals."""

    def __init__(self, *args):
        """Initializes the sum.

        args: tuple of signals
        """
        super().__init__()
        self.signals = args

    @property
    def period(self):
        """Period of the signal in seconds.

        Note: this is not correct; it's mostly a placekeeper.

        But it is correct for a harmonic sequence where all
        component frequencies are multiples of the fundamental.

        returns: float seconds
        """
        return max(sig.period for sig in self.signals)

    def evaluate(self, ts):
        """Evaluates the signal at the given times.

        ts: float array of times

        returns: float wave array
        """
        ts = np.asarray(ts)
        return sum(sig.evaluate(ts) for sig in self.signals)


class Sinusoid(Signal):
    """Represents a sinusoidal signal."""

    def __init__(self, freq=440, amp=1.0, offset=0, func=np.sin):
        """Initializes a sinusoidal signal.

        freq: float frequency in Hz
        amp: float amplitude, 1.0 is nominal max
        offset: float phase offset in radians
        func: function that maps phase to amplitude
        """
        super().__init__()
        self.freq = freq
        self.amp = amp
        self.offset = offset
        self.func = func

    @property
    def period(self):
        """Period of the signal in seconds.

        returns: float seconds
        """
        return 1.0 / self.freq

    def evaluate(self, ts):
        """Evaluates the signal at the given times.

        ts: float array of times

        returns: float wave array
        """
        ts = np.asarray(ts)
        phases = PI2 * self.freq * ts + self.offset
        ys = self.amp * self.func(phases)
        return ys


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


class Spectrum(_SpectrumParent):
    """Represents the spectrum of a signal."""

    def __len__(self):
        """Length of the spectrum."""
        return len(self.hs)

    def __add__(self, other):
        """Adds two spectrums elementwise.

        other: Spectrum

        returns: new Spectrum
        """
        if other == 0:
            return self.copy()

        assert all(self.fs == other.fs)
        hs = self.hs + other.hs
        return Spectrum(hs, self.fs, self.framerate, self.full)

    __radd__ = __add__

    def __mul__(self, other):
        """Multiplies two spectrums elementwise.

        other: Spectrum

        returns: new Spectrum
        """
        assert all(self.fs == other.fs)
        hs = self.hs * other.hs
        return Spectrum(hs, self.fs, self.framerate, self.full)

    def convolve(self, other):
        """Convolves two Spectrums.

        other: Spectrum

        returns: Spectrum
        """
        assert all(self.fs == other.fs)
        if self.full:
            hs1 = np.fft.fftshift(self.hs)
            hs2 = np.fft.fftshift(other.hs)
            hs = np.convolve(hs1, hs2, mode='same')
            hs = np.fft.ifftshift(hs)
        else:
            # not sure this branch would mean very much
            hs = np.convolve(self.hs, other.hs, mode='same')

        return Spectrum(hs, self.fs, self.framerate, self.full)

    @property
    def real(self):
        """Returns the real part of the hs (read-only property)."""
        return np.real(self.hs)

    @property
    def imag(self):
        """Returns the imaginary part of the hs (read-only property)."""
        return np.imag(self.hs)

    @property
    def angles(self):
        """Returns a sequence of angles (read-only property)."""
        return np.angle(self.hs)

    def scale(self, factor):
        """Multiplies all elements by the given factor.

        factor: what to multiply the magnitude by (could be complex)
        """
        self.hs *= factor

    def low_pass(self, cutoff, factor=0):
        """Attenuate frequencies above the cutoff.

        cutoff: frequency in Hz
        factor: what to multiply the magnitude by
        """
        self.hs[abs(self.fs) > cutoff] *= factor

    def high_pass(self, cutoff, factor=0):
        """Attenuate frequencies below the cutoff.

        cutoff: frequency in Hz
        factor: what to multiply the magnitude by
        """
        self.hs[abs(self.fs) < cutoff] *= factor

    def band_stop(self, low_cutoff, high_cutoff, factor=0):
        """Attenuate frequencies between the cutoffs.

        low_cutoff: frequency in Hz
        high_cutoff: frequency in Hz
        factor: what to multiply the magnitude by
        """
        # TODO: test this function
        fs = abs(self.fs)
        indices = (low_cutoff < fs) & (fs < high_cutoff)
        self.hs[indices] *= factor

    def pink_filter(self, beta=1):
        """Apply a filter that would make white noise pink.

        beta: exponent of the pink noise
        """
        denom = self.fs ** (beta / 2.0)
        denom[0] = 1
        self.hs /= denom

    def differentiate(self):
        """Apply the differentiation filter.

        returns: new Spectrum
        """
        new = self.copy()
        new.hs *= PI2 * 1j * new.fs
        return new

    def integrate(self):
        """Apply the integration filter.

        returns: new Spectrum
        """
        new = self.copy()
        new.hs /= PI2 * 1j * new.fs
        return new

    def make_integrated_spectrum(self):
        """Makes an integrated spectrum.
        """
        cs = np.cumsum(self.power)
        cs /= cs[-1]
        return IntegratedSpectrum(cs, self.fs)

    def make_wave(self):
        """Transforms to the time domain.

        returns: Wave
        """
        if self.full:
            ys = np.fft.ifft(self.hs)
        else:
            ys = np.fft.irfft(self.hs)

        # NOTE: whatever the start time was, we lose it when
        # we transform back; we could fix that by saving start
        # time in the Spectrum
        # ts = self.start + np.arange(len(ys)) / self.framerate
        return Wave(ys, frame_rate=self.framerate)


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
        return Wave(ys, framerate=self.framerate)


class WaveFactory(IWaveFactory):

    def create_wave(self, ys, ts=None, frame_rate=None):
        return Wave(ys, ts, frame_rate)

    def create_wave_sbk(self, ys, ts=None, frame_rate=None):
        return Wave(ys, ts, frame_rate)


WAVE_FACTORY = WaveFactory()


class Wave(IWave):
    """Represents a discrete-time waveform.

    """

    def __init__(self, ys, ts=None, frame_rate=None):
        """Initializes the wave.

        ys: wave array
        ts: array of times
        framerate: samples per second
        """
        super().__init__(ys, ts, frame_rate)
        self.ys = np.asanyarray(ys)
        self.framerate = frame_rate if frame_rate is not None else 11025
        self.wave_factory = WaveFactory()

        if ts is None:
            self.ts = np.arange(len(ys)) / self.framerate
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
        return len(self.ys) / self.framerate

    def __add__(self, other):
        """Adds two waves elementwise.

        other: Wave

        returns: new Wave
        """
        if other == 0:
            return self

        assert self.framerate == other.framerate

        # make an array of times that covers both waves
        start = min(self.start, other.start)
        end = max(self.end, other.end)
        n = int(round((end - start) * self.framerate)) + 1
        ys = np.zeros(n)
        ts = start + np.arange(n) / self.framerate

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

        return self.wave_factory.create_wave(ys, ts, self.framerate)

    __radd__ = __add__

    def __or__(self, other):
        """Concatenates two waves.

        other: Wave

        returns: new Wave
        """
        if self.framerate != other.framerate:
            raise ValueError('Wave.__or__: framerates do not agree')

        ys = np.concatenate((self.ys, other.ys))
        # ts = np.arange(len(ys)) / self.framerate
        return self.wave_factory.create_wave(ys, frame_rate=self.framerate)

    def __mul__(self, other):
        """Multiplies two waves elementwise.

        Note: this operation ignores the timestamps; the result
        has the timestamps of self.

        other: Wave

        returns: new Wave
        """
        # the spectrums have to have the same framerate and duration
        assert self.framerate == other.framerate
        assert len(self) == len(other)

        ys = self.ys * other.ys
        return self.wave_factory.create_wave(ys, self.ts, self.framerate)

    def max_diff(self, other):
        """Computes the maximum absolute difference between waves.

        other: Wave

        returns: float
        """
        assert self.framerate == other.framerate
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
            assert self.framerate == other.framerate
            window = other.ys
        else:
            window = other

        ys = np.convolve(self.ys, window, mode='full')
        # ts = np.arange(len(ys)) / self.framerate
        return self.wave_factory.create_wave(ys, framerate=self.framerate)

    def diff(self):
        """Computes the difference between successive elements.

        returns: new Wave
        """
        ys = np.diff(self.ys)
        ts = self.ts[1:].copy()
        return self.wave_factory.create_wave(ys, ts, self.framerate)

    def cumsum(self):
        """Computes the cumulative sum of the elements.

        returns: new Wave
        """
        ys = np.cumsum(self.ys)
        ts = self.ts.copy()
        return self.wave_factory.create_wave(ys, ts, self.framerate)

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
        self.ys = apodize(self.ys, self.framerate, denom, duration)

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
        self.ts = self.start + np.arange(n) / self.framerate

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
        return self.wave_factory.create_wave(ys, ts, self.framerate)

    def make_spectrum(self, full=False):
        """Computes the spectrum using FFT.

        returns: Spectrum
        """
        n = len(self.ys)
        d = 1 / self.framerate

        if full:
            hs = np.fft.fft(self.ys)
            fs = np.fft.fftfreq(n, d)
        else:
            hs = np.fft.rfft(self.ys)
            fs = np.fft.rfftfreq(n, d)

        return Spectrum(hs, fs, self.framerate, full)

    def make_dct(self):
        """Computes the DCT of this wave.
        """
        N = len(self.ys)
        hs = scipy.fftpack.dct(self.ys, type=2)
        fs = (0.5 + np.arange(N)) / 2
        return Dct(hs, fs, self.framerate)

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
        wfile = WavFileWriter(filename, self.framerate)
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
        audio = Audio(data=self.ys.real, rate=self.framerate)
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


def cos_signal(freq=440, amp=1.0, offset=0):
    """Makes a cosine Sinusoid.

    freq: float frequency in Hz
    amp: float amplitude, 1.0 is nominal max
    offset: float phase offset in radians

    returns: Sinusoid object
    """
    return Sinusoid(freq, amp, offset, func=np.cos)


def sin_signal(freq=440, amp=1.0, offset=0):
    """Makes a sine Sinusoid.

    freq: float frequency in Hz
    amp: float amplitude, 1.0 is nominal max
    offset: float phase offset in radians

    returns: Sinusoid object
    """
    return Sinusoid(freq, amp, offset, func=np.sin)


def sinc(freq=440, amp=1.0, offset=0):
    """Makes a Sinc function.

    freq: float frequency in Hz
    amp: float amplitude, 1.0 is nominal max
    offset: float phase offset in radians

    returns: Sinusoid object
    """
    return Sinusoid(freq, amp, offset, func=np.sinc)


class SilentSignal(Signal):
    """Represents silence."""

    def evaluate(self, ts):
        """Evaluates the signal at the given times.

        ts: float array of times

        returns: float wave array
        """
        return np.zeros(len(ts))


def quantize(ys, bound, dtype):
    """Maps the waveform to quanta.

    ys: wave array
    bound: maximum amplitude
    dtype: numpy data type of the result

    returns: quantized signal
    """
    if max(ys) > 1 or min(ys) < -1:
        warnings.warn('Warning: normalizing before quantizing.')
        ys = normalize(ys)

    zs = (ys * bound).astype(dtype)
    return zs


def normalize(ys, amp=1.0):
    """Normalizes a wave array so the maximum amplitude is +amp or -amp.

    ys: wave array
    amp: max amplitude (pos or neg) in result

    returns: wave array
    """
    high, low = abs(max(ys)), abs(min(ys))
    return amp * ys / max(high, low)


def rest(duration):
    """Makes a rest of the given duration.

    duration: float seconds

    returns: Wave
    """
    signal = SilentSignal()
    wave = signal.make_wave(duration)
    return wave


def apodize(ys, framerate, denom=20, duration=0.1):
    """Tapers the amplitude at the beginning and end of the signal.

    Tapers either the given duration of time or the given
    fraction of the total duration, whichever is less.

    ys: wave array
    framerate: int frames per second
    denom: float fraction of the segment to taper
    duration: float duration of the taper in seconds

    returns: wave array
    """
    # a fixed fraction of the segment
    n = len(ys)
    k1 = n // denom

    # a fixed duration of time
    k2 = int(duration * framerate)

    k = min(k1, k2)

    w1 = np.linspace(0, 1, k)
    w2 = np.ones(n - 2 * k)
    w3 = np.linspace(1, 0, k)

    window = np.concatenate((w1, w2, w3))
    return ys * window


def read_wave(filename='sound.wav'):
    """Reads a wave file.

    filename: string

    returns: Wave
    """
    fp = open_wave(filename, 'r')

    nchannels = fp.getnchannels()
    nframes = fp.getnframes()
    sampwidth = fp.getsampwidth()
    framerate = fp.getframerate()

    z_str = fp.readframes(nframes)

    fp.close()

    dtype_map = {1: np.int8, 2: np.int16, 3: 'special', 4: np.int32}
    if sampwidth not in dtype_map:
        raise ValueError('sampwidth %d unknown' % sampwidth)

    if sampwidth == 3:
        xs = np.fromstring(z_str, dtype=np.int8).astype(np.int32)
        ys = (xs[2::3] * 256 + xs[1::3]) * 256 + xs[0::3]
    else:
        ys = np.fromstring(z_str, dtype=dtype_map[sampwidth])

    # if it's in stereo, just pull out the first channel
    if nchannels == 2:
        ys = ys[::2]

    # ts = np.arange(len(ys)) / framerate
    wave = Wave(ys, frame_rate=framerate)
    wave.normalize()
    return wave


def truncate(self, n):
    """Trims this wave to the given length.

    n: integer index
    """
    self.ys = truncate(self.ys, n)
    self.ts = truncate(self.ts, n)


def unbias(self):
    """Unbiases the signal.
    """
    self.ys = unbias(self.ys)


def play_wave(filename='sound.wav', player='aplay'):
    """Plays a wave file.

    filename: string
    player: string name of executable that plays wav files
    """
    cmd = '%s %s' % (player, filename)
    popen = subprocess.Popen(cmd, shell=True)
    popen.communicate()


def find_index(self, t):
    """Find the index corresponding to a given time."""
    n = len(self)
    start = self.start
    end = self.end
    i = round((n - 1) * (t - start) / (end - start))
    return int(i)


def zero_pad(self, n):
    """Trims this wave to the given length.

    n: integer index
    """
    self.ys = zero_pad(self.ys, n)
    self.ts = self.start + np.arange(n) / self.framerate
