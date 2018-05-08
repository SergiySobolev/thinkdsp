from __future__ import print_function, division

import subprocess
import warnings
from wave import open as open_wave

import numpy as np

from com.sbk.dsp.constants import PI2
from com.sbk.func.unbias.unbias import unbias
from com.sbk.wave.wave import Wave
from com.sbk.wave.wave_factory import WaveFactory

try:
    from IPython.display import Audio
except:
    warnings.warn("Can't import Audio from IPython.display; "
                  "Wave.make_audio() will not work.")


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

    def plot(self, frame_rate=11025, periods=3):
        """Plots the signal.

        The default behavior is to plot three periods.

        framerate: samples per second
        """
        duration = self.period * periods
        wave = self.make_wave(duration, start=0, frame_rate=frame_rate)
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
        return Wave(ys, ts, frame_rate=frame_rate)


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


class SilentSignal(Signal):
    """Represents silence."""

    def evaluate(self, ts):
        """Evaluates the signal at the given times.

        ts: float array of times

        returns: float wave array
        """
        return np.zeros(len(ts))

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




def rest(duration):
    """Makes a rest of the given duration.

    duration: float seconds

    returns: Wave
    """
    signal = SilentSignal()
    wave = signal.make_wave(duration)
    return wave




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
