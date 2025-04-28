#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pigpio.h>   // Para controlar el GPIO
#include <curl/curl.h> // Para enviar HTTP requests

// Simulador de lectura RFID
char* leer_rfid() {
    // En la práctica acá iría el código real para leer el RC522 usando SPI y pigpio
    // Por ahora devolvemos un UID simulado
    return "04A1B2C3D4";
}

// Función para enviar el UID al backend y recibir la respuesta
int enviar_uid_al_backend(const char* uid, char* respuesta_servidor, size_t tamano_respuesta) {
    CURL *curl;
    CURLcode res;
    int exito = 0;

    struct curl_slist *headers = NULL;
    char json_data[256];

    snprintf(json_data, sizeof(json_data), "{\"uid\":\"%s\"}", uid);

    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, "http://192.168.0.100:8080/api/rfid"); // Cambia la IP/puerto
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_data);

        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        // Función para capturar respuesta
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, 
            +[](void *contents, size_t size, size_t nmemb, void *userp) -> size_t {
                size_t total_size = size * nmemb;
                strncat((char*)userp, (char*)contents, total_size);
                return total_size;
            });
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, respuesta_servidor);

        res = curl_easy_perform(curl);

        if(res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() falló: %s\n", curl_easy_strerror(res));
            exito = -1;
        } else {
            exito = 0;
        }

        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    }

    return exito;
}

int main() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "No se pudo inicializar pigpio\n");
        return 1;
    }

    printf("Inicializando módulo RFID...\n");

    while (1) {
        printf("\nEsperando tarjeta...\n");

        char* uid = leer_rfid();
        printf("UID detectado: %s\n", uid);

        char respuesta[512] = {0};

        if (enviar_uid_al_backend(uid, respuesta, sizeof(respuesta)) == 0) {
            printf("Respuesta del servidor: %s\n", respuesta);

            // Aquí podrías actualizar una GUI en lugar de printf
            if (strstr(respuesta, "PERMITIDO") != NULL) {
                printf("ACCESO PERMITIDO\n");
                // Mostrar pantalla verde, por ejemplo
            } else {
                printf("ACCESO DENEGADO\n");
                // Mostrar pantalla roja, por ejemplo
            }
        } else {
            printf("Error al comunicarse con el servidor.\n");
        }

        gpioDelay(5000000); // Esperar 5 segundos antes de leer de nuevo
    }

    gpioTerminate();
    return 0;
}