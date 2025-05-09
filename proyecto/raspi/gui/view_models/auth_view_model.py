# auth_service.py
import mmap
import os
import posix_ipc

from gui.api.services.auth_service import AuthService
from gui.api.constants import BASE_URL
from gui.types.auth_status import AuthStatus
from gui.constants import SHM_NAME, SHM_SIZE, SEM_NAME


class AuthViewModel:
    def __init__(self, api_base_url=BASE_URL):
        self.api_base_url = api_base_url
        self.shm_fd = None
        self.shm = None
        self.sem = posix_ipc.Semaphore(SEM_NAME)  # Obtener el semáforo
        self.api_service = AuthService(
            api_base_url
        )  # Inicializar el servicio de la API
        self._init_shared_memory()

    def _init_shared_memory(self):
        try:
            self.shm_fd = os.open(f"/dev/shm{SHM_NAME}", os.O_RDONLY | os.O_RDWR)

            # Validación de tamaño correcto
            actual_size = os.fstat(self.shm_fd).st_size
            if actual_size < SHM_SIZE * 2:
                os.ftruncate(self.shm_fd, SHM_SIZE * 2)

            self.shm = mmap.mmap(
                self.shm_fd,
                SHM_SIZE * 2,
                mmap.MAP_SHARED,
                mmap.PROT_READ | mmap.PROT_WRITE,
            )
        except Exception as e:
            print(f"Error inicializando memoria compartida: {e}")
            self.shm = None

    def read_card(self):
        """Lee el ID de la tarjeta desde la memoria compartida."""
        if not self.shm:
            return None

        try:
            self.sem.acquire()  # Bloqueo para lectura segura

            self.shm.seek(0)
            data = self.shm.read(SHM_SIZE).split(b"\x00")[0]
            card_id = data.decode("utf-8") if data else None

            # Siempre limpiar la memoria, incluso si no hay dato
            self.shm.seek(0)
            self.shm.write(b"\x00" * SHM_SIZE)
            print(f"ID de tarjeta leído: {card_id}")
            return card_id if card_id else None
        except Exception as e:
            print(f"Error leyendo tarjeta desde memoria: {e}")
            return None
        finally:
            self.sem.release()  # Liberar semáforo

    # def authenticate_user(self):
    #     """Autentica un usuario usando el ID de la tarjeta RFID."""
    #     try:
    #         external_id = self.read_card()
    #         if not external_id:
    #             print("No se pudo leer el ID de la tarjeta.")
    #             return None

    #         # Llamar al servicio de la API para autenticar al usuario con el external_id
    #         user = self.api_service.authenticate_user(external_id)
    #         return user

    #     except Exception as e:
    #         print(f"Error autenticando usuario: {e}")
    #         return None

    def authenticate_user(self):
        """Autentica un usuario usando el ID de la tarjeta RFID."""
        try:
            external_id = self.read_card()
            if not external_id:
                return AuthStatus.NO_CARD, None

            user = self.api_service.authenticate_user(external_id)
            if user:
                return AuthStatus.AUTHORIZED, user
            else:
                return AuthStatus.UNAUTHORIZED, None

        except Exception as e:
            print(f"Error autenticando usuario: {e}")
            return AuthStatus.NO_CARD, None  # Tratar error como sin tarjeta

    def __del__(self):
        if self.shm:
            self.shm.close()
        if self.shm_fd:
            os.close(self.shm_fd)
        if self.sem:
            self.sem.close()


# # auth_service.py
# import mmap
# import os
# import posix_ipc

# from gui.api.services.auth_service import AuthService
# from gui.api.constants import BASE_URL
# from gui.constants import SHM_NAME, SHM_SIZE

# SEM_NAME = "/rfid_sem"  # Mismo nombre que en el lector


# class AuthViewModel:
#     def __init__(self, api_base_url=BASE_URL):
#         self.api_base_url = api_base_url
#         self.shm_fd = None
#         self.shm = None
#         self.sem = posix_ipc.Semaphore(SEM_NAME)  # Obtener el semáforo
#         self.api_service = AuthService(
#             api_base_url
#         )  # Inicializar el servicio de la API
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

#             print(f"ID de tarjeta leído: {external_id}")
#             # Utilizar el servicio de la API para autenticar al usuario
#             user = self.api_service.authenticate_user(external_id)
#             return user

#         except Exception as e:
#             print(f"Error autenticando usuario: {e}")
#             return None

#     def __del__(self):
#         if self.shm:
#             self.shm.close()
#         if self.shm_fd:
#             os.close(self.shm_fd)
#         if self.sem:
#             self.sem.close()
