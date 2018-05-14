import unittest

import numpy.testing as npt
import numpy as np

from com.sbk.func.convolve.convolve import convolve


class TestConvolve(unittest.TestCase):

    def setUp(self):
        self.x = range(0, 1000)
        self.sin = np.sin(self.x)
        self.lg = np.log(self.x)
        self.signal = self.sin + self.lg

    def test_convolve(self):
        signal = [0, -1, -1.2, 2, 1.4, 1.4, 0.8, 0, -0.8]
        impulse_response = [1, 0.5, 0.2, 0]
        res = convolve(signal, impulse_response)
        expected_res = [0.0, -1.0, -1.7,  1.2,  2.16,  2.5,   1.78,  0.68, -0.64, -0.4, -0.16,  0.0]
        numpy_res = np.convolve(signal, impulse_response)
        npt.assert_array_equal(res, numpy_res)
        npt.assert_array_almost_equal(res, expected_res)