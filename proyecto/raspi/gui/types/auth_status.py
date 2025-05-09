from enum import Enum

class AuthStatus(Enum):
    NO_CARD = "no_card"
    UNAUTHORIZED = "unauthorized"
    AUTHORIZED = "authorized"