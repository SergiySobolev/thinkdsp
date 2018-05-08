import numpy as np

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