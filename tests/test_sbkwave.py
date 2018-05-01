import unittest

from com.sbk.dsp import sbkdsp
from com.sbk.wave.sbkwave import SbkWave


class SbkWaveTest(unittest.TestCase):

    def setUp(self):
        test_sinus_freq = 880
        test_sinus_amp = 1
        test_sinus_offset = 0
        test_frame_rate = 24000
        test_duration = 3
        self.base_sinus_wave = sbkdsp.sin_signal(freq=test_sinus_freq,
                                            amp=test_sinus_amp,
                                            offset=test_sinus_offset) \
            .make_wave(duration=test_duration,
                       frame_rate=test_frame_rate)
        self.sinus_wave = SbkWave(wave=self.base_sinus_wave)
        self.stretched_wave = self.sinus_wave.stretch(2)

    def test_len_have_to_be_equal_72000(self):
        l = len(self.sinus_wave)
        self.assertEqual(l, 72000, "Len of SbkWave have to be equal to 72000")

    def test_ts_duration_have_to_be_6_000_after_stretch_with_factor_2(self):
        self.assertAlmostEqual(self.stretched_wave.ts_duration, 5.9999, 4, "Duration of stretched with stretch_factor=2 have to be close to 5.999")

    def test_should_double_ts_when_stretch_with_factor_2(self):
        self.assertEqual(len(self.stretched_wave), 72000, "Length sinus wave have to equal 72 000")
