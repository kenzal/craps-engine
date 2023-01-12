import unittest
import craps.table as table
import craps.table.config as TableConfig
from craps.dice import Outcome


# noinspection DuplicateAssertionTestSmellUnittest
class TestBet(unittest.TestCase):
    puck: table.puck.Puck
    table_config: TableConfig
    wager: int

    def setUp(self) -> None:
        self.table_config = table.config.Config()
        self.puck = table.puck.Puck(self.table_config)
        self.wager = 60
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
        self.assertEqual(self.wager, bet.get_payout(self.outcomes[7]))
        self.assertEqual(self.wager, bet.get_payout(self.outcomes[11]))

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
        self.assertEqual(self.wager, bet.get_payout(point_roll))
        self.assertEqual(0, bet.get_payout(self.outcomes[11]))

        signature = bet.get_signature()
        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                         puck=bet._puck,
                                                         table_config=bet._table_config)
        self.assertEqual(bet, reconstructed_bet)

    def test_pass_line_odds_payouts(self):
        for j, config in enumerate([
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.mirrored345()),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(2)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(5)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(10)),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(2)),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(3)),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(5)),
        ]):
            with self.subTest(j=j):
                for total in config.odds.valid_keys():
                    outcome = self.outcomes[total]
                    if total != 7:
                        with self.subTest(i=total):
                            bet = table.bet.Come(self.wager, puck=self.puck, table_config=config,
                                                 location=total)
                            self.assertEqual(bet.max_odds(), config.odds[total] * self.wager,
                                             "Max Odds should be the max odds for the place number times the wager")
                            odds_payout = int(bet.max_odds() * config.get_true_odds(total))
                            bet.set_odds(bet.max_odds())
                            self.assertEqual(bet.get_payout(outcome), self.wager + odds_payout)

                            signature = bet.get_signature()
                            reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                             puck=bet._puck,
                                                                             table_config=bet._table_config)
                            self.assertEqual(bet, reconstructed_bet)

    def test_put(self):
        point_roll = self.outcomes[4]
        other_point = self.outcomes[6]
        bet = table.bet.Put(self.wager, puck=self.puck, table_config=self.table_config,
                            location=point_roll.total())
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

        signature = bet.get_signature()
        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                         puck=bet._puck,
                                                         table_config=bet._table_config)
        self.assertEqual(bet, reconstructed_bet)

    def test_put_payouts(self):
        for j, config in enumerate([
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.mirrored345()),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(2)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(5)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(10)),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(2)),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(3)),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(5)),
        ]):
            with self.subTest(j=j):
                for total in config.odds.valid_keys():
                    outcome = self.outcomes[total]
                    if total != 7:
                        with self.subTest(i=total):
                            bet = table.bet.Put(self.wager, puck=self.puck, table_config=config, location=total)
                            self.assertTrue(bet.is_winner(outcome))
                            self.assertEqual(self.wager, bet.get_payout(outcome))
                            odds_bet = self.wager * 2
                            odds_payout = int(config.get_true_odds(total) * odds_bet)
                            bet.set_odds(odds_bet)
                            payout = bet.get_payout(outcome)
                            self.assertEqual(payout, self.wager + odds_payout)

                            signature = bet.get_signature()
                            reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                             puck=bet._puck,
                                                                             table_config=bet._table_config)
                            self.assertEqual(bet, reconstructed_bet)

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

        signature = bet.get_signature()
        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                         puck=bet._puck,
                                                         table_config=bet._table_config)
        self.assertEqual(bet, reconstructed_bet)

    def test_come_payouts(self):
        for j, config in enumerate([
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.mirrored345()),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(2)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(5)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(10)),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(2)),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(3)),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(5)),
        ]):
            with self.subTest(j=j):
                for total in config.odds.valid_keys():
                    outcome = self.outcomes[total]
                    if total != 7:
                        with self.subTest(i=total):
                            bet = table.bet.Come(self.wager, puck=self.puck, table_config=config, location=total)
                            self.assertTrue(bet.is_winner(outcome))
                            self.assertEqual(self.wager, bet.get_payout(outcome))
                            odds_bet = self.wager * 2
                            odds_payout = int(config.get_true_odds(total) * odds_bet)
                            bet.set_odds(odds_bet)
                            payout = bet.get_payout(outcome)
                            self.assertEqual(payout, self.wager + odds_payout)

                            signature = bet.get_signature()
                            reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                             puck=bet._puck,
                                                                             table_config=bet._table_config)
                            self.assertEqual(bet, reconstructed_bet)

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

        signature = bet.get_signature()
        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                         puck=bet._puck,
                                                         table_config=bet._table_config)
        self.assertEqual(bet, reconstructed_bet)

    def test_dont_pass_max_odds(self):
        for j, config in enumerate([
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.mirrored345()),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(2)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(5)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(10)),
        ]):
            with self.subTest(j=j):
                seven_out = self.outcomes[7]
                for total in config.odds.valid_keys():
                    if total != 7:
                        with self.subTest(i=total):
                            wager = 5
                            bet = table.bet.DontPass(wager, puck=self.puck, table_config=config, location=total)
                            odds_payout = int(bet.max_odds() / config.get_true_odds(total))
                            bet.set_odds(bet.max_odds())
                            self.assertEqual(bet.get_payout(seven_out), wager + odds_payout)

                            signature = bet.get_signature()
                            reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                             puck=bet._puck,
                                                                             table_config=bet._table_config)
                            self.assertEqual(bet, reconstructed_bet)

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

        signature = bet.get_signature()
        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                         puck=bet._puck,
                                                         table_config=bet._table_config)
        self.assertEqual(bet, reconstructed_bet)

    def test_dont_come_max_odds(self):
        for j, config in enumerate([
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.mirrored345()),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(2)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(5)),
            TableConfig.Config(odds=TableConfig.odds.StandardOdds.flat(10)),
        ]):
            with self.subTest(j=j):
                seven_out = self.outcomes[7]
                for total in config.odds.valid_keys():
                    if total != 7:
                        with self.subTest(i=total):
                            wager = 5
                            bet = table.bet.DontCome(wager, puck=self.puck, table_config=config, location=total)
                            odds_payout = int(bet.max_odds() / config.get_true_odds(total))
                            bet.set_odds(bet.max_odds())
                            self.assertEqual(bet.get_payout(seven_out), wager + odds_payout)

                            signature = bet.get_signature()
                            reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                             puck=bet._puck,
                                                                             table_config=bet._table_config)
                            self.assertEqual(bet, reconstructed_bet)

    def test_field(self):
        bet = table.bet.Field(self.wager, puck=self.puck, table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertFalse(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertTrue(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

        for j, config in enumerate([
            TableConfig.Config(field_2_pay=2, field_12_pay=2),
            TableConfig.Config(field_2_pay=2, field_12_pay=3),
            TableConfig.Config(field_2_pay=3, field_12_pay=2),
            TableConfig.Config(field_2_pay=3, field_12_pay=3),
        ]):
            with self.subTest(j=j):
                for outcome in self.outcomes.values():
                    with self.subTest(i=outcome.total()):
                        bet = table.bet.Field(self.wager, puck=self.puck, table_config=config)
                        if outcome.total() in [3, 4, 9, 10, 11]:
                            self.assertTrue(bet.is_winner(outcome))
                            self.assertFalse(bet.is_loser(outcome))
                            self.assertEqual(bet.get_payout(outcome), self.wager)
                        elif outcome.total() == 2:
                            self.assertTrue(bet.is_winner(outcome))
                            self.assertFalse(bet.is_loser(outcome))
                            self.assertEqual(bet.get_payout(outcome), self.wager * config.field_2_pay)
                        elif outcome.total() == 12:
                            self.assertTrue(bet.is_winner(outcome))
                            self.assertFalse(bet.is_loser(outcome))
                            self.assertEqual(bet.get_payout(outcome), self.wager * config.field_12_pay)
                        else:
                            self.assertTrue(bet.is_loser(outcome))
                            self.assertFalse(bet.is_winner(outcome))

                        signature = bet.get_signature()
                        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                         puck=bet._puck,
                                                                         table_config=bet._table_config)
                        self.assertEqual(bet, reconstructed_bet)

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

        signature = bet.get_signature()
        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                         puck=bet._puck,
                                                         table_config=bet._table_config)
        self.assertEqual(bet, reconstructed_bet)

    def test_place_payouts(self):
        self.puck.place(6)
        for j, config in enumerate([
            TableConfig.Config(pay_vig_before_buy=True),
            TableConfig.Config(pay_vig_before_buy=False),
        ]):
            with self.subTest(j=j):
                for total in config.odds.valid_keys():
                    outcome = self.outcomes[total]
                    with self.subTest(i=total):
                        bet = table.bet.Place(self.wager, puck=self.puck, table_config=config, location=total)
                        self.assertTrue(bet.is_winner(outcome))
                        self.assertEqual(bet.get_payout(outcome), int(self.wager * config.get_place_odds(total)))

                        signature = bet.get_signature()
                        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                         puck=bet._puck,
                                                                         table_config=bet._table_config)
                        self.assertEqual(bet, reconstructed_bet)

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

        signature = bet.get_signature()
        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                         puck=bet._puck,
                                                         table_config=bet._table_config)
        self.assertEqual(bet, reconstructed_bet)

    def test_buy_payouts(self):
        self.puck.place(6)
        for j, config in enumerate([
            TableConfig.Config(pay_vig_before_buy=True),
            TableConfig.Config(pay_vig_before_buy=False),
        ]):
            with self.subTest(j=j):
                for total in config.odds.valid_keys():
                    outcome = self.outcomes[total]
                    with self.subTest(i=total):
                        bet = table.bet.Buy(self.wager, puck=self.puck, table_config=config, location=total)
                        self.assertTrue(bet.is_winner(outcome))
                        self.assertEqual(bet.get_payout(outcome),
                                         int(self.wager * config.get_true_odds(total)) - bet.get_vig())

                        signature = bet.get_signature()
                        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                         puck=bet._puck,
                                                                         table_config=bet._table_config)
                        self.assertEqual(bet, reconstructed_bet)

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

    def test_lay_payouts(self):
        for j, config in enumerate([
            TableConfig.Config(pay_vig_before_lay=False),
            TableConfig.Config(pay_vig_before_lay=True),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(2), pay_vig_before_lay=False),
            TableConfig.Config(is_crapless=True, odds=TableConfig.odds.CraplessOdds.flat(2), pay_vig_before_lay=True),
        ]):
            with self.subTest(j=j):
                for total in config.odds.valid_keys():
                    seven_out = self.outcomes[7]
                    with self.subTest(i=total):
                        bet = table.bet.Lay(self.wager, puck=self.puck, table_config=config, location=total)
                        self.assertTrue(bet.is_winner(seven_out))
                        self.assertEqual(bet.get_payout(seven_out),
                                         int(self.wager / config.get_true_odds(total)) - bet.get_vig())

                        signature = bet.get_signature()
                        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                         puck=bet._puck,
                                                                         table_config=bet._table_config)
                        self.assertEqual(bet, reconstructed_bet)

    def test_hard_way(self):
        bet_hard_outcome = Outcome(2, 2)
        bet_easy_outcome = Outcome(1, 3)
        self.assertEqual(bet_easy_outcome.total(), bet_hard_outcome.total())
        self.assertNotEqual(bet_easy_outcome, bet_hard_outcome)
        self.assertFalse(bet_easy_outcome.is_hard())
        self.assertTrue(bet_hard_outcome.is_hard())
        other_outcome = self.outcomes[6]
        bet = table.bet.HardWay(self.wager,
                                puck=self.puck,
                                location=bet_hard_outcome.total(),
                                table_config=self.table_config)
        self.assertFalse(bet.allow_odds)
        self.assertTrue(bet.can_toggle)
        self.assertFalse(bet.has_vig)
        self.assertFalse(bet.multi_bet)
        self.assertFalse(bet.single_roll)
        self.assertEqual(bet.wager, self.wager)
        self.assertIsNone(bet.odds)

        # Puck is Off, bet following puck
        for outcome in [bet_hard_outcome, bet_easy_outcome, other_outcome, self.outcomes[7]]:
            with self.subTest("No effect when puck is off and bet follows puck",
                              i=outcome.total()):
                self.assertFalse(bet.is_on())
                self.assertFalse(bet.is_winner(outcome))
                self.assertFalse(bet.is_loser(outcome))

        self.puck.place(bet_hard_outcome.total())  # puck is on, bet following puck
        self.assertTrue(bet.is_winner(bet_hard_outcome))
        self.assertFalse(bet.is_loser(bet_hard_outcome))
        self.assertTrue(bet.is_loser(bet_easy_outcome))
        self.assertFalse(bet.is_winner(bet_easy_outcome))
        self.assertFalse(bet.is_winner(other_outcome))
        self.assertFalse(bet.is_loser(other_outcome))

        bet.turn_off()  # puck is on, but hard way is off
        for outcome in [bet_hard_outcome, bet_easy_outcome, other_outcome, self.outcomes[7]]:
            with self.subTest("No effect when puck is off and bet follows puck",
                              i=outcome.total()):
                self.assertFalse(bet.is_on())
                self.assertFalse(bet.is_winner(outcome))
                self.assertFalse(bet.is_loser(outcome))

        bet.turn_on()
        self.puck.remove()  # puck is off, but bet is on

        self.puck.place(bet_hard_outcome.total())  # puck is on, bet following puck
        self.assertTrue(bet.is_winner(bet_hard_outcome))
        self.assertFalse(bet.is_loser(bet_hard_outcome))
        self.assertTrue(bet.is_loser(bet_easy_outcome))
        self.assertFalse(bet.is_winner(bet_easy_outcome))
        self.assertFalse(bet.is_winner(other_outcome))
        self.assertFalse(bet.is_loser(other_outcome))

        signature = bet.get_signature()
        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                         puck=bet._puck,
                                                         table_config=bet._table_config)
        self.assertEqual(bet, reconstructed_bet)

    def test_hard_ways_payout(self):
        for outcome in [
            Outcome(2, 2),
            Outcome(3, 3),
            Outcome(4, 4),
            Outcome(5, 5),
        ]:
            with self.subTest(i=outcome.total()):
                bet = table.bet.HardWay(self.wager,
                                        puck=self.puck,
                                        table_config=self.table_config,
                                        location=outcome.total())
                bet.turn_on()
                self.assertTrue(bet.is_winner(outcome))
                self.assertEqual(bet.get_payout(outcome), self.wager * (7 if outcome.total() in [4, 10] else 9))

                signature = bet.get_signature()
                reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                 puck=bet._puck,
                                                                 table_config=bet._table_config)
                self.assertEqual(bet, reconstructed_bet)

    def test_any_seven(self):
        for i, outcome in enumerate(Outcome.get_all()):
            with self.subTest("All Totals of Seven should win, otherwise, lose",
                              i=i):
                bet = table.bet.AnySeven(self.wager,
                                         puck=self.puck,
                                         table_config=self.table_config)
                self.assertFalse(bet.allow_odds)
                self.assertFalse(bet.can_toggle)
                self.assertFalse(bet.has_vig)
                self.assertFalse(bet.multi_bet)
                self.assertTrue(bet.single_roll)
                self.assertEqual(bet.wager, self.wager)
                self.assertIsNone(bet.odds)
                if outcome.total() == 7:
                    self.assertTrue(bet.is_winner(outcome))
                    self.assertFalse(bet.is_loser(outcome))
                    self.assertEqual(bet.get_payout(outcome), self.wager * 4)
                else:
                    self.assertTrue(bet.is_loser(outcome))
                    self.assertFalse(bet.is_winner(outcome))

                signature = bet.get_signature()
                reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                 puck=bet._puck,
                                                                 table_config=bet._table_config)
                self.assertEqual(bet, reconstructed_bet)

    def test_any_craps(self):
        for i, outcome in enumerate(Outcome.get_all()):
            with self.subTest("All Craps should win, otherwise, lose",
                              i=i):
                bet = table.bet.AnyCraps(self.wager,
                                         puck=self.puck,
                                         table_config=self.table_config)
                self.assertFalse(bet.allow_odds)
                self.assertFalse(bet.can_toggle)
                self.assertFalse(bet.has_vig)
                self.assertFalse(bet.multi_bet)
                self.assertTrue(bet.single_roll)
                self.assertEqual(bet.wager, self.wager)
                self.assertIsNone(bet.odds)
                if outcome.total() in [2, 3, 12]:
                    self.assertTrue(bet.is_winner(outcome))
                    self.assertFalse(bet.is_loser(outcome))
                    self.assertEqual(bet.get_payout(outcome), self.wager * 7)
                else:
                    self.assertTrue(bet.is_loser(outcome))
                    self.assertFalse(bet.is_winner(outcome))

                signature = bet.get_signature()
                reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                 puck=bet._puck,
                                                                 table_config=bet._table_config)
                self.assertEqual(bet, reconstructed_bet)

    def test_hop(self):
        for i, outcome in enumerate(Outcome.get_all()):
            with self.subTest(i=i):
                bet = table.bet.Hop(self.wager,
                                    puck=self.puck,
                                    table_config=self.table_config,
                                    outcome=outcome)
                self.assertFalse(bet.allow_odds)
                self.assertFalse(bet.can_toggle)
                self.assertFalse(bet.has_vig)
                self.assertFalse(bet.multi_bet)
                self.assertTrue(bet.single_roll)
                self.assertEqual(bet.wager, self.wager)
                self.assertIsNone(bet.odds)
                for j, test_outcome in enumerate(Outcome.get_all()):
                    with self.subTest("Only when outcome is test outcome should win, otherwise, lose",
                                      j=j):
                        if outcome == test_outcome:
                            self.assertTrue(bet.is_winner(test_outcome))
                            self.assertFalse(bet.is_loser(test_outcome))
                            self.assertEqual(bet.get_payout(test_outcome),
                                             self.wager * (self.table_config.hop_hard_pay_to_one if
                                                           test_outcome.is_hard()
                                                           else self.table_config.hop_easy_pay_to_one))
                        else:
                            self.assertTrue(bet.is_loser(test_outcome))
                            self.assertFalse(bet.is_winner(test_outcome))

                        signature = bet.get_signature()
                        reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                         puck=bet._puck,
                                                                         table_config=bet._table_config)
                        self.assertEqual(bet, reconstructed_bet)

    def test_horn(self):
        for i, outcome in enumerate(Outcome.get_all()):
            with self.subTest("Horn bets should win, otherwise, lose",
                              i=i):
                bet = table.bet.Horn(self.wager,
                                     puck=self.puck,
                                     table_config=self.table_config)
                self.assertFalse(bet.allow_odds)
                self.assertFalse(bet.can_toggle)
                self.assertFalse(bet.has_vig)
                self.assertEqual(bet.multi_bet, 4)
                self.assertTrue(bet.single_roll)
                self.assertEqual(bet.wager, self.wager)
                self.assertIsNone(bet.odds)
                if outcome.total() in [2, 3, 11, 12]:
                    self.assertTrue(bet.is_winner(outcome))
                    self.assertFalse(bet.is_loser(outcome))
                    self.assertEqual(bet.get_payout(outcome),
                                     self.wager / 4 * (self.table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                       else self.table_config.hop_easy_pay_to_one))
                else:
                    self.assertTrue(bet.is_loser(outcome))
                    self.assertFalse(bet.is_winner(outcome))

                signature = bet.get_signature()
                reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                 puck=bet._puck,
                                                                 table_config=bet._table_config)
                self.assertEqual(bet, reconstructed_bet)

    def test_horn_high(self):
        for i, outcome in enumerate(Outcome.get_all()):
            with self.subTest("Horn bets should win, otherwise, lose",
                              i=i):
                bet = table.bet.HornHigh(self.wager,
                                         puck=self.puck,
                                         location=11,  # Horn High Yo
                                         table_config=self.table_config)
                self.assertFalse(bet.allow_odds)
                self.assertFalse(bet.can_toggle)
                self.assertFalse(bet.has_vig)
                self.assertEqual(bet.multi_bet, 5)
                self.assertTrue(bet.single_roll)
                self.assertEqual(bet.wager, self.wager)
                self.assertIsNone(bet.odds)
                if outcome.total() in [2, 3, 12]:
                    self.assertTrue(bet.is_winner(outcome))
                    self.assertFalse(bet.is_loser(outcome))
                    self.assertEqual(bet.get_payout(outcome),
                                     self.wager / 5 * (self.table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                       else self.table_config.hop_easy_pay_to_one))
                elif outcome.total() == 11:
                    self.assertTrue(bet.is_winner(outcome))
                    self.assertFalse(bet.is_loser(outcome))
                    self.assertEqual(bet.get_payout(outcome),
                                     self.wager / 5 * 2 * (self.table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                           else self.table_config.hop_easy_pay_to_one))
                else:
                    self.assertTrue(bet.is_loser(outcome))
                    self.assertFalse(bet.is_winner(outcome))

                signature = bet.get_signature()
                reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                 puck=bet._puck,
                                                                 table_config=bet._table_config)
                self.assertEqual(bet, reconstructed_bet)

    def test_world(self):
        for i, outcome in enumerate(Outcome.get_all()):
            with self.subTest("Horn bets should win, 7 pushes, otherwise, lose",
                              i=i):
                bet = table.bet.World(self.wager,
                                      puck=self.puck,
                                      table_config=self.table_config)
                self.assertFalse(bet.allow_odds)
                self.assertFalse(bet.can_toggle)
                self.assertFalse(bet.has_vig)
                self.assertEqual(bet.multi_bet, 5)
                self.assertTrue(bet.single_roll)
                self.assertEqual(bet.wager, self.wager)
                self.assertIsNone(bet.odds)
                if outcome.total() == 7:  # Push Bet
                    self.assertFalse(bet.is_winner(outcome))
                    self.assertFalse(bet.is_loser(outcome))
                else:
                    if outcome.total() in [2, 3, 11, 12]:  # Win
                        self.assertTrue(bet.is_winner(outcome))
                        self.assertFalse(bet.is_loser(outcome))
                        self.assertEqual(bet.get_payout(outcome),
                                         self.wager / 5 * (self.table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                           else self.table_config.hop_easy_pay_to_one))
                    else:  # Lose
                        self.assertTrue(bet.is_loser(outcome))
                        self.assertFalse(bet.is_winner(outcome))

                signature = bet.get_signature()
                reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                 puck=bet._puck,
                                                                 table_config=bet._table_config)
                self.assertEqual(bet, reconstructed_bet)

    def test_craps_3_way(self):
        for i, outcome in enumerate(Outcome.get_all()):
            with self.subTest("Craps bets should win, otherwise, lose",
                              i=i):
                bet = table.bet.Craps3Way(self.wager,
                                          puck=self.puck,
                                          table_config=self.table_config)
                self.assertFalse(bet.allow_odds)
                self.assertFalse(bet.can_toggle)
                self.assertFalse(bet.has_vig)
                self.assertEqual(bet.multi_bet, 3)
                self.assertTrue(bet.single_roll)
                self.assertEqual(bet.wager, self.wager)
                self.assertIsNone(bet.odds)
                if outcome.total() in [2, 3, 12]:
                    self.assertTrue(bet.is_winner(outcome))
                    self.assertFalse(bet.is_loser(outcome))
                    self.assertEqual(bet.get_payout(outcome),
                                     self.wager / 3 * (self.table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                       else self.table_config.hop_easy_pay_to_one))
                else:
                    self.assertTrue(bet.is_loser(outcome))
                    self.assertFalse(bet.is_winner(outcome))

    def test_c_and_e(self):
        for i, outcome in enumerate(Outcome.get_all()):
            with self.subTest("Horn bets should win, otherwise, lose",
                              i=i):
                bet = table.bet.CE(self.wager,
                                   puck=self.puck,
                                   table_config=self.table_config)
                self.assertFalse(bet.allow_odds)
                self.assertFalse(bet.can_toggle)
                self.assertFalse(bet.has_vig)
                self.assertEqual(bet.multi_bet, 2)
                self.assertTrue(bet.single_roll)
                self.assertEqual(bet.wager, self.wager)
                self.assertIsNone(bet.odds)
                if outcome.total() in [2, 3, 12]:
                    self.assertTrue(bet.is_winner(outcome))
                    self.assertFalse(bet.is_loser(outcome))
                    self.assertEqual(bet.get_payout(outcome), self.wager / 2 * 7)
                elif outcome.total() == 11:
                    self.assertTrue(bet.is_winner(outcome))
                    self.assertFalse(bet.is_loser(outcome))
                    self.assertEqual(bet.get_payout(outcome), self.wager / 2 * self.table_config.hop_easy_pay_to_one)
                else:
                    self.assertTrue(bet.is_loser(outcome))
                    self.assertFalse(bet.is_winner(outcome))

                signature = bet.get_signature()
                reconstructed_bet = table.bet.Bet.from_signature(signature=signature,
                                                                 puck=bet._puck,
                                                                 table_config=bet._table_config)
                self.assertEqual(bet, reconstructed_bet)


if __name__ == '__main__':
    unittest.main()
