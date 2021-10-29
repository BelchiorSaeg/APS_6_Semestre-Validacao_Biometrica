# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
from exceptions import DataBaseError, ExceptionCodes

_DATABASE_PATH = "data\\user_data\\database.db"
_CREATION_CODE_PATH = "data\\user_data\\database_creation_code.sql"
_INSERTION_CODE_PATH = "data\\user_data\\database_insertion_code.sql"
_AGROTOXICOS_PATH = "data\\agrotoxicos\\agrofitprodutosformulados.csv"
_INFORMACOES_FISCAIS_PATH = "data\\informacoes_fiscais\\mapa_despesas.csv"
_INFORMACOES_FISCAIS_2_PATH = "data\\informacoes_fiscais\\mapa_receitas.csv"
_PRODUTORES_RURAIS_PATH = "data\\produtores_rurais\\cnpomapa30092019.csv"


class DataBase:

    def __init__(self) -> None:

        try:
            with open(_DATABASE_PATH):
                pass

            self._start_connection()

        except FileNotFoundError:
            self._create_database()

    def _create_database(self) -> None:

        with open(_CREATION_CODE_PATH, encoding="UTF-8") as file:
            creation_code = file.read()

        with open(_INSERTION_CODE_PATH, encoding="UTF-8") as file:
            insertion_code = file.read()

        connection = sqlite3.connect(_DATABASE_PATH)

        cursor = connection.cursor()

        cursor.execute(creation_code)
        cursor.execute(insertion_code)
        connection.commit()
        cursor.close()

        self.connection = connection

    def _start_connection(self) -> None:
        self.connection = sqlite3.connect(_DATABASE_PATH)

    def get_user_passwords(self, email: str) -> str:
        querry = f"""
SELECT PASSWORD_TEXT, PASSWORD_BIOMETRY FROM USERS U
WHERE U.EMAIL = '{email}'
"""
        cursor = self.connection.cursor()

        try:
            password = list(cursor.execute(querry))[0]

        except IndexError:
            error_code = ExceptionCodes.DataBaseError.NO_DATA_FOUND

            raise DataBaseError(error_code, "No data Found")

        finally:
            cursor.close()

        return password

    def get_user_data(self, email: str) -> str:
        querry = f"""
SELECT ID, FULL_NAME, EMAIL, PERMISSION_LEVEL FROM USERS U
WHERE U.EMAIL = '{email}'
"""
        cursor = self.connection.cursor()

        try:
            user_data = list(cursor.execute(querry))[0]
        except IndexError:
            error_code = ExceptionCodes.DataBaseError.NO_DATA_FOUND

            raise DataBaseError(error_code, "No data Found")

        finally:
            cursor.close()

        return user_data

    @property
    def agrotoxicos(self):
        df = pd.read_csv(_AGROTOXICOS_PATH, sep=";")

        return df

    @property
    def informacoes_fiscais(self):
        df_1 = pd.read_csv(_INFORMACOES_FISCAIS_PATH, sep=";")
        df_2 = pd.read_csv(_INFORMACOES_FISCAIS_2_PATH, sep=";")

        return df_1, df_2

    @property
    def produtores_rurais(self):
        df = pd.read_csv(_PRODUTORES_RURAIS_PATH, sep=";")

        return df


class Session:

    def __init__(self, user_id: int, full_name: str,
                 email: str, permission_level: int) -> None:

        self.user_id = user_id
        self.full_name = full_name
        self.email = email
        self.permission_level = permission_level
        self.active = False
