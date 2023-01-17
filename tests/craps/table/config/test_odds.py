import unittest
import json
import craps.table.config.odds as ConfigOdds


class TestOdds(unittest.TestCase):

    def test_mirrored(self):
        odds = ConfigOdds.StandardOdds.mirrored345()
        with self.assertRaises(KeyError):
            odds.__getitem__(0)
        with self.assertRaises(KeyError):
            odds.__getitem__(1)
        with self.assertRaises(KeyError):
            odds.__getitem__(2)
        self.assertEqual(odds[4], 3)
        self.assertEqual(odds[5], 4)
        self.assertEqual(odds[6], 5)
        with self.assertRaises(KeyError):
            odds.__getitem__(7)
        self.assertEqual(odds[8], 5)
        self.assertEqual(odds[9], 4)
        self.assertEqual(odds[10], 3)
        with self.assertRaises(KeyError):
            odds.__getitem__(11)
        with self.assertRaises(KeyError):
            odds.__getitem__(12)
        with self.assertRaises(KeyError):
            odds.__getitem__(13)

    def test_flat(self):
        for i in [2, 3, 5, 10, 100]:
            with self.subTest(i=i):
                odds = ConfigOdds.StandardOdds.flat(i)
                with self.assertRaises(KeyError):
                    odds.__getitem__(0)
                with self.assertRaises(KeyError):
                    odds.__getitem__(1)
                with self.assertRaises(KeyError):
                    odds.__getitem__(2)
                self.assertEqual(odds[4], i)
                self.assertEqual(odds[5], i)
                self.assertEqual(odds[6], i)
                with self.assertRaises(KeyError):
                    odds.__getitem__(7)
                self.assertEqual(odds[8], i)
                self.assertEqual(odds[9], i)
                self.assertEqual(odds[10], i)
                with self.assertRaises(KeyError):
                    odds.__getitem__(11)
                with self.assertRaises(KeyError):
                    odds.__getitem__(12)
                with self.assertRaises(KeyError):
                    odds.__getitem__(13)

    def test_flat_crapless(self):
        for i in [2, 3, 5]:
            with self.subTest(i=i):
                odds = ConfigOdds.CraplessOdds.flat(i)
                with self.assertRaises(KeyError):
                    odds.__getitem__(0)
                with self.assertRaises(KeyError):
                    odds.__getitem__(1)
                self.assertEqual(odds[2], i)
                self.assertEqual(odds[3], i)
                self.assertEqual(odds[4], i)
                self.assertEqual(odds[5], i)
                self.assertEqual(odds[6], i)
                with self.assertRaises(KeyError):
                    odds.__getitem__(7)
                self.assertEqual(odds[8], i)
                self.assertEqual(odds[9], i)
                self.assertEqual(odds[10], i)
                self.assertEqual(odds[11], i)
                self.assertEqual(odds[12], i)
                with self.assertRaises(KeyError):
                    odds.__getitem__(13)


if __name__ == '__main__':
    unittest.main()
