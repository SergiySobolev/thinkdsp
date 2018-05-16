import unittest

import numpy.testing as npt

from com.sbk.func.convolve.convolve import flipped_sub_signal


class TestFlippedSubSignal(unittest.TestCase):

    def test_sub_signal_index_less_than_length_1(self):
        signal = [1, 2, 3, 4, 5]
        npt.assert_array_equal(flipped_sub_signal(signal, 3, 5), [4, 3, 2, 1, 0])

    def test_sub_signal_index_less_than_length_2(self):
        signal = [1, 2, 3, 4, 5, 6, 7 ]
        npt.assert_array_equal(flipped_sub_signal(signal, 2, 6), [3, 2, 1, 0, 0, 0])

    def test_sub_signal_index_less_than_length_3(self):
        signal = [1, 2, 3, 4, 5, 6, 7]
        npt.assert_array_equal(flipped_sub_signal(signal, 0, 4), [1, 0, 0, 0])

    def test_sub_signal_index_with_length_longer_than_signal_1(self):
        signal = [1, 2, 3, 4, 5, 6, 7]
        npt.assert_array_equal(flipped_sub_signal(signal, 5, 6), [6, 5, 4, 3, 2, 1])

    def test_sub_signal_index_with_length_longer_than_signal_2(self):
        signal = [1, 2, 3, 4, 5, 6, 7]
        npt.assert_array_equal(flipped_sub_signal(signal, 6, 3), [7, 6, 5])

    def test_sub_signal_common_case(self):
        signal = [1, 2, 3, 4, 5, 6, 7]
        npt.assert_array_equal(flipped_sub_signal(signal, 4, 3), [5, 4, 3])
