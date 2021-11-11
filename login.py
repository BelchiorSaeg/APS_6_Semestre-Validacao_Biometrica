# -*- coding: utf-8 -*-

from exceptions import DataBaseError, LoginError, ExceptionCodes
from data_manager import Session
from fingerprint_processing import Fingerprint

DATABASE = None


class LoginHandler:

    def __init__(self) -> None:
        self._session = None
        self._valid_login = False
        self._valid_fingerprint = False
        self._fingerprint = None

    def validate_login(self, user_email: str, password_text: str) -> None:

        db = DATABASE
        error_code = None

        if not user_email:
            error_code = ExceptionCodes.LoginError.NO_USER

        elif not password_text:
            error_code = ExceptionCodes.LoginError.NO_PASSWORD

        if error_code:
            raise LoginError(error_code)

        try:
            passwords = db.get_user_passwords(user_email)

        except DataBaseError as exc:
            error_code = exc.args[0]

            if error_code == ExceptionCodes.DataBaseError.NO_DATA_FOUND:
                error_code = ExceptionCodes.LoginError.INVALID_USER_OR_PASSWORD
            else:
                error_code = ExceptionCodes.UNDEFINED_ERROR

            raise LoginError(error_code)

        if not user_email:
            error_code = ExceptionCodes.LoginError.NO_USER

        elif not password_text:
            error_code = ExceptionCodes.LoginError.NO_PASSWORD

        elif password_text != passwords[0]:
            error_code = ExceptionCodes.LoginError.INVALID_USER_OR_PASSWORD

        if error_code:
            raise LoginError(error_code)

        self._session = self._create_session(user_email)
        self._valid_login = True
        self._fingerprint = passwords[1]

    def validate_fingerprint(self, fingerprint) -> None:
        """
        EM CONSTRUÇÃO!!!!!!!
        """
        error_code = None

        if not self._valid_login:
            error_code = ExceptionCodes.LoginError.LOGIN_NOT_VALIDATE
            raise LoginError(error_code)

        fingerprint = Fingerprint.process_image(fingerprint)
        match_level = Fingerprint.match_level(self._fingerprint, fingerprint)

        if match_level < 0.9:
            error_code = ExceptionCodes.LoginError.INVALID_FINGERPRINT
            raise LoginError(error_code)

        self._valid_fingerprint = True
        self._session.active = True

    @property
    def session(self):
        return self._session

    @staticmethod
    def _create_session(user_email: str):
        args = DATABASE.get_user_data(user_email)

        return Session(*args)
