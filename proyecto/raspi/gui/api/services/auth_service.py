# api_service.py
import requests
from gui.api.models.users import User
from gui.api.constants import BASE_URL


class AuthService:
    def __init__(self, api_base_url=BASE_URL):
        self.api_base_url = api_base_url

    def authenticate_user(self, external_id):
        """Autentica un usuario en la API usando el external_id."""
        try:
            response = requests.get(
                f"{self.api_base_url}/users/external-id/{external_id.strip()}"
            )

            if response.status_code == 200:
                data = response.json()
                return User(
                    username=data.get("username"),
                    surname=data.get("surname"),
                    balance=data.get("balance", 0.0),
                    external_id=external_id.strip(),
                )
            return None

        except requests.RequestException as e:
            print(f"Error de conexión: {e}")
            return None


# import mmap
# import os
# import requests
# import posix_ipc

# from gui.api.models.users import User
# from gui.api.constants import BASE_URL
# from gui.constants import SHM_NAME, SHM_SIZE

# SEM_NAME = "/rfid_sem"  # Mismo nombre que en el lector


# class AuthService:
#     def __init__(self, api_base_url=BASE_URL):
#         self.api_base_url = api_base_url
#         self.shm_fd = None
#         self.shm = None
#         self.sem = posix_ipc.Semaphore(SEM_NAME)  # Obtener el semáforo
#         self._init_shared_memory()

#     def _init_shared_memory(self):
#         try:
#             self.shm_fd = os.open(f"/dev/shm{SHM_NAME}", os.O_RDONLY | os.O_RDWR)

#             # Validación de tamaño correcto
#             actual_size = os.fstat(self.shm_fd).st_size
#             if actual_size < SHM_SIZE * 2:
#                 os.ftruncate(self.shm_fd, SHM_SIZE * 2)

#             self.shm = mmap.mmap(
#                 self.shm_fd,
#                 SHM_SIZE * 2,
#                 mmap.MAP_SHARED,
#                 mmap.PROT_READ | mmap.PROT_WRITE,
#             )
#         except Exception as e:
#             print(f"Error inicializando memoria compartida: {e}")
#             self.shm = None

#     def read_card(self):
#         if not self.shm:
#             return None

#         try:
#             self.sem.acquire()  # Bloqueo para lectura segura

#             self.shm.seek(0)
#             data = self.shm.read(SHM_SIZE).split(b"\x00")[0]
#             card_id = data.decode("utf-8") if data else None

#             # Siempre limpiar la memoria, incluso si no hay dato
#             self.shm.seek(0)
#             self.shm.write(b"\x00" * SHM_SIZE)

#             return card_id if card_id else None
#         except Exception as e:
#             print(f"Error leyendo tarjeta desde memoria: {e}")
#             return None
#         finally:
#             self.sem.release()  # Liberar semáforo

#     def authenticate_user(self):
#         try:
#             external_id = self.read_card()
#             if not external_id:
#                 return None

#             response = requests.get(
#                 f"{self.api_base_url}/users/external-id/{external_id.strip()}"
#             )

#             if response.status_code == 200:
#                 data = response.json()
#                 return User(
#                     username=data.get("username"),
#                     surname=data.get("surname"),
#                     balance=data.get("balance", 0.0),
#                     external_id=external_id.strip(),
#                 )
#             return None

#         except requests.RequestException as e:
#             print(f"Error de conexión: {e}")
#             return None

#     def __del__(self):
#         if self.shm:
#             self.shm.close()
#         if self.shm_fd:
#             os.close(self.shm_fd)
#         if self.sem:
#             self.sem.close()


# import requests
# import mmap
# import os

# from gui.api.models.users import User
# from gui.api.constants import BASE_URL
# from gui.constants import SHM_NAME, SHM_SIZE


# class AuthService:
#     def __init__(self, api_base_url=BASE_URL):
#         self.api_base_url = api_base_url
#         self.shm_fd = None
#         self.shm = None
#         self._init_shared_memory()

#     def _init_shared_memory(self):
#         """Inicializa el acceso a la memoria compartida"""
#         try:
#             self.shm_fd = os.open(f"/dev/shm{SHM_NAME}", os.O_RDONLY)
#             self.shm = mmap.mmap(self.shm_fd, SHM_SIZE, mmap.MAP_SHARED, mmap.PROT_READ)
#         except Exception as e:
#             print(f"Error inicializando memoria compartida: {e}")
#             self.shm = None

#     def read_card(self):
#         """Lee el ID de la tarjeta desde memoria compartida"""
#         if not self.shm:
#             return None

#         try:
#             self.shm.seek(0)
#             data = self.shm.read(SHM_SIZE).split(b"\x00")[0]
#             return data.decode("utf-8") if data else None
#         except Exception as e:
#             print(f"Error leyendo tarjeta desde memoria: {e}")
#             return None

#     def authenticate_user(self):
#         """Autentica un usuario leyendo el RFID desde memoria compartida"""
#         try:
#             external_id = self.read_card()

#             if not external_id:
#                 return None

#             response = requests.get(
#                 f"{self.api_base_url}/users/external-id/{external_id.strip()}"
#             )

#             if response.status_code == 200:
#                 data = response.json()
#                 return User(
#                     username=data.get("username"),
#                     surname=data.get("surname"),
#                     balance=data.get("balance", 0.0),
#                     external_id=external_id.strip(),
#                 )

#             return None

#         except requests.RequestException as e:
#             print(f"Error de conexión: {e}")
#             return None
#         finally:
#             # Opcional: limpiar memoria aquí si es necesario
#             pass

#     def __del__(self):
#         """Libera recursos al destruir la instancia"""
#         if self.shm:
#             self.shm.close()
#         if self.shm_fd:
#             os.close(self.shm_fd)
