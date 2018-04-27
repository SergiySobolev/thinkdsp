import unittest

from com.sbk.wave.amplify.amplify import do_amplification


class TestAmplification(unittest.TestCase):

    @unittest.skip("Just for running from IDE")
    def test_amplify(self):
        do_amplification("temp.wav", "scaled_temp.wav", 7)
