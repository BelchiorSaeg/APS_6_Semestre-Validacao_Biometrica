# -*- coding: utf-8 -*-

import sqlite3
import bcrypt
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
        pass

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
        connection.close()

    def connect(self) -> None:
        """
        |> Inicia a conexao com banco de dados.
        |> conexao atribuida a propriedade 'self.connection'
        """
        try:
            with open(_DATABASE_PATH):
                pass

        except FileNotFoundError:
            self._create_database()

        self._connection = sqlite3.connect(_DATABASE_PATH)

    def close(self) -> None:
        """
        | > Fecha a conexao com o banco de dados.
        """
        self.connection.close()

    def get_user_passwords(self, email: str) -> list:
        """
        | Returno
        | -------
        | type: list
        |
        | > (password_hash, password_biometry)
        |
        """
        querry = f"""
SELECT PASSWORD_HASH, PASSWORD_BIOMETRY FROM USERS U
WHERE U.EMAIL = '{email}'
"""
        cursor = self.connection.cursor()

        try:
            passwords = list(cursor.execute(querry))[0]

        except IndexError:
            error_code = ExceptionCodes.DataBaseError.NO_DATA_FOUND

            raise DataBaseError(error_code, "No data Found")

        finally:
            cursor.close()

        return passwords

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

    def register_user(self, full_name: str, email: str, password_text: str,
                      password_biometry, permission_level: int):

        password = (email + password_text).encode()
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).hex()

        querry = f"""
INSERT INTO USERS (FULL_NAME, EMAIL, PASSWORD_HASH, PASSWORD_BIOMETRY,
                   PERMISSION_LEVEL) VALUES

    ('{full_name}', '{email}', '{password_hash}', {password_biometry},
     {permission_level})
"""

        cursor = self.connection.cursor()
        cursor.execute(querry)
        self.connection.commit()
        cursor.close()

    @property
    def connection(self):
        error_code = None

        try:
            cursor = self._connection.cursor()
            cursor.close()

        except AttributeError:
            error_code = ExceptionCodes.DataBaseError.DATABASE_NOT_CONNECTED

        except sqlite3.ProgrammingError as exc:
            if exc.args[0] != "Cannot operate on a closed database.":
                raise sqlite3.ProgrammingError(*exc.args)

            error_code = ExceptionCodes.DataBaseError.DATABASE_NOT_CONNECTED

        if error_code:
            raise DataBaseError(error_code)

        return self._connection

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


class User:

    def __init__(self, full_name: str, email: str, password_text: str,
                 password_biometry, permission_level: int):

        password = (email + password_text).encode()
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt())

        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.password_biometry = password_biometry
        self.permission_level = permission_level
