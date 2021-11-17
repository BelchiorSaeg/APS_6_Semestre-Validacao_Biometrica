# -*- coding: utf-8 -*-

import sqlite3
import bcrypt
import pandas as pd
from exceptions import DataBaseError, ExceptionCodes


_DATABASE_PATH = "data\\user_data\\database.db"
_CREATION_CODE_PATH = "data\\user_data\\database_creation_code.sql"
_USER_DATA_PATH = "data\\user_data\\user_data.txt"
_AGROTOXICOS_PATH = "data\\agrotoxicos\\agrofitprodutosformulados.csv"
_INFORMACOES_FISCAIS_PATH = "data\\informacoes_fiscais\\mapa_despesas.csv"
_INFORMACOES_FISCAIS_2_PATH = "data\\informacoes_fiscais\\mapa_receitas.csv"
_PRODUTORES_RURAIS_PATH = "data\\produtores_rurais\\cnpomapa30092019.csv"


class DataBase:

    def __init__(self) -> None:
        self._connection = None

    def _create_database(self) -> None:

        with open(_CREATION_CODE_PATH, encoding="UTF-8") as file:
            creation_code = file.read()

        with open(_USER_DATA_PATH, encoding="UTF-8") as file:
            user_data = file.read().splitlines()
            user_data = [line.split(', ') for line in user_data]

        # reseta o arquivo caso exista.
        with open(_DATABASE_PATH, 'w', encoding="UTF-8") as file:
            pass

        connection = sqlite3.connect(_DATABASE_PATH)

        cursor = connection.cursor()

        cursor.execute(creation_code)
        connection.commit()
        cursor.close()
        connection.close()

        self.connect()

        for data in user_data:
            print('user ', data[0], '...', sep="")
            self.register_user(data[1], data[2], data[3], data[4],
                               int(data[5]))

        self.close()

    def _validate_database(self) -> None:
        error_code = None

        if self._connection is None:
            error_code = ExceptionCodes.DataBaseError.DATABASE_NOT_CONNECTED

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

        if error_code is not None:
            raise DataBaseError(error_code)

    def _validate_data(self, email: str) -> None:
        querry = """
            SELECT
                *
            FROM
                USERS
            WHERE
                EMAIL = ?
        """
        error_code = None

        self._validate_database()

        cursor = self.connection.cursor()
        cursor.execute(querry, (email, ))

        if cursor.fetchone() is None:
            error_code = ExceptionCodes.DataBaseError.NO_DATA_FOUND

        if error_code is not None:
            raise DataBaseError(error_code)

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
        querry = """
            SELECT
                PASSWORD_HASH, PASSWORD_BIOMETRY
            FROM
                USERS U
            WHERE
                U.EMAIL = ?"""
        self._validate_data(email)

        cursor = self.connection.cursor()
        cursor.execute(querry, (email, ))
        passwords = cursor.fetchone()
        cursor.close()

        return passwords

    def get_user_data(self, email: str) -> str:
        querry = """
            SELECT
                ID, FULL_NAME, EMAIL, PERMISSION_LEVEL
            FROM
                USERS U
            WHERE
                U.EMAIL = ?"""

        self._validate_data(email)

        cursor = self.connection.cursor()

        cursor.execute(querry, (email, ))
        user_data = cursor.fetchone()
        cursor.close()

        return user_data

    def register_user(self, full_name: str, email: str,
                      password_text: str,
                      password_biometry: bytes,
                      permission_level: int) -> None:

        password = (email + password_text).encode()
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).hex()

        querry = """
            INSERT INTO
                USERS (FULL_NAME, EMAIL, PASSWORD_HASH, PASSWORD_BIOMETRY,
                       PERMISSION_LEVEL)
            VALUES
                (?, ?, ?, ?, ?)
"""

        if password_biometry is None:
            password_biometry = 'NULL'

        cursor = self.connection.cursor()

        cursor.execute(querry, (full_name, email, password_hash,
                                password_biometry, permission_level))

        self.connection.commit()
        cursor.close()

    def register_user_fingerprint(self, user_email: str,
                                  fingerprint: bytes) -> None:
        querry = """
            UPDATE
                USERS
            SET
                PASSWORD_BIOMETRY = ?
            WHERE
                EMAIL = ?
        """
        self._validate_data(user_email)

        cursor = self._connection.cursor()
        cursor.execute(querry, (fingerprint, user_email))
        cursor.close()
        self.connection.commit()

    @property
    def connection(self) -> sqlite3.Connection:
        self._validate_database()

        return self._connection

    @property
    def agrotoxicos(self) -> pd.DataFrame:
        df = pd.read_csv(_AGROTOXICOS_PATH, sep=";")

        return df

    @property
    def informacoes_fiscais(self) -> pd.DataFrame:
        df_1 = pd.read_csv(_INFORMACOES_FISCAIS_PATH, sep=";")
        df_2 = pd.read_csv(_INFORMACOES_FISCAIS_2_PATH, sep=";")

        return df_1, df_2

    @property
    def produtores_rurais(self) -> pd.DataFrame:
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
