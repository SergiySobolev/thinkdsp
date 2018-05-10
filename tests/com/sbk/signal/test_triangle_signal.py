import unittest

from com.sbk.converter.converter import signal_to_wave
from com.sbk.signal.triangle_signal import TriangleSignal


class TestTriangleSignal(unittest.TestCase):

    def setUp(self):
        self.test_freq = 200
        self.test_duration = 0.05
        self.test_frame_rate = 10000
        self.triangle_signal = TriangleSignal(freq=self.test_freq)
        self.wave = signal_to_wave(signal=self.triangle_signal, duration=self.test_duration, frame_rate=self.test_frame_rate)

    def test_triangle_signal_frequency_equal_to_200(self):
        self.assertEqual(self.triangle_signal.freq, 200, "Frequency has to be equal to 200")

    def test_triangle_signal_amp_equal_to_1(self):
        self.assertEqual(self.triangle_signal.amp, 1, "Amplitude has to be equal to 1")

    def test_triangle_signal_period_equal_to_1(self):
        self.assertEqual(self.triangle_signal.period, 0.005, "Period has to be 1/200")

    def test_triangle_signal_wave_len_have_to_be_equal_to_11025(self):
        self.assertEqual(len(self.wave), 500, "Wave length has to be equal to 11025")

    def test_triangle_signal_wave_elements(self):
        self.assertEqual(self.wave.ys[0], 1, "Wave has to start from 1")
        self.assertAlmostEqual(self.wave.ys[1], 0.9199999999)
        self.assertAlmostEqual(self.wave.ys[2], 0.84)
        self.assertAlmostEqual(self.wave.ys[12], 0.04, msg="Wave has to cross OX at 12 element")
        self.assertAlmostEqual(self.wave.ys[13], -0.04, msg="Wave has to cross OX at 13 element")
        self.assertEqual(self.wave.ys[25], -1, "Wave's element #25 has to be equal to -1")