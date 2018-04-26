import unittest

import sbkdsp


class SinusWaveTest(unittest.TestCase):
    def setUp(self):
        test_sinus_freq = 880
        test_sinus_amp = 1
        test_sinus_offset = 0
        test_frame_rate = 24000
        test_duration = 3
        self.sinus_wave = sbkdsp.sin_signal(freq=test_sinus_freq,
                                            amp=test_sinus_amp,
                                            offset=test_sinus_offset) \
            .make_wave(duration=test_duration,
                       frame_rate=test_frame_rate)

    def test_len_of_sin_wave_have_to_be_72000(self):
        l = len(self.sinus_wave)
        self.assertEqual(l, 72000, "Length sinus wave have to equal 72 000")
