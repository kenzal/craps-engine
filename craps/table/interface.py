from craps.table.config import Config
from craps.table.puck import Puck, PuckLocation


class TableInterface:
    config: Config  #: Table Configuration (rules)
    puck: Puck  #: The Point Puck on the table

    def point_set(self) -> bool:
        return self.puck.is_on()

    def get_point(self) -> PuckLocation:
        return self.puck.location()