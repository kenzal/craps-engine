import unittest
from engine import *


class TestEngine(unittest.TestCase):
    def test_something(self):
        eng = Engine(**req)  # add assertion here
        self.assertTrue(eng.table.puck.is_on())


if __name__ == '__main__':
    unittest.main()
