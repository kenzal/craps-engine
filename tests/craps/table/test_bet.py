import unittest
import craps.table as table
import craps.table.config as TableConfig


class TestBet(unittest.TestCase):
    puck: table.puck.Puck
    table_config: TableConfig
    wager: int

    def setUp(self) -> None:
        self.table_config = table.config.Config()
        self.puck = table.puck.Puck(self.table_config)
        self.wager = 50

    def test_pass_line(self):
        bet = table.bet.PassLine(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

    def test_put(self):
        bet = table.bet.Put(self.wager, puck=self.puck, table_config=self.table_config, location=4)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

    def test_come(self):
        bet = table.bet.Come(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

    def test_dont_pass(self):
        bet = table.bet.DontPass(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

    def test_dont_come(self):
        bet = table.bet.DontCome(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

    def test_field(self):
        bet = table.bet.Field(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertTrue(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

    def test_place(self):
        bet = table.bet.Place(self.wager, puck=self.puck, location=4, table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertTrue(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

    def test_buy(self):
        bet = table.bet.Buy(self.wager, puck=self.puck, location=4, table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertTrue(bet.can_toggle)
        self.assertTrue(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

    def test_lay(self):
        bet = table.bet.Lay(self.wager, puck=self.puck, location=6, table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertTrue(bet.can_toggle)
        self.assertTrue(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)


if __name__ == '__main__':
    unittest.main()
