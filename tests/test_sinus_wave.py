import unittest

from com.sbk.dsp import sbkdsp


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

    def test_time_array_len_have_to_be_72000(self):
        l = len(self.sinus_wave.ts)
        self.assertEqual(l, 72000, "Sinus wave time stamp array len have to equal 72 000")

    def test_time_array_first_values(self):
        ts0 = self.sinus_wave.ts[0]
        self.assertEqual(ts0, 0, "First time stamp element have to be 0")
        ts_1 = self.sinus_wave.ts[1]
        self.assertAlmostEqual(ts_1, 0.000041667, 5, "Second time stamp element have to be 1/24000")
        ts_2 = self.sinus_wave.ts[2]
        self.assertAlmostEqual(ts_2, 0.000083333, 5, "Third time stamp element have to be 2/24000")
        ts_last = self.sinus_wave.ts[71999]
        self.assertAlmostEqual(ts_last, 2.999958333, 5, "Last time stamp element have to be 2/24000")


if __name__ == '__main__':
    unittest.main()
