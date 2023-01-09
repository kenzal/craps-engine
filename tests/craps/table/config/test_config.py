import json
import unittest
from craps.table.config import Config, InconsistentConfig
from craps.table.config.odds import StandardOdds, CraplessOdds


class TestConfig(unittest.TestCase):

    def test_default(self):
        config = Config()
        self.assertEqual(config.allow_buy_59, False)
        self.assertEqual(config.allow_put, False)
        self.assertEqual(config.bet_max, None)
        self.assertEqual(config.bet_min, 5)
        self.assertEqual(config.dont_bar, 12)
        self.assertEqual(config.field_12_pay, 3)
        self.assertEqual(config.field_2_pay, 2)
        self.assertEqual(config.hard_way_max, None)
        self.assertEqual(config.hop_easy_pay_to_one, 15)
        self.assertEqual(config.hop_hard_pay_to_one, 30)
        self.assertEqual(config.hop_max, None)
        self.assertEqual(config.is_crapless, False)
        self.assertEqual(config.min_buy_lay, None)
        self.assertEqual(config.odds, StandardOdds.mirrored345())
        self.assertEqual(config.odds_max, None)
        self.assertEqual(config.pay_vig_before_buy, False)
        self.assertEqual(config.pay_vig_before_lay, False)

    def test_crapless(self):
        self.assertEqual(Config(is_crapless=True, odds=CraplessOdds.flat(5)).odds[3], 5)
        with self.assertRaises(InconsistentConfig):
            Config(is_crapless=True)
        with self.assertRaises(InconsistentConfig):
            Config(is_crapless=True, odds=StandardOdds.flat(5))

    def test_bad_bar(self):
        with self.assertRaises(InconsistentConfig):
            Config(dont_bar=6)

    def test_negative_bet_min(self):
        with self.assertRaises(InconsistentConfig):
            Config(bet_min=-5)

    def test_bet_min(self):
        self.assertEqual(Config(bet_min=10).bet_min, 10)
        with self.assertRaises(InconsistentConfig):
            Config(bet_min=6)

    def test_bet_max(self):
        self.assertEqual(Config(bet_max=10).bet_max, 10)
        with self.assertRaises(InconsistentConfig):
            Config(bet_min=10, bet_max=5)
        with self.assertRaises(InconsistentConfig):
            Config(bet_max=12)

    def test_as_json(self):
        self.assertEqual(json.loads(Config().as_json()), json.loads('{}'))
        self.assertEqual(json.loads(Config(odds_max=5000).as_json()), json.loads('{"odds_max":5000}'))
        self.assertEqual(json.loads(Config(odds=StandardOdds.flat(10)).as_json()), json.loads('{"odds":"flat(10)"}'))

        for i, o in enumerate([
            Config(odds_max=5000),
            Config(odds=StandardOdds.flat(10)),
            Config(is_crapless=True, odds=CraplessOdds.flat(5)),
            Config(odds=StandardOdds({4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 6})),
        ]):
            with self.subTest(i=i):
                self.assertEqual(o, Config.from_json(o.as_json()))


if __name__ == '__main__':
    unittest.main()
