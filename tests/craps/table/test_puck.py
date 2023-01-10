import json
import unittest
import craps.table.puck
import craps.table.config as TableConfig
import craps.table.config.odds as ConfigOdds


class TestConfig(unittest.TestCase):

    def test_default(self):
        puck = craps.table.puck.Puck(TableConfig.Config())
        self.assertTrue(puck.is_off())
        self.assertFalse(puck.is_on())
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.remove()
        puck.place(4)
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.place(5)
        puck.remove()
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.place(2)
        with self.assertRaises(craps.table.puck.IllegalMove):
            puck.place(0)

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

    def test_json(self):
        puck = craps.table.puck.Puck(TableConfig.Config())
        self.assertEqual(puck.location(), craps.table.puck.Puck(TableConfig.Config()).set_from_json(puck.as_json()).location())
        puck.place(4)
        self.assertEqual(puck, puck.set_from_json(puck.as_json()))


if __name__ == '__main__':
    unittest.main()
