import unittest

import numpy as np
import numpy.testing as npt

from com.sbk.func.convolve.convolve import convolve


class TestConvolutionProperties(unittest.TestCase):

    def setUp(self):
        self.signal_1 = [1.0, 2.0, 3.0]
        self.signal_2 = [4.0, 5.0, 6.0]
        self.signal_3 = [7.0, 8.0, 9.0]

    def test_commutativity(self):
        npt.assert_array_equal(convolve(self.signal_1, self.signal_2), convolve(self.signal_1, self.signal_2))

    def test_associativity(self):
        npt.assert_array_equal(convolve(self.signal_1,
                                        convolve(self.signal_2, self.signal_3)),
                               convolve(convolve(self.signal_1, self.signal_2), self.signal_3))

    def test_distributivity(self):
        npt.assert_array_equal(np.add(convolve(self.signal_1, self.signal_2), convolve(self.signal_1, self.signal_3)),
                               convolve(self.signal_1, np.add(self.signal_2, self.signal_3)))