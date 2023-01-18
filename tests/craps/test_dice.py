import unittest
import craps.dice as dice


class DiceTest(unittest.TestCase):
    def test_dice_creation(self):
        outcome = dice.Outcome(1, 3)
        reverse = dice.Outcome(3, 1)
        self.assertEqual(outcome, dice.Outcome(1, 3))
        self.assertEqual(outcome, reverse)
        self.assertFalse(outcome.is_hard())
        self.assertEqual(outcome.total(), 4)
        with self.assertRaises(ValueError):  # Can not move twice
            dice.Outcome(1, 7)
        self.assertNotEqual(outcome, [1, 3])
        self.assertEqual(outcome.for_json(), [1, 3])
        self.assertEqual(hash(outcome), hash(reverse))
        self.assertIn(outcome, dice.Outcome.get_all())
        self.assertIn(outcome, dice.Outcome.get_all_unique())


if __name__ == '__main__':
    unittest.main()
