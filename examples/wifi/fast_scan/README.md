| Plataformas Soportadas | ESP32 | ESP32-C2 | ESP32-C3 | ESP32-C5 | ESP32-C6 | ESP32-C61 | ESP32-S2 | ESP32-S3 |
| ---------------------- | ----- | -------- | -------- | -------- | -------- | --------- | -------- | -------- |

# Ejemplo de Escaneo Rápido Wi-Fi

(Consulte el archivo README.md en el directorio de nivel superior 'examples' para obtener más información sobre los ejemplos).

Este ejemplo muestra cómo utilizar la funcionalidad de escaneo del controlador Wi-Fi de ESP para conectarse a un punto de acceso (AP).

Se admiten dos métodos de escaneo: escaneo rápido y escaneo de todos los canales.

* `escaneo rápido`: en este modo, el escaneo finaliza inmediatamente después de detectar un AP coincidente, incluso si no se han escaneado todos los canales. Puede establecer umbrales para la intensidad de la señal, así como seleccionar los modos de autenticación deseados proporcionados por los AP. El controlador Wi-Fi ignorará los AP que no cumplan con los criterios mencionados.

* `escaneo de todos los canales`: el escaneo finalizará solo después de escanear todos los canales; el controlador Wi-Fi almacenará 4 de los AP que coincidan completamente. Los métodos de clasificación para los AP incluyen rssi y authmode. Después del escaneo, el controlador Wi-Fi selecciona el AP que mejor se adapta según la clasificación.

Después del escaneo, el controlador Wi-Fi intentará conectarse. Debido a que necesita asignar memoria dinámica valiosa para almacenar los AP coincidentes y, en la mayoría de los casos, conectarse al AP con la recepción más fuerte, no necesita registrar todos los AP coincidentes. El número de coincidencias almacenadas está limitado a 4 para limitar el uso de memoria dinámica. Entre las 4 coincidencias, se permite que los AP lleven el mismo nombre SSID y todos los modos de autenticación posibles: abierto, WEP, WPA y WPA2.

## Cómo usar el ejemplo

Antes de la configuración y compilación del proyecto, asegúrese de establecer el chip objetivo correcto usando `idf.py set-target <chip_name>`.

### Hardware Requerido

* Una placa de desarrollo con SoC ESP32/ESP32-S2/ESP32-C3 (por ejemplo, ESP32-DevKitC, ESP-WROVER-KIT, etc.)
* Un cable USB para alimentación y programación

### Configurar el proyecto

Abra el menú de configuración del proyecto (`idf.py menuconfig`).

En el menú `Example Configuration`:

* Use `WiFi SSID` para establecer el SSID.
* Use `WiFi Password` para establecer la contraseña.

Opcional: Si es necesario, cambie las otras opciones según sus requisitos.

### Compilar y Cargar

Compile el proyecto y cárguelo en la placa, luego ejecute la herramienta de monitoreo para ver la salida serial:

Ejecute `idf.py -p PORT flash monitor` para compilar, cargar y monitorear el proyecto.

(Para salir del monitor serial, escriba ``Ctrl-]``).

Consulte la Guía de Inicio para todos los pasos para configurar y usar ESP-IDF para construir proyectos.

* [Guía de Inicio de ESP-IDF en ESP32](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html)
* [Guía de Inicio de ESP-IDF en ESP32-S2](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s2/get-started/index.html)
* [Guía de Inicio de ESP-IDF en ESP32-C3](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/get-started/index.html)

## Salida del Ejemplo

Al ejecutar el ejemplo, verá el siguiente registro:

```
I (616) wifi:wifi firmware version: 6bff005
I (616) wifi:wifi certification version: v7.0
I (616) wifi:config NVS flash: enabled
I (616) wifi:config nano formatting: disabled
I (626) wifi:Init data frame dynamic rx buffer num: 32
I (626) wifi:Init management frame dynamic rx buffer num: 32
I (636) wifi:Init management short buffer num: 32
I (636) wifi:Init dynamic tx buffer num: 32
I (646) wifi:Init static rx buffer size: 1600
I (646) wifi:Init static rx buffer num: 10
I (646) wifi:Init dynamic rx buffer num: 32
I (656) wifi_init: rx ba win: 6
I (656) wifi_init: tcpip mbox: 32
I (666) wifi_init: udp mbox: 6
I (666) wifi_init: tcp mbox: 6
I (666) wifi_init: tcp tx win: 5744
I (676) wifi_init: tcp rx win: 5744
I (676) wifi_init: tcp mss: 1440
I (686) wifi_init: WiFi IRAM OP enabled
I (686) wifi_init: WiFi RX IRAM OP enabled
I (696) phy_init: phy_version 4660,0162888,Dec 23 2020
I (796) wifi:mode : sta (xx:xx:xx:xx:xx:xx)
I (796) wifi:enable tsf
I (806) wifi:new:<8,1>, old:<1,0>, ap:<255,255>, sta:<8,1>, prof:1
I (806) wifi:state: init -> auth (b0)
I (826) wifi:state: auth -> assoc (0)
I (836) wifi:state: assoc -> run (10)
I (876) wifi:connected with SSID, aid = 1, channel 8, 40U, bssid = xx:xx:xx:xx:xx:xx
I (876) wifi:security: WPA2-PSK, phy: bgn, rssi: -56
I (886) wifi:pm start, type: 1

I (966) wifi:AP's beacon interval = 102400 us, DTIM period = 1
W (1106) wifi:<ba-add>idx:0 (ifx:0, xx:xx:xx:xx:xx:xx), tid:0, ssn:0, winSize:64
I (2086) scan: got ip:192.168.68.110
I (2086) esp_netif_handlers: sta ip: 192.168.68.110, mask: 255.255.255.0, gw: 192.168.68.1

```

## Solución de problemas

Para cualquier consulta técnica, por favor abra un [issue](https://github.com/espressif/esp-idf/issues) en GitHub. Nos pondremos en contacto con usted pronto.
