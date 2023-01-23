import json
import unittest

from JsonEncoder import ComplexEncoder
from craps.table.bet import BetAbstract, Come
from craps.table.config import Config
from craps.table.puck import Puck
from craps.table.table import Table
from engine import Engine, process_request
from craps.bet import get_bet_from_set
from craps.dice import Outcome as DiceOutcome


# noinspection DuplicatedCode
class TestEngine(unittest.TestCase):

    def test_get_bet_from_empty_list(self):
        self.assertIsNone(get_bet_from_set(bet_set=[], bet_type='Come', bet_placement=None))

    def test_get_bet_from_list_of_similar(self):
        config = Config()
        puck = Puck(table_config=config)
        table = Table(config=config, puck_location=puck.location())
        bet_list = [
            BetAbstract.from_signature({"type": "Come", "wager": 10, "placement": 4}, table=table),
            BetAbstract.from_signature({"type": "Come", "wager": 10, "placement": None}, table=table),
        ]
        self.assertIsInstance(bet_list[0], Come)
        self.assertIsInstance(bet_list[1], Come)
        self.assertIsInstance(get_bet_from_set(bet_set=bet_list, bet_type='Come', bet_placement=4), Come)
        self.assertIsInstance(get_bet_from_set(bet_set=bet_list, bet_type='Come', bet_placement=None), Come)
        self.assertIsInstance(get_bet_from_set(bet_set=bet_list, bet_type=Come, bet_placement=4), Come)
        self.assertIsInstance(get_bet_from_set(bet_set=bet_list, bet_type=Come, bet_placement=None), Come)

    def test_pass_line_set(self):
        req = {"instructions": {"place": [{"type": "PassLine", "wager": 10}]}, "dice": [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(4, result['new_table']['puck_location'])
        self.assertEqual(1, len(result['new_table']['existing_bets']))
        existing_bet = result['new_table']['existing_bets'].copy().pop()
        self.assertEqual(4, existing_bet.placement)

    def test_pass_line_winner(self):
        req = {"table": {"existing_bets": [{"type": "PassLine", "wager": 10, "placement": 4}], "puck_location": 4},
               "dice":  [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertIsNone(result['new_table']['puck_location'])
        self.assertEqual(1, len(result['new_table']['existing_bets']))
        existing_bet = result['new_table']['existing_bets'].copy().pop()
        self.assertIsNone(existing_bet.placement)

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
        self.assertEqual(1, len(result['new_table']['existing_bets']))
        existing_bet = result['new_table']['existing_bets'].copy().pop()
        self.assertEqual(4, existing_bet.placement)

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
        self.assertIsNotNone(get_bet_from_set(bet_set=result['new_table']['existing_bets'], bet_type='Come', bet_placement=4))
        self.assertIsNotNone(get_bet_from_set(bet_set=result['new_table']['existing_bets'], bet_type='Come', bet_placement=None))

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
        existing_bet = result['new_table']['existing_bets'].copy().pop()
        returned_bet = result['returned'].copy().pop()
        self.assertEqual(4, existing_bet.placement)
        self.assertEqual(10, existing_bet.wager)
        self.assertEqual(5, returned_bet.wager)

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
        existing_bet = result['new_table']['existing_bets'].copy().pop()
        self.assertEqual(8, existing_bet.placement)
        self.assertEqual(5, existing_bet.wager)

    def test_dont_pass_set(self):
        req = {"instructions": {"place": [{"type": "DontPass", "wager": 10}]}, "dice": [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(4, result['new_table']['puck_location'])
        self.assertEqual(1, len(result['new_table']['existing_bets']))
        existing_bet = result['new_table']['existing_bets'].copy().pop()
        self.assertEqual(4, existing_bet.placement)

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
        self.assertEqual(8, result['returned'].copy().pop().placement)

    def test_non_traveling_bet_remains(self):
        req = {"table": {"existing_bets": [{"type": "Place", "wager": 6, "placement": 8}],
                         "puck_location": 6},
               "dice":  [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(1, len(result['new_table']['existing_bets']))
        self.assertEqual(0, len(result['returned']))
        existing_bet = result['new_table']['existing_bets'].copy().pop()
        self.assertEqual(8, existing_bet.placement)
        self.assertEqual(6, existing_bet.wager)

    def test_vig_notification(self):
        req = {"table": {"existing_bets": [{"type": "Buy", "wager": 100, "placement": 10}],
                         "puck_location": 6},
               "dice":  [5, 5]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(5, 5))
        self.assertEqual(1, len(result['new_table']['existing_bets']))
        self.assertEqual(0, len(result['returned']))
        existing_bet = result['new_table']['existing_bets'].copy().pop()
        self.assertEqual(10, existing_bet.placement)
        self.assertEqual(100, existing_bet.wager)
        self.assertEqual(5, result['winners'].copy().pop().vig_paid)
        self.assertEqual(195, result['summary']['total_winnings_to_player'])

    def test_circuit(self):
        req = {"instructions": {"place": [{"type": "PassLine", "wager": 10}]}, "dice": [1, 3]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(1, 3))
        self.assertEqual(4, result['new_table']['puck_location'])
        self.assertEqual(4, result['new_table']['existing_bets'].copy().pop().placement)
        req = {"table":        json.loads(json.dumps(result['new_table'], cls=ComplexEncoder)),
               "instructions": {"set_odds": [{"type": "PassLine", "wager": 10, "placement": 4, "odds": 20}]},
               "dice":         [2, 2]}
        eng = Engine(**req)
        eng.process_instructions()
        result = eng.get_result()
        self.assertNotIn('Exception', result)
        self.assertEqual(result['summary']['dice_outcome'], DiceOutcome(2, 2))
        self.assertIsNone(result['new_table']['puck_location'])
        self.assertIsNone(result['new_table']['existing_bets'].copy().pop().placement)
        self.assertEqual(result['summary']['total_winnings_to_player'], 50)

    def test_hash_returns_same_roll(self):
        req_1 = {}  # Default everything - no hash provided
        eng_1 = Engine(**req_1)
        eng_1.roll_dice()
        result_1 = eng_1.get_result()
        hash = result_1['hash']
        dice_1 = result_1['summary']['dice_outcome']
        req_2 = {'hash': hash}
        eng_2 = Engine(**req_2)
        eng_2.roll_dice()
        result_2 = eng_2.get_result()
        dice_2 = result_2['summary']['dice_outcome']
        self.assertEqual(dice_1, dice_2)
        self.assertEqual(json.dumps(result_1, cls=ComplexEncoder),
                         json.dumps(result_2, cls=ComplexEncoder))

    def test_outlier_hash(self):
        req = {'hash': 'f'*64}
        eng = Engine(**req)
        self.assertIsNone(eng.dice_roll)
        eng.roll_dice()
        self.assertIsNotNone(eng.dice_roll)

    def test_good_process_request(self):
        req = {'hash': 'f'*64}
        result = process_request(req)
        self.assertEqual(result['hash'], 'f'*64)

    def test_bad_process_request(self):
        req = {'hash': 'n'*64}
        result = process_request(req)
        self.assertIn('success', result)
        self.assertEqual(result['success'], False)



if __name__ == '__main__':
    unittest.main()
