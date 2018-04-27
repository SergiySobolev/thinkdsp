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
        self.assertAlmostEqual(ts_last, 2.999958333, 5, "Last time stamp element have to be almost 3")

    def test_start_ts_have_to_be_0(self):
        self.assertEqual(self.sinus_wave.start, 0, "First time stamp element have to be 0")

    def test_end_ts_have_to_be_3(self):
        self.assertAlmostEqual(self.sinus_wave.end, 2.999958333, 5, "Last time stamp element have to be almost 3")

    def test_duration_have_to_be_3(self):
        self.assertEqual(self.sinus_wave.duration, 3,  "Duration have to be almost 3")

    def test_shifted_by_1_wave_start_ts_have_to_be_1(self):
        shifted_wave = self.sinus_wave.copy()
        shifted_wave.shift(1)
        self.assertEqual(shifted_wave.start, 1, "First time stamp element have to be 1")

    def test_shifted_by_1_wave_end_ts_have_to_be_4(self):
        shifted_wave = self.sinus_wave.copy()
        shifted_wave.shift(1)
        self.assertAlmostEqual(shifted_wave.end, 3.9999583333333333, 7,  "End time stamp element have to be 4")

    def test_ys_first_values(self):
        ys_0 = self.sinus_wave.ys[0]
        self.assertAlmostEqual(ys_0, 0, 7, "First wave element have to be zero")
        ys_1 = self.sinus_wave.ys[1]
        self.assertAlmostEqual(ys_1, 0.228350870, 7, "Second wave element have to be about 0.22835")
        ys_2 = self.sinus_wave.ys[2]
        self.assertAlmostEqual(ys_2, 0.444635179, 7, "Third wave element have to be about 0.444635179")

    def test_scaled_by_3_ys_first_values(self):
        scaled_wave = self.sinus_wave.copy()
        scaled_wave.scale(3)
        ys_0 = scaled_wave.ys[0]
        self.assertAlmostEqual(ys_0, 0, 7, "First wave element have to be zero")
        ys_1 = scaled_wave.ys[1]
        self.assertAlmostEqual(ys_1, 0.685052610331, 7, "Second wave element have to be about 0.22835")
        ys_2 = scaled_wave.ys[2]
        self.assertAlmostEqual(ys_2, 1.33390553755, 7, "Third wave element have to be about 0.444635179")

