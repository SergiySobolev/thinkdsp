import unittest

from com.sbk.wave.amplify.amplify import do_amplification


class TestAmplification(unittest.TestCase):

    def test_len_of_sin_wave_have_to_be_72000(self):
        do_amplification("temp.wav", "scaled_temp.wav", 7)
