import unittest
from .. import util

class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_cm_to_inches(self):
        self.assertAlmostEqual(util.cm_to_inches(3), 1.181102, 5)
        self.assertAlmostEqual(util.cm_to_inches(-5), -1.96850, 5)
        self.assertAlmostEqual(util.cm_to_inches(2.54), 1.0, 5)

    def test_cm_to_inches_inverse(self):
        self.assertAlmostEqual(util.cm_to_inches(3.0, inverse=True), 7.62, 5)
        self.assertAlmostEqual(util.cm_to_inches(-5, inverse=True), -12.7, 5)

    def test_integerround(self):
        self.assertEqual(util.integerround(2.54), 5)
        self.assertEqual(util.integerround(0), 0)
        self.assertEqual(util.integerround(-11), -10)
        self.assertEqual(util.integerround(5.0, base=3),6)
