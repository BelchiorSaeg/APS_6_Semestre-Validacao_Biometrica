# -*- coding: utf-8 -*-

import bcrypt

from exceptions import DataBaseError, LoginError, ExceptionCodes
from data_manager import Session
from fingerprint_processing import Fingerprint

DATABASE = None


class LoginHandler:
    """
    | > Gerenciador do processo de login
    """

    def __init__(self) -> None:
        self._session = None
        self._valid_login = False
        self._valid_fingerprint = False
        self._fingerprint = None

    def validate_login(self, user_email: str, password_text: str) -> None:

        database = DATABASE
        error_code = None

        # E-mail vazio
        if not user_email:
            error_code = ExceptionCodes.LoginError.NO_USER

        # Senha vazia
        elif not password_text:
            error_code = ExceptionCodes.LoginError.NO_PASSWORD

        if error_code is not None:
            raise LoginError(error_code)

        try:
            passwords = database.get_user_passwords(user_email)
            password_hash, password_biometry = passwords

        except DataBaseError as exc:
            error_code = exc.args[0]

        # Usuario e, ou senha invalidos
            if error_code == ExceptionCodes.DataBaseError.NO_DATA_FOUND:
                error_code = ExceptionCodes.LoginError.INVALID_USER_OR_PASSWORD

        # Erro desconhecido
            else:
                error_code = ExceptionCodes.UNDEFINED_ERROR

        if error_code is not None:
            raise LoginError(error_code)

        # Senha Invalida
        if not bcrypt.checkpw((user_email + password_text).encode(),
                              bytes.fromhex(password_hash)):

            error_code = ExceptionCodes.LoginError.INVALID_USER_OR_PASSWORD

        if error_code:
            raise LoginError(error_code)

        self._session = self._create_session(user_email)
        self._valid_login = True
        self._fingerprint = password_biometry

    def validate_fingerprint(self, fingerprint: bytes,
                             force_validation: bool = False) -> None:

        # ignora a verificacao da digital e forca a validacao do usuario
        if force_validation:
            self._session.active = True
            return

        # Login ainda nao foi validado
        if not self._valid_login:
            error_code = ExceptionCodes.LoginError.LOGIN_NOT_VALIDATE
            raise LoginError(error_code)

        # Usuario nao possui digital cadastrada
        if self._fingerprint is None:
            error_code = ExceptionCodes.LoginError.UNREGISTERED_FINGERPRINT
            raise LoginError(error_code)

        fingerprint = Fingerprint.process_image(fingerprint)
        match_level = Fingerprint.match_level(self._fingerprint, fingerprint)

        # Digital nao teve o minimo de compatibilidade desejada
        if match_level < 0.005:
            error_code = ExceptionCodes.LoginError.INVALID_FINGERPRINT
            raise LoginError(error_code)

        self._valid_fingerprint = True
        self._session.active = True

    @property
    def session(self) -> Session:
        return self._session

    @staticmethod
    def _create_session(user_email: str) -> Session:
        args = DATABASE.get_user_data(user_email)

        return Session(*args)
