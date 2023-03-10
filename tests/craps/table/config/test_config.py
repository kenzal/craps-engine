import json
import unittest
import craps.table.config as TableConfig
import craps.table.config.odds as ConfigOdds


# noinspection DuplicateAssertionTestSmellUnittest
class TestConfig(unittest.TestCase):

    def test_default(self):
        config = TableConfig.Config()
        self.assertFalse(config.allow_buy_59)
        self.assertFalse(config.allow_put)
        self.assertIsNone(config.bet_max)
        self.assertEqual(config.bet_min, 5)
        self.assertEqual(config.dont_bar, 12)
        self.assertEqual(config.field_12_pay, 3)
        self.assertEqual(config.field_2_pay, 2)
        self.assertIsNone(config.hard_way_max)
        self.assertEqual(config.hop_easy_pay_to_one, 15)
        self.assertEqual(config.hop_hard_pay_to_one, 30)
        self.assertIsNone(config.hop_max)
        self.assertFalse(config.is_crapless)
        self.assertIsNone(config.min_buy_lay)
        self.assertEqual(config.odds, ConfigOdds.StandardOdds.mirrored345())
        self.assertIsNone(config.odds_max)
        self.assertFalse(config.pay_vig_before_buy)
        self.assertFalse(config.pay_vig_before_lay)

    def test_crapless(self):
        self.assertEqual(TableConfig.Config(is_crapless=True, odds=ConfigOdds.CraplessOdds.flat(5)).odds[3], 5)
        with self.assertRaises(TableConfig.InconsistentConfig):
            TableConfig.Config(is_crapless=True)
        with self.assertRaises(TableConfig.InconsistentConfig):
            TableConfig.Config(is_crapless=True, odds=ConfigOdds.StandardOdds.flat(5))

    def test_bad_bar(self):
        with self.assertRaises(TableConfig.InconsistentConfig):
            TableConfig.Config(dont_bar=6)

    def test_negative_bet_min(self):
        with self.assertRaises(TableConfig.InconsistentConfig):
            TableConfig.Config(bet_min=-5)

    def test_bet_min(self):
        self.assertEqual(TableConfig.Config(bet_min=10).bet_min, 10)
        with self.assertRaises(TableConfig.InconsistentConfig):
            TableConfig.Config(bet_min=6)

    def test_bet_max(self):
        self.assertEqual(TableConfig.Config(bet_max=10).bet_max, 10)
        with self.assertRaises(TableConfig.InconsistentConfig):
            TableConfig.Config(bet_min=10, bet_max=5)
        with self.assertRaises(TableConfig.InconsistentConfig):
            TableConfig.Config(bet_max=12)

    def test_from_json_string(self):
        json_str = '{"is_crapless":true,"place_2_12_odds":[25,5],"place_3_11_odds":[13,5],"odds":"flat(2)"}'
        json_obj = json.loads(json_str)
        self.assertEqual(TableConfig.Config.from_json(json_str), TableConfig.Config.from_json(json_obj))
        bad_odds_1 = {'odds': 'not_a_method'}
        with self.assertRaises(TableConfig.InconsistentConfig):
            TableConfig.Config.from_json(bad_odds_1)
        bad_odds_2 = {'odds': 'bad_method()'}
        with self.assertRaises(TableConfig.InconsistentConfig):
            TableConfig.Config.from_json(bad_odds_2)
        explicit_odds = {'odds': {4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 6}}
        TableConfig.Config.from_json(explicit_odds)


if __name__ == '__main__':
    unittest.main()
