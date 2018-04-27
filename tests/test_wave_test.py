import unittest

from com.sbk.dsp.sbkdsp import Wave


class EmptyWaveTest(unittest.TestCase):
    def setUp(self):
        ys = []
        self.empty_wave = Wave(ys)

    def test_len_of_empty_wave_have_to_be_zero(self):
        l = len(self.empty_wave)
        self.assertEqual(l, 0, "Length of empty wave have to be 0")

