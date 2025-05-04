import requests
from gui.api.services.rfid_reader import RFIDReader
from gui.api.models.users import User

from gui.api.constants import BASE_URL

class AuthService:
    def __init__(self, api_base_url=BASE_URL):
        self.api_base_url = api_base_url
        self.reader = RFIDReader()

    def authenticate_user(self):
        """Autentica un usuario via RFID."""
        try:
            card_id = self.reader.read_card()
            response = requests.get(
                f"{self.api_base_url}/users/external-id/{card_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                return User(
                    username=data.get("username"),
                    surname=data.get("surname"),
                    balance=data.get("balance", 0.0),
                    card_id=card_id
                )
                
            return None
            
        except requests.RequestException as e:
            print(f"Error de conexión: {e}")
            return None