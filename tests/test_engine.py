import json
import unittest

from JsonEncoder import ComplexEncoder
from craps.table import Bet, Come, Config, Puck
from engine import Engine
from craps.table.bet import get_bet_from_list
from craps.dice import Outcome as DiceOutcome


class TestEngine(unittest.TestCase):

    def test_get_bet_from_empty_list(self):
        self.assertIsNone(get_bet_from_list(bet_list=[], bet_type='Come', bet_placement=None))

    def test_get_bet_from_list_of_similar(self):
        config = Config
        puck = Puck(table_config=config)
        bet_list = [
            Bet.from_signature({"type": "Come", "wager": 10, "placement": 4}, puck=puck),
            Bet.from_signature({"type": "Come", "wager": 10, "placement": None}, puck=puck),
        ]
        self.assertIsInstance(bet_list[0], Come)
        self.assertIsInstance(bet_list[1], Come)
        self.assertIsInstance(get_bet_from_list(bet_list=bet_list, bet_type='Come', bet_placement=4), Come)
        self.assertIsInstance(get_bet_from_list(bet_list=bet_list, bet_type='Come', bet_placement=None), Come)
        self.assertIsInstance(get_bet_from_list(bet_list=bet_list, bet_type=Come, bet_placement=4), Come)
        self.assertIsInstance(get_bet_from_list(bet_list=bet_list, bet_type=Come, bet_placement=None), Come)

    def test_pass_line_set(self):
        req = {"instructions": {"place": [{"type": "PassLine", "wager": 10}]}, "dice": [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(4, result['new_table']['puck_location'])
        self.assertEqual(4, result['new_table']['existing_bets'][0].placement)

    def test_pass_line_winner(self):
        req = {"table": {"existing_bets": [{"type": "PassLine", "wager": 10, "placement": 4}], "puck_location": 4},
               "dice":  [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertIsNone(result['new_table']['puck_location'])
        self.assertIsNone(result['new_table']['existing_bets'][0].placement)

    def test_come_set(self):
        req = {"table":        {"puck_location": 4},
               "instructions": {"place": [{"type": "Come", "wager": 10}]},
               "dice":         [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertIsNone(result['new_table']['puck_location'])
        self.assertEqual(4, result['new_table']['existing_bets'][0].placement)

    def test_come_down_and_up(self):
        req = {"table":        {"existing_bets": [{"type": "Come", "wager": 10, "placement": 4}], "puck_location": 6},
               "instructions": {"place": [{"type": "Come", "wager": 10}]},
               "dice":         [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(len(result['new_table']['existing_bets']), 2)
        self.assertIsNotNone(get_bet_from_list(bet_list=result['new_table']['existing_bets'], bet_type='Come', bet_placement=4))
        self.assertIsNotNone(get_bet_from_list(bet_list=result['new_table']['existing_bets'], bet_type='Come', bet_placement=None))

    def test_come_down_and_up_different_wagers(self):
        req = {"table":        {"existing_bets": [{"type": "Come", "wager": 5, "placement": 4}], "puck_location": 6},
               "instructions": {"place": [{"type": "Come", "wager": 10}]},
               "dice":         [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(1, len(result['new_table']['existing_bets']))
        self.assertEqual(1, len(result['returned']))
        self.assertEqual(4, result['new_table']['existing_bets'][0].placement)
        self.assertEqual(10, result['new_table']['existing_bets'][0].wager)
        self.assertEqual(5, result['returned'][0].wager)

    def test_unaffected_dont_remains(self):
        req = {"table": {"existing_bets": [{"type": "DontCome", "wager": 5, "placement": 8}], "puck_location": 6},
               "dice":  [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(1, len(result['new_table']['existing_bets']))
        self.assertEqual(0, len(result['returned']))
        self.assertEqual(8, result['new_table']['existing_bets'][0].placement)
        self.assertEqual(5, result['new_table']['existing_bets'][0].wager)

    def test_dont_pass_set(self):
        req = {"instructions": {"place": [{"type": "DontPass", "wager": 10}]}, "dice": [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(4, result['new_table']['puck_location'])
        self.assertEqual(4, result['new_table']['existing_bets'][0].placement)

    def test_winning_dont_pass_returned(self):
        req = {"table": {"existing_bets": [{"type": "DontCome", "wager": 5, "placement": 8}],
                         "puck_location": 6},
               "dice":  [3, 4]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(3, 4))
        self.assertIsNone(result['new_table']['puck_location'])
        self.assertEqual(1, len(result['returned']))
        self.assertEqual(8, result['returned'][0].placement)

    def test_circuit(self):
        req = {"instructions": {"place": [{"type": "PassLine", "wager": 10}]}, "dice": [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(4, result['new_table']['puck_location'])
        self.assertEqual(4, result['new_table']['existing_bets'][0].placement)
        req = {"table":        json.loads(json.dumps(result['new_table'], cls=ComplexEncoder)),
               "instructions": {"set_odds": [{"type": "PassLine", "wager": 10, "placement": 4, "odds": 20}]},
               "dice":         [2, 2]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(2, 2))
        self.assertIsNone(result['new_table']['puck_location'])
        self.assertIsNone(result['new_table']['existing_bets'][0].placement)
        self.assertEqual(result['summary']['total_winnings_to_player'], 50)


if __name__ == '__main__':
    unittest.main()
