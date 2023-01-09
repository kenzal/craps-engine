import unittest
import json
from craps.table.config.odds import Odds, StandardOdds, CraplessOdds


class TestOdds(unittest.TestCase):

    def test_mirrored(self):
        odds = StandardOdds.mirrored345()
        with self.assertRaises(KeyError):
            odds[0]
        with self.assertRaises(KeyError):
            odds[1]
        with self.assertRaises(KeyError):
            odds[2]
        self.assertEqual(odds[4], 3)
        self.assertEqual(odds[5], 4)
        self.assertEqual(odds[6], 5)
        with self.assertRaises(KeyError):
            odds[7]
        self.assertEqual(odds[8], 5)
        self.assertEqual(odds[9], 4)
        self.assertEqual(odds[10], 3)
        with self.assertRaises(KeyError):
            odds[11]
        with self.assertRaises(KeyError):
            odds[12]
        with self.assertRaises(KeyError):
            odds[13]

    def test_flat(self):
        for i in [2, 3, 5, 10, 100]:
            with self.subTest(i=i):
                odds = StandardOdds.flat(i)
                with self.assertRaises(KeyError):
                    odds[0]
                with self.assertRaises(KeyError):
                    odds[1]
                with self.assertRaises(KeyError):
                    odds[2]
                self.assertEqual(odds[4], i)
                self.assertEqual(odds[5], i)
                self.assertEqual(odds[6], i)
                with self.assertRaises(KeyError):
                    odds[7]
                self.assertEqual(odds[8], i)
                self.assertEqual(odds[9], i)
                self.assertEqual(odds[10], i)
                with self.assertRaises(KeyError):
                    odds[11]
                with self.assertRaises(KeyError):
                    odds[12]
                with self.assertRaises(KeyError):
                    odds[13]

    def test_flat_crapless(self):
        for i in [2, 3, 5]:
            with self.subTest(i=i):
                odds = CraplessOdds.flat(i)
                with self.assertRaises(KeyError):
                    odds[0]
                with self.assertRaises(KeyError):
                    odds[1]
                self.assertEqual(odds[2], i)
                self.assertEqual(odds[3], i)
                self.assertEqual(odds[4], i)
                self.assertEqual(odds[5], i)
                self.assertEqual(odds[6], i)
                with self.assertRaises(KeyError):
                    odds[7]
                self.assertEqual(odds[8], i)
                self.assertEqual(odds[9], i)
                self.assertEqual(odds[10], i)
                self.assertEqual(odds[11], i)
                self.assertEqual(odds[12], i)
                with self.assertRaises(KeyError):
                    odds[13]

    def test_as_json(self):
        self.assertEqual(json.loads(StandardOdds.mirrored345().as_json()), json.loads('"mirrored345()"'))
        self.assertEqual(json.loads(StandardOdds.flat(5).as_json()), json.loads('"flat(5)"'))


if __name__ == '__main__':
    unittest.main()
