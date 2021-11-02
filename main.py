# -*- coding: utf-8 -*-

from data_manager import DataBase
import login


class System:

    def __init__(self) -> None:
        self._database = DataBase()
        self._database.connect()

        login.DATABASE = self.database

    @property
    def database(self):
        return self._database


if __name__ == "__main__":
    SYSTEM = System()
