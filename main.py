# -*- coding: utf-8 -*-

from data_manager import DataBase
import login

class System:

    def __init__(self) -> None:
        self.start()

    @property
    def database(self) -> DataBase:
        return self._database

    def start(self):
        self._database = DataBase()
        self._database.connect()

        login.DATABASE = self.database

    def finish(self):
        self._database.close()


if __name__ == "__main__":
    SYSTEM = System()
    SYSTEM.start()
    SYSTEM.finish()
