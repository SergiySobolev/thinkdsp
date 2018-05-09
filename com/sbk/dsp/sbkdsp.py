from __future__ import print_function, division

import subprocess
import warnings
from wave import open as open_wave

import numpy as np

from com.sbk.converter.converter import signal_to_wave
from com.sbk.signal.silent_signal import SilentSignal
from com.sbk.wave.wave import Wave

try:
    from IPython.display import Audio
except:
    warnings.warn("Can't import Audio from IPython.display; "
                  "Wave.make_audio() will not work.")




def rest(duration):
    """Makes a rest of the given duration.

    duration: float seconds

    returns: Wave
    """
    signal = SilentSignal()
    wave = signal_to_wave(signal, duration)
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




def play_wave(filename='sound.wav', player='aplay'):
    """Plays a wave file.

    filename: string
    player: string name of executable that plays wav files
    """
    cmd = '%s %s' % (player, filename)
    popen = subprocess.Popen(cmd, shell=True)
    popen.communicate()


