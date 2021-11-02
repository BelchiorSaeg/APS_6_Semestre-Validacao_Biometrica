# -*- coding: utf-8 -*-

class LoginError(Exception):
    pass


class DataBaseError(Exception):
    pass


class ExceptionCodes:
    """
    | Armazena os codigos dos erros lancados no algoritmo.
    """

    UNDEFINED_ERROR = "0.0.0"

    class LoginError:
        """
        | Erros lancados pela classe LoginError.
        """

        NO_PASSWORD = "1.1.0"
        NO_USER = "1.1.1"
        INVALID_USER_OR_PASSWORD = "1.1.2"
        INVALID_FINGERPRINT = "1.1.3"

    class DataBaseError:
        """
        | Erros lancados pela classe DataBaseError.
        """

        NO_DATA_FOUND = "1.2.0"
        DATABASE_NOT_CONNECTED = "1.2.1"
