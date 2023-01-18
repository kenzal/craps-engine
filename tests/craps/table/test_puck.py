import unittest
import craps.table.puck
import craps.table.config as TableConfig
import craps.table.config.odds as ConfigOdds


# noinspection DuplicateAssertionTestSmellUnittest
class TestConfig(unittest.TestCase):

    def test_default(self):
        puck = craps.table.puck.Puck(TableConfig.Config())
        self.assertTrue(puck.is_off())
        self.assertFalse(puck.is_on())
        self.assertIsNone(puck.for_json())
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.remove()
        puck.place(4)
        self.assertEqual(puck.for_json(), 4)
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.place(5)
        puck.remove()
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.place(2)
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.place(0)
        puck.set_from_json('10')
        self.assertTrue(puck.is_on())
        self.assertEqual(10, puck.location())

    def test_crapless(self):
        puck = craps.table.puck.Puck(TableConfig.Config(is_crapless=True, odds=ConfigOdds.CraplessOdds.flat(5)))

        self.assertTrue(puck.is_off())
        self.assertFalse(puck.is_on())
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.remove()
        puck.place(4)
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.place(5)
        puck.remove()
        puck.place(2)
        self.assertEqual(2, puck.location())
        puck.remove()
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.place(0)


if __name__ == '__main__':
    unittest.main()
