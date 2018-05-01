import unittest

from com.sbk.dsp import sbkdsp


class AudioFileTest(unittest.TestCase):
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

    @unittest.skip("Just for running from IDE")
    def test_write_to_file(self):
        self.sinus_wave.scale(5000)
        self.sinus_wave.make_audio()
        self.sinus_wave.scale(10)
        self.sinus_wave.make_audio()