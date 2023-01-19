"""
Module: Craps.Table.Interface
"""
from craps.table.config import Config
from craps.table.puck import Puck, PuckLocation


class TableInterface:
    """Table Interface"""
    config: Config  #: Table Configuration (rules)
    puck: Puck  #: The Point Puck on the table

    def point_set(self) -> bool:
        """
        Point is set.

        :return: If Point is set or not
        :rtype: bool
        """
        return self.puck.is_on()

    def get_point(self) -> PuckLocation:
        """
        Value of current point

        :return: Value of current point
        :rtype: PuckLocation
        """
        return self.puck.location()
