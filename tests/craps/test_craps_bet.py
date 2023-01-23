import unittest

from craps.bet import BetStatus, BetSignature, get_bet_from_list, BetInterface
from craps.table.bet import PassLine, Place, Field


class TestCrapsBet(unittest.TestCase):
    def test_bet_status(self):
        self.assertEqual(BetStatus.ON.value, 'ON')
        self.assertEqual(BetStatus.OFF.value, 'OFF')
        self.assertNotEqual(BetStatus.ON, BetStatus.OFF)

    def test_bet_signature(self):
        sig = BetSignature(wager=10, type=PassLine, override_puck=BetStatus.ON)
        self.assertEqual(sig.get_type(), PassLine.__name__)
        expected_json_object = {"wager": 10, "type": "PassLine", "override_puck": "ON"}
        actual_json_object = sig.for_json()
        self.assertEqual(expected_json_object, actual_json_object)
        sig_2 = BetSignature(wager=5, type=PassLine)
        tuple_obj = ("red", "blue")
        self.assertTrue(sig.same_type_and_place(sig_2))
        self.assertFalse(sig.same_type_and_place(tuple_obj))

    def test_get_bet_from_list(self):
        bet_list = [BetSignature(wager=10, type=PassLine, override_puck=BetStatus.ON),
                    BetSignature(wager=10, type=Place, placement=4),
                    BetSignature(wager=10, type=Place, placement=6),
                    BetSignature(wager=10, type=Field),
                    BetSignature(wager=25, type=Field),  # Duplicate Field bet for testing only
                    ]
        self.assertIsInstance(get_bet_from_list(bet_list=bet_list, bet_type=PassLine), BetInterface)
        self.assertIsNone(get_bet_from_list(bet_list=bet_list, bet_type=Place, bet_placement=10))
        self.assertIsInstance(get_bet_from_list(bet_list=bet_list, bet_type=Field), list)


if __name__ == '__main__':
    unittest.main()
