import json
import typing

from craps.table.config import Config


class IllegalMove(Exception):
    pass


class Puck:
    _location: typing.Union[int, None] = None

    def __init__(self, table_config: Config):
        self.table_config = table_config

    def is_on(self) -> bool:
        return self._location is not None

    def is_off(self) -> bool:
        return not self.is_on()

    def place(self, location: int) -> typing.NoReturn:
        if self.is_on():
            raise IllegalMove("Puck already placed")
        if location not in self.table_config.get_valid_points():
            raise IllegalMove("Invalid puck location")
        self._location = location

    def location(self) -> typing.Union[int, None]:
        return self._location

    def remove(self) -> typing.NoReturn:
        if self.is_off():
            raise IllegalMove("Puck is already Off")
        self._location = None

    def as_json(self) -> str:
        return json.dumps(self._location)

    def set_from_json(self, json_str):
        self._location = json.loads(json_str)
        return self
