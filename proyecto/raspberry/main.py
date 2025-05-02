#!/usr/bin/env python3

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time

# Inicializar el lector RFID
reader = SimpleMFRC522()

try:
    print("Esperando que el usuario escanee su tarjeta RFID...")

    id, text = reader.read()
    external_id = str(id)  # Convertir a string para la URL
    print(f"ID escaneado: {external_id}")

    # URL del servidor con el external_id
    url = f"http://192.168.1.4/api/v1/users/external-id/{external_id}"

    # Hacer la solicitud GET
    response = requests.get(url)

    if response.status_code == 200:
        user = response.json()
        nombre = user.get("username", "desconocido")
        apellido = user.get("surname", "")
        saldo = user.get("balance", 0.0)
        print(f"Hola {nombre} {apellido}, tenés ${saldo:.2f} de saldo.")
    elif response.status_code == 404:
        print("Usuario no encontrado.")
    else:
        print(f"Error al consultar el servidor: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")

finally:
    GPIO.cleanup()
