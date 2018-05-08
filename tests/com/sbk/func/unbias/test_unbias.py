import unittest

import numpy as np

import numpy.testing as npt

from com.sbk.func.unbias.unbias import unbias


class TestUnbias(unittest.TestCase):

    def test_unbias(self):
        npt.assert_array_equal(unbias(np.array([1,2,3])), [-1, 0, 1], err_msg="Unbiased [1,2,3] have to be equal to [-1,0,1]")
