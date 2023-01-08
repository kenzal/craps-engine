from dataclasses import dataclass
from .odds import Odds, StandardOdds, CraplessOdds


class InconsistentConfig(Exception):
    pass


@dataclass(frozen=True)
class Config:
    allow_buy_59: bool = False
    allow_put: bool = False
    bet_max: int = None
    bet_min: int = 5
    dont_bar: int = 12
    field_12_pay: int = 3
    field_2_pay: int = 2
    hard_way_max: int = None
    hop_easy_pay_to_one: int = 15
    hop_hard_pay_to_one: int = 30
    hop_max: int = None
    is_crapless: bool = False
    min_buy_lay: int = None
    odds: Odds = StandardOdds.mirrored345()
    odds_max: int = None
    pay_vig_before_buy: bool = False
    pay_vig_before_lay: bool = False

    def __post_init__(self):
        if self.is_crapless and not isinstance(self.odds, CraplessOdds):
            raise InconsistentConfig('Crapless Config requires CraplessOdds')
        if not self.is_crapless and not isinstance(self.odds, StandardOdds):
            raise InconsistentConfig('Standard Craps requires Standard Odds')
        if self.dont_bar not in [2, 3, 12]:
            raise InconsistentConfig("dont_bar Must Bar a Craps Number")
        if self.bet_min % 5:
            raise InconsistentConfig("bet_min must be multiple of 5")
        if self.bet_max and self.bet_max % 5:
            raise InconsistentConfig("bet_max, if set, must be multiple of 5")
        if self.bet_max and self.bet_max < self.bet_min:
            raise InconsistentConfig("bet_max, if set, must be greater than bet_min")
