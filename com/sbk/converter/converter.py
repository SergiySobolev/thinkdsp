import numpy as np

from com.sbk.spectrum.spectrum import Spectrum
from com.sbk.wave.wave import Wave


def spectrum_to_wave(spectrum):
    if spectrum.full:
        ys = np.fft.ifft(spectrum.hs)
    else:
        ys = np.fft.irfft(spectrum.hs)

        # NOTE: whatever the start time was, we lose it when
        # we transform back; we could fix that by saving start
        # time in the Spectrum
        # ts = self.start + np.arange(len(ys)) / self.framerate
    return Wave(ys, frame_rate=spectrum.framerate)


def wave_to_spectrum(wave, full=False):
    """Computes the spectrum using FFT.

           returns: Spectrum
           """
    n = len(wave.ys)
    d = 1 / wave.frame_rate

    if full:
        hs = np.fft.fft(wave.ys)
        fs = np.fft.fftfreq(n, d)
    else:
        hs = np.fft.rfft(wave.ys)
        fs = np.fft.rfftfreq(n, d)

    return Spectrum(hs, fs, wave.frame_rate, full)


def signal_to_wave(signal, duration=1, start=0, frame_rate=11025):
    """Makes a Wave object.

            duration: float seconds
            start: float seconds
            framerate: int frames per second

            returns: Wave
            """
    n = round(duration * frame_rate)
    ts = start + np.arange(n) / frame_rate
    ys = signal.evaluate(ts)
    return Wave(ys, ts, frame_rate=frame_rate)