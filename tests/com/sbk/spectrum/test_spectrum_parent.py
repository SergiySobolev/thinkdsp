import unittest

from com.sbk.converter.converter import signal_to_wave, wave_to_spectrum
from com.sbk.signal.triangle.triangle_signal import TriangleSignal


class TestSpectrumParent(unittest.TestCase):

    def setUp(self):
        self.test_freq = 200
        self.triangle_signal = TriangleSignal(self.test_freq)
        self.triangle_wave = signal_to_wave(self.triangle_signal)
        self.triangle_spectrum = wave_to_spectrum(self.triangle_wave)

    def test_spectrum_parent_plot(self):
        self.triangle_spectrum.plot(high=2000)
