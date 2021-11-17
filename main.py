# -*- coding: utf-8 -*-

from data_manager import DataBase
import login


class System:
    SYSTEM_IDLE = 0
    SYSTEM_STARTED = 1
    SYSTEM_FINISHED = 2

    def __init__(self) -> None:
        self.start()
        self._status = self.SYSTEM_IDLE

    @property
    def database(self) -> DataBase:
        return self._database

    @property
    def status(self) -> int:
        return self._status

    def start(self):
        self._database = DataBase()
        self._database.connect()

        login.DATABASE = self.database

        self._status = self.SYSTEM_STARTED

    def finish(self):
        self._database.close()

        self._status = self.SYSTEM_FINISHED


if __name__ == "__main__":
    SYSTEM = System()
    SYSTEM.start()
    SYSTEM.finish()
