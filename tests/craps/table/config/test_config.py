import unittest
from craps.table.config import Config, InconsistentConfig
from craps.table.config.odds import StandardOdds, CraplessOdds


class TestConfig(unittest.TestCase):

    def test_default(self):
        config = Config()
        self.assertEquals(config.allow_buy_59, False)
        self.assertEquals(config.allow_put, False)
        self.assertEquals(config.bet_max, None)
        self.assertEquals(config.bet_min, 5)
        self.assertEquals(config.dont_bar, 12)
        self.assertEquals(config.field_12_pay, 3)
        self.assertEquals(config.field_2_pay, 2)
        self.assertEquals(config.hard_way_max, None)
        self.assertEquals(config.hop_easy_pay_to_one, 15)
        self.assertEquals(config.hop_hard_pay_to_one, 30)
        self.assertEquals(config.hop_max, None)
        self.assertEquals(config.is_crapless, False)
        self.assertEquals(config.min_buy_lay, None)
        self.assertEquals(config.odds, StandardOdds.mirrored345())
        self.assertEquals(config.odds_max, None)
        self.assertEquals(config.pay_vig_before_buy, False)
        self.assertEquals(config.pay_vig_before_lay, False)

    def test_crapless(self):
        self.assertEqual(Config(is_crapless=True, odds=CraplessOdds.flat(5)).odds[3], 5)
        with self.assertRaises(InconsistentConfig):
            Config(is_crapless=True)
        with self.assertRaises(InconsistentConfig):
            Config(is_crapless=True, odds=StandardOdds.flat(5))

    def test_bad_bar(self):
        with self.assertRaises(InconsistentConfig):
            Config(dont_bar=6)

    def test_bet_min(self):
        self.assertEquals(Config(bet_min=10).bet_min, 10)
        with self.assertRaises(InconsistentConfig):
            Config(bet_min=6)

    def test_bet_max(self):
        self.assertEquals(Config(bet_max=10).bet_max, 10)
        with self.assertRaises(InconsistentConfig):
            Config(bet_min=10, bet_max=5)
        with self.assertRaises(InconsistentConfig):
            Config(bet_max=12)


if __name__ == '__main__':
    unittest.main()
