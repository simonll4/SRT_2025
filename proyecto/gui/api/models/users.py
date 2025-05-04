from dataclasses import dataclass

@dataclass
class User:
    username: str
    surname: str
    balance: float
    card_id: str