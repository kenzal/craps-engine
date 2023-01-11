import unittest
import craps.table as table
import craps.table.config as TableConfig
from craps.dice import Outcome


class TestBet(unittest.TestCase):
    puck: table.puck.Puck
    table_config: TableConfig
    wager: int

    def setUp(self) -> None:
        self.table_config = table.config.Config()
        self.puck = table.puck.Puck(self.table_config)
        self.wager = 50
        self.outcomes = {
            2:  Outcome(1, 1),  # Aces
            3:  Outcome(1, 2),  # Ace-Deuce, Shocker
            4:  Outcome(2, 2),  # Little Joe
            5:  Outcome(2, 3),  # Fiver
            6:  Outcome(3, 3),  #
            7:  Outcome(3, 4),  # Big Red
            8:  Outcome(4, 4),  #
            9:  Outcome(4, 5),  # Niner
            10: Outcome(5, 5),  # The Big one on the End
            11: Outcome(5, 6),  # Yo
            12: Outcome(6, 6),  # Midnight, Boxcars
        }

    def test_pass_line(self):
        bet = table.bet.PassLine(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)
        self.assertTrue(bet.is_winner(self.outcomes[7]), 'Wins on Seven')
        self.assertTrue(bet.is_winner(self.outcomes[11]), 'Wins on Yo')
        self.assertTrue(bet.is_loser(self.outcomes[2]), 'Loses on Aces')
        self.assertTrue(bet.is_loser(self.outcomes[3]), 'Loses on Three')
        self.assertTrue(bet.is_loser(self.outcomes[12]), 'Loses on Midnight')

        point_roll = self.outcomes[4]
        other_point = self.outcomes[6]
        self.assertFalse(bet.is_winner(point_roll), 'Does Not Win on point number')
        self.assertFalse(bet.is_loser(point_roll), 'Does Not Lose on point number')

        bet.move(point_roll.total())
        with self.assertRaises(table.bet.InvalidBet):  # Can not move twice
            bet.move(other_point.total())

        self.assertFalse(bet.is_winner(self.outcomes[7]), 'Does not win on Seven')
        self.assertTrue(bet.is_loser(self.outcomes[7]), 'Loses on Seven')
        self.assertTrue(bet.is_winner(self.outcomes[4]), 'Wins on Point')
        self.assertFalse(bet.is_loser(self.outcomes[4]), 'Does not lose on Point')
        self.assertFalse(bet.is_winner(self.outcomes[11]), 'Does not win on Yo')
        self.assertFalse(bet.is_loser(self.outcomes[2]), 'Does not lose on Aces')
        self.assertFalse(bet.is_loser(self.outcomes[3]), 'Does not lose on Three')
        self.assertFalse(bet.is_loser(self.outcomes[12]), 'Does not lose on Midnight')
        self.assertFalse(bet.is_winner(other_point), 'Does not win on other point')
        self.assertFalse(bet.is_loser(other_point), 'Does not lose on other point')

    def test_put(self):
        point_roll = self.outcomes[4]
        other_point = self.outcomes[6]
        bet = table.bet.Put(self.wager, puck=self.puck, table_config=self.table_config,
                            location=self.outcomes[4].total())
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

        with self.assertRaises(table.bet.InvalidBet):  # Can not move twice
            bet.move(other_point.total())

        self.assertFalse(bet.is_winner(self.outcomes[7]), 'Does not win on Seven')
        self.assertTrue(bet.is_loser(self.outcomes[7]), 'Loses on Seven')
        self.assertTrue(bet.is_winner(self.outcomes[4]), 'Wins on Point')
        self.assertFalse(bet.is_loser(self.outcomes[4]), 'Does not lose on Point')
        self.assertFalse(bet.is_winner(self.outcomes[11]), 'Does not win on Yo')
        self.assertFalse(bet.is_loser(self.outcomes[2]), 'Does not lose on Aces')
        self.assertFalse(bet.is_loser(self.outcomes[3]), 'Does not lose on Three')
        self.assertFalse(bet.is_loser(self.outcomes[12]), 'Does not lose on Midnight')
        self.assertFalse(bet.is_winner(other_point), 'Does not win on other point')
        self.assertFalse(bet.is_loser(other_point), 'Does not lose on other point')

    def test_come(self):
        bet = table.bet.Come(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)
        self.assertTrue(bet.is_winner(self.outcomes[7]), 'Wins on Seven')
        self.assertTrue(bet.is_winner(self.outcomes[11]), 'Wins on Yo')
        self.assertTrue(bet.is_loser(self.outcomes[2]), 'Loses on Aces')
        self.assertTrue(bet.is_loser(self.outcomes[3]), 'Loses on Three')
        self.assertTrue(bet.is_loser(self.outcomes[12]), 'Loses on Midnight')

        point_roll = self.outcomes[4]
        other_point = self.outcomes[6]
        self.assertFalse(bet.is_winner(point_roll), 'Does Not Win on point number')
        self.assertFalse(bet.is_loser(point_roll), 'Does Not Lose on point number')

        bet.move(point_roll.total())
        with self.assertRaises(table.bet.InvalidBet):  # Can not move twice
            bet.move(other_point.total())

        self.assertFalse(bet.is_winner(self.outcomes[7]), 'Does not win on Seven')
        self.assertTrue(bet.is_loser(self.outcomes[7]), 'Loses on Seven')
        self.assertTrue(bet.is_winner(self.outcomes[4]), 'Wins on Point')
        self.assertFalse(bet.is_loser(self.outcomes[4]), 'Does not lose on Point')
        self.assertFalse(bet.is_winner(self.outcomes[11]), 'Does not win on Yo')
        self.assertFalse(bet.is_loser(self.outcomes[2]), 'Does not lose on Aces')
        self.assertFalse(bet.is_loser(self.outcomes[3]), 'Does not lose on Three')
        self.assertFalse(bet.is_loser(self.outcomes[12]), 'Does not lose on Midnight')
        self.assertFalse(bet.is_winner(other_point), 'Does not win on other point')
        self.assertFalse(bet.is_loser(other_point), 'Does not lose on other point')

    def test_dont_pass(self):
        bet = table.bet.DontPass(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

        self.assertTrue(bet.is_loser(self.outcomes[7]), 'Loses on Seven')
        self.assertTrue(bet.is_loser(self.outcomes[11]), 'Wins on Yo')
        self.assertTrue(bet.is_winner(self.outcomes[2]), 'Wins on Aces')
        self.assertTrue(bet.is_winner(self.outcomes[3]), 'Wins on Three')
        self.assertFalse(bet.is_winner(self.outcomes[12]), 'Does not lose on Midnight')
        self.assertFalse(bet.is_loser(self.outcomes[12]), 'Does not win on Midnight')

        point_roll = self.outcomes[4]
        other_point = self.outcomes[6]
        self.assertFalse(bet.is_winner(point_roll), 'Does Not Win on point number')
        self.assertFalse(bet.is_loser(point_roll), 'Does Not Lose on point number')

        bet.move(point_roll.total())
        with self.assertRaises(table.bet.InvalidBet):  # Can not move twice
            bet.move(other_point.total())

        self.assertTrue(bet.is_winner(self.outcomes[7]), 'Wins on Seven')
        self.assertFalse(bet.is_loser(self.outcomes[7]), 'Does not lose on Seven')
        self.assertTrue(bet.is_loser(self.outcomes[4]), 'Loses on Point')
        self.assertFalse(bet.is_winner(self.outcomes[4]), 'Does not win on Point')
        self.assertFalse(bet.is_loser(self.outcomes[11]), 'Does not lose on Yo')
        self.assertFalse(bet.is_winner(self.outcomes[2]), 'Does not win on Aces')
        self.assertFalse(bet.is_winner(self.outcomes[3]), 'Does not win on Three')
        self.assertFalse(bet.is_winner(self.outcomes[12]), 'Does not win on Midnight')
        self.assertFalse(bet.is_winner(other_point), 'Does not win on other point')
        self.assertFalse(bet.is_loser(other_point), 'Does not lose on other point')

    def test_dont_come(self):
        bet = table.bet.DontCome(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertTrue(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

        point_roll = self.outcomes[4]
        other_point = self.outcomes[6]
        self.assertFalse(bet.is_winner(point_roll), 'Does Not Win on point number')
        self.assertFalse(bet.is_loser(point_roll), 'Does Not Lose on point number')

        bet.move(point_roll.total())
        with self.assertRaises(table.bet.InvalidBet):  # Can not move twice
            bet.move(other_point.total())

        self.assertTrue(bet.is_winner(self.outcomes[7]), 'Wins on Seven')
        self.assertFalse(bet.is_loser(self.outcomes[7]), 'Does not lose on Seven')
        self.assertTrue(bet.is_loser(self.outcomes[4]), 'Loses on Point')
        self.assertFalse(bet.is_winner(self.outcomes[4]), 'Does not win on Point')
        self.assertFalse(bet.is_loser(self.outcomes[11]), 'Does not lose on Yo')
        self.assertFalse(bet.is_winner(self.outcomes[2]), 'Does not win on Aces')
        self.assertFalse(bet.is_winner(self.outcomes[3]), 'Does not win on Three')
        self.assertFalse(bet.is_winner(self.outcomes[12]), 'Does not win on Midnight')
        self.assertFalse(bet.is_winner(other_point), 'Does not win on other point')
        self.assertFalse(bet.is_loser(other_point), 'Does not lose on other point')

    def test_field(self):
        bet = table.bet.Field(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertTrue(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

        for outcome in self.outcomes.values():
            with self.subTest(i=outcome.total()):
                self.assertTrue(bet.is_winner(outcome)) if outcome.total() in [2, 3, 4, 9, 10, 11, 12] \
                    else self.assertFalse(bet.is_winner(outcome))
                self.assertTrue(bet.is_loser(outcome)) if outcome.total() in [5, 6, 7, 8] \
                    else self.assertFalse(bet.is_loser(outcome))

    def test_place(self):
        place_outcome = self.outcomes[4]
        other_outcome = self.outcomes[6]
        seven_outcome = self.outcomes[7]
        bet = table.bet.Place(self.wager,
                              puck=self.puck,
                              location=place_outcome.total(),
                              table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertTrue(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

        self.puck.place(other_outcome.total())  # Puck is On
        self.assertTrue(bet.is_on())
        self.assertTrue(bet.is_winner(place_outcome))
        self.assertFalse(bet.is_loser(place_outcome))
        self.assertFalse(bet.is_winner(other_outcome))
        self.assertFalse(bet.is_loser(other_outcome))
        self.assertFalse(bet.is_winner(seven_outcome))
        self.assertTrue(bet.is_loser(seven_outcome))

        bet.turn_off()  # Turn off bets (puck still on)

        for outcome in self.outcomes.values():
            with self.subTest("No effect when bet is off",
                              i=outcome.total()):
                self.assertFalse(bet.is_on())
                self.assertFalse(bet.is_winner(outcome))
                self.assertFalse(bet.is_loser(outcome))

        bet.follow_puck()  # Bet again following puck
        self.puck.remove()  # Puck is off

        for outcome in self.outcomes.values():
            with self.subTest("No effect when puck is off and bet follows puck",
                              i=outcome.total()):
                self.assertFalse(bet.is_on())
                self.assertFalse(bet.is_winner(outcome))
                self.assertFalse(bet.is_loser(outcome))

        bet.turn_on()  # Bet is on though puck is off
        self.assertTrue(bet.is_on())
        self.assertTrue(self.puck.is_off())
        self.assertTrue(bet.is_winner(place_outcome))
        self.assertFalse(bet.is_loser(place_outcome))
        self.assertFalse(bet.is_winner(other_outcome))
        self.assertFalse(bet.is_loser(other_outcome))
        self.assertFalse(bet.is_winner(seven_outcome))
        self.assertTrue(bet.is_loser(seven_outcome))

    def test_buy(self):
        place_outcome = self.outcomes[4]
        other_outcome = self.outcomes[6]
        seven_outcome = self.outcomes[7]
        bet = table.bet.Buy(self.wager, puck=self.puck, location=place_outcome.total(), table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertTrue(bet.can_toggle)
        self.assertTrue(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

        self.puck.place(other_outcome.total())  # Puck is On
        self.assertTrue(bet.is_on())
        self.assertTrue(bet.is_winner(place_outcome))
        self.assertFalse(bet.is_loser(place_outcome))
        self.assertFalse(bet.is_winner(other_outcome))
        self.assertFalse(bet.is_loser(other_outcome))
        self.assertFalse(bet.is_winner(seven_outcome))
        self.assertTrue(bet.is_loser(seven_outcome))

        bet.turn_off()  # Turn off bets (puck still on)

        for outcome in self.outcomes.values():
            with self.subTest("No effect when bet is off",
                              i=outcome.total()):
                self.assertFalse(bet.is_on())
                self.assertFalse(bet.is_winner(outcome))
                self.assertFalse(bet.is_loser(outcome))

        bet.follow_puck()  # Bet again following puck
        self.puck.remove()  # Puck is off

        for outcome in self.outcomes.values():
            with self.subTest("No effect when puck is off and bet follows puck",
                              i=outcome.total()):
                self.assertFalse(bet.is_on())
                self.assertFalse(bet.is_winner(outcome))
                self.assertFalse(bet.is_loser(outcome))

        bet.turn_on()  # Bet is on though puck is off
        self.assertTrue(bet.is_on())
        self.assertTrue(self.puck.is_off())
        self.assertTrue(bet.is_winner(place_outcome))
        self.assertFalse(bet.is_loser(place_outcome))
        self.assertFalse(bet.is_winner(other_outcome))
        self.assertFalse(bet.is_loser(other_outcome))
        self.assertFalse(bet.is_winner(seven_outcome))
        self.assertTrue(bet.is_loser(seven_outcome))

    def test_lay(self):
        place_outcome = self.outcomes[4]
        other_outcome = self.outcomes[6]
        seven_outcome = self.outcomes[7]
        bet = table.bet.Lay(self.wager,
                            puck=self.puck,
                            location=place_outcome.total(),
                            table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertTrue(bet.can_toggle)
        self.assertTrue(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

        self.assertTrue(bet.is_on())
        self.assertTrue(bet.is_winner(seven_outcome))
        self.assertFalse(bet.is_loser(seven_outcome))
        self.assertFalse(bet.is_winner(other_outcome))
        self.assertFalse(bet.is_loser(other_outcome))
        self.assertFalse(bet.is_winner(place_outcome))
        self.assertTrue(bet.is_loser(place_outcome))

        bet.turn_off()  # Turn off bets (puck still on)

        for outcome in self.outcomes.values():
            with self.subTest("No effect when bet is off",
                              i=outcome.total()):
                self.assertFalse(bet.is_on())
                self.assertFalse(bet.is_winner(outcome))
                self.assertFalse(bet.is_loser(outcome))


if __name__ == '__main__':
    unittest.main()
