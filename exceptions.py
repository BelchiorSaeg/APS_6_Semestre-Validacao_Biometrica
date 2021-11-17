# -*- coding: utf-8 -*-

class _CustomException(Exception):

    def __init__(self, error_code, input_message=None, *args):
        self.error_code = error_code
        self.error_name = get_exception_name(error_code)

        message = f"Error '{self.error_name}' with code '{self.error_code}'"

        if input_message:
            message += " - " + input_message

        super().__init__(error_code, message, *args)


class LoginError(_CustomException):
    pass


class DataBaseError(_CustomException):
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

        # Tentativa de validar a digital sem logar o usuario com a senha
        LOGIN_NOT_VALIDATE = "1.1.4"

        # Tentativa de validacao de usuario sem digital cadastrada
        UNREGISTERED_FINGERPRINT = "1.1.5"

    class DataBaseError:
        """
        | Erros lancados pela classe DataBaseError.
        """

        NO_DATA_FOUND = "1.2.0"
        DATABASE_NOT_CONNECTED = "1.2.1"


def get_exception_name(code: str) -> str:
    return _EXCEPTION_NAMES[code]


def _get_exception_names() -> dict:
    error_names = {}

    for item in dir(ExceptionCodes):

        class_origin = ExceptionCodes

        if item[0] != "_":

            if item.isupper():
                error_code = getattr(class_origin, item)
                error_names[error_code] = item

            else:
                class_origin = getattr(class_origin, item)

                for sub_item in dir(class_origin):

                    if sub_item[:2] != "__":

                        if sub_item.isupper():
                            error_code = getattr(class_origin, sub_item)
                            error_names[error_code] = sub_item

    return error_names


_EXCEPTION_NAMES = _get_exception_names()
