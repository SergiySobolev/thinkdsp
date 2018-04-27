import unittest

from com.sbk.dsp import sbkdsp
from com.sbk.wave.amplify.audiofile import AudioFile


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

    def test_write_to_file(self):
        self.sinus_wave.scale(5000)
        AudioFile.write_wave_to_out_file(self.sinus_wave)