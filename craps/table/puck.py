"""
Module: Craps.Table.Puck
"""
import json
import typing

from craps.table.config import Config


class IllegalMove(Exception):
    """Illegal Move Exception"""


class Puck:
    """
    The On/Off Puck for a craps table.

    Each puck is aware of its table configuration in order to determine legal placement.
    """
    table_config: Config  #: Craps Table Configuration - used to determine legal placement
    _location: typing.Union[int, None] = None

    def __init__(self, table_config: Config):
        """

        :param table_config: Table Configuration
        :type table_config: Config
        """
        self.table_config = table_config

    def for_json(self) -> typing.Union[None, int]:
        """
        Either None or int(2-12) for the puck location for json serialization.

        :return: None or Point as integer
        :rtype: None|int
        """
        return self._location

    def is_on(self) -> bool:
        """
        True if the puck has a location, False otherwise.

        :return: bool
        """
        return self._location is not None

    def is_off(self) -> bool:
        """
        True if the puck has no location, False otherwise.

        :return: bool
        """
        return not self.is_on()

    def location(self) -> typing.Union[int, None]:
        """
        None or int(2-12) for the puck location.

        :return: None or Point as integer
        :rtype: None|int
        """
        return self._location

    def place(self, location: int) -> typing.NoReturn:
        """
        Set the puck location to the desired point.

        :param location: Point as an integer
        :type location: int
        :raise IllegalMove: Raised if attempting in illegal operation
        """
        if self.is_on():
            raise IllegalMove("Puck already placed")
        if location not in self.table_config.get_valid_points():
            raise IllegalMove("Invalid puck location")
        self._location = location

    def remove(self) -> typing.NoReturn:
        """
        Remove the puck from the point.

        :raise IllegalMove: Raised if puck is already off.
        """
        if self.is_off():
            raise IllegalMove("Puck is already Off")
        self._location = None

    def set_from_json(self, json_str):
        """
        Sets the location of the puck from a json string serialization

        :param json_str: JSON Representation of puck
        :type json_str: str
        """
        self._location = json.loads(json_str)
        return self
