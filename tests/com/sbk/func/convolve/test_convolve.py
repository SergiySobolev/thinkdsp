import unittest

import numpy.testing as npt

from com.sbk.func.convolve.convolve import convolve


class TestConvolve(unittest.TestCase):

    def test_convolve(self):
        signal = [0, -1, -1.2, 2, 1.4, 1.4, 0.8, 0, -0.8]
        impulse_response = [1, 0.5, 0.2, 0]
        res = convolve(signal, impulse_response)
        npt.assert_array_equal(res, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        # npt.assert_array_equal(unbias(np.array([1,2,3])),
        #                        [-1, 0, 1],
        #                        err_msg="Unbiased [1,2,3] have to be equal to [-1,0,1]")