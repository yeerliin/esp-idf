# Ejemplo OTA

---
**NOTAS**

- Esta guía se aplica a todos los ejemplos de actualización OTA
- "ESP-Dev-Board" se refiere a cualquier placa de desarrollo con chipset Espressif (p.ej., ESP32/ESP32-S2/ESP32-C3, etc.)
---


## Descripción general

Una aplicación en "ESP-Dev-Board" puede ser actualizada en tiempo de ejecución mediante la descarga de una nueva imagen a través de Wi-Fi o Ethernet y grabándola en una partición OTA. El ESP-IDF ofrece dos métodos para realizar actualizaciones Over The Air (OTA):

- Utilizando las APIs nativas proporcionadas por el componente [`app_update`](../../../components/app_update).
- Utilizando APIs simplificadas proporcionadas por el componente [`esp_https_ota`](../../../components/esp_https_ota), que proporciona funcionalidad para actualizar a través de HTTPS.

El uso de la API nativa se demuestra en el directorio `native_ota_example`, mientras que la API proporcionada por el componente `esp_https_ota` se demuestra en `simple_ota_example`, `advanced_https_ota` y `partitions_ota`.

El ejemplo `partitions_ota` demuestra el proceso de actualización OTA para cualquier tipo de partición (otros ejemplos solo admiten actualizaciones seguras para la aplicación):
- Aplicación (actualización segura).
- Bootloader (actualización no segura).
- Tabla de particiones (actualización no segura).
- Otras particiones de datos (actualización no segura).

**Nota:** Las **actualizaciones seguras** están diseñadas para garantizar que el dispositivo permanezca operativo incluso si el proceso de actualización se interrumpe. Esto significa que el dispositivo puede seguir arrancando y funcionando normalmente, minimizando el riesgo de fallos. Por otro lado, las **actualizaciones no seguras** conllevan un riesgo significativo. Si la actualización se interrumpe durante la copia a la partición de destino, puede provocar fallos críticos, potencialmente haciendo que el dispositivo quede inoperativo e irrecuperable. Dado que la copia final se realiza en el lado del usuario, este riesgo puede minimizarse asegurando una alimentación estable y condiciones sin errores durante este tiempo.

Para obtener información sobre el componente `esp_https_ota`, consulte [ESP HTTPS OTA](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/esp_https_ota.html).

Para simplificar, los ejemplos de OTA utilizan una tabla de particiones predefinida creada al habilitar la opción `CONFIG_PARTITION_TABLE_TWO_OTA` en menuconfig, que admite tres particiones de aplicación: `factory`, `OTA_0` y `OTA_1`. Consulte [Tablas de Particiones](https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/partition-tables.html) para más información.

En el primer arranque, el bootloader cargará la imagen contenida en la partición `factory` (es decir, la imagen de ejemplo). Este firmware desencadena una actualización OTA. Descargará una nueva imagen desde un servidor HTTPS y la guardará en la partición `OTA_0`. A continuación, actualiza la partición `ota_data` para indicar qué aplicación debe arrancar después del próximo reinicio. Al reiniciar, el bootloader lee el contenido de la partición `ota_data` para determinar qué aplicación se selecciona para ejecutar.

El flujo de trabajo OTA se ilustra en el siguiente diagrama:

![Flujo de trabajo OTA](ota_workflow.png)

## Cómo usar los ejemplos

### Hardware Requerido

"ESP-Dev-Board" es necesario para ejecutar los ejemplos de OTA. Asegúrese de que Ethernet esté configurado correctamente si está probando OTA con Ethernet. Para más información sobre la configuración de Ethernet, consulte los [ejemplos](../../ethernet) de Ethernet.

### Configurar el proyecto

Abra el menú de configuración del proyecto (`idf.py menuconfig`).

En el menú `Example Connection Configuration`:

* Elija la interfaz de red en la opción `Connect using` según su placa. Actualmente se admiten tanto Wi-Fi como Ethernet
* Si se utiliza la interfaz Wi-Fi, proporcione el SSID y la contraseña Wi-Fi del AP al que desea conectarse
* Si utiliza la interfaz Ethernet, configure el modelo de PHY en la opción `Ethernet PHY Device`, p.ej. `IP101`

En el menú `Example Configuration`:

* Establezca la URL del firmware a descargar en la opción `Firmware Upgrade URL`. El formato debe ser `https://<dirección-ip-host>:<puerto-host>/<nombre-archivo-firmware>`, p.ej. `https://192.168.2.106:8070/hello_world.bin`
  * **Nota:** La parte del servidor de esta URL (p.ej. `192.168.2.106`) debe coincidir con el campo **CN** utilizado al [generar el certificado y la clave](#ejecutar-servidor-https)

### Compilar y Flashear

Ejecute `idf.py -p PORT flash monitor` para compilar y flashear el proyecto. Este comando verifica si la tabla de particiones contiene la partición `ota_data` y la restaura a un estado inicial. Esto permite que la aplicación recién cargada se ejecute desde la partición `factory`.

(Para salir del monitor serie, escriba ``Ctrl-]``.)

Consulte la [Guía de Inicio](https://docs.espressif.com/projects/esp-idf/en/latest/get-started/index.html) para todos los pasos necesarios para configurar y utilizar ESP-IDF para compilar proyectos.

## Salida del Ejemplo

### Configurar e iniciar el Servidor HTTPS

Después de una compilación exitosa, necesitamos crear un certificado autofirmado y ejecutar un servidor HTTPS simple de la siguiente manera:

![crear_certificado_autofirmado](https://dl.espressif.com/dl/esp-idf/docs/_static/ota_self_signature.gif)

* Entre en el directorio que contiene el/los artefacto/s de compilación del proyecto, que serán alojados por el servidor HTTPS, p.ej. `cd build`.
* Para crear un nuevo certificado y clave autofirmados, ejecute el comando `openssl req -x509 -newkey rsa:2048 -keyout ca_key.pem -out ca_cert.pem -days 365 -nodes`.
  * Cuando se le solicite el `Common Name (CN)`, introduzca el nombre del servidor al que se conectará la "ESP-Dev-Board". Cuando ejecute este ejemplo desde una máquina de desarrollo, probablemente sea la dirección IP. El cliente HTTPS verificará que el `CN` coincida con la dirección dada en la URL HTTPS.
* Este directorio debe contener el firmware (p.ej. `hello_world.bin`) que se utilizará en el proceso de actualización. Puede ser cualquier aplicación ESP-IDF válida, siempre que su nombre de archivo corresponda al nombre configurado usando `Firmware Upgrade URL` en menuconfig. La única diferencia con flashear un firmware a través de la interfaz serie es que el binario se flashea en la partición `factory`, mientras que las actualizaciones OTA utilizan una de las particiones OTA.


Puede iniciar el servidor utilizando cualquiera de los siguientes métodos: 

#### Servidor basado en Python

* Para iniciar un servidor HTTPS basado en Python usando [example_test_scipt](simple_ota_example/pytest_simple_ota.py), ejecute `pytest_simple_ota.py <BIN_DIR> <PORT> [CERT_DIR]`, donde:
    - `<BIN_DIR>` es un directorio que contiene el firmware (p.ej. `hello_world.bin`) que se utilizará en el proceso de actualización.`
    - `<PORT>` es el puerto del servidor, aquí `8070`
    - `[CERT_DIR]` es un argumento opcional que apunta a un directorio específico con el archivo de certificado y clave: `ca_cert.pem` y `ca_key.pem`.

Ejemplo de salida de consola:
``` bash
$ cd idf/examples/system/ota/simple_ota_example
$ python pytest_simple_ota.py build 8070
Starting HTTPS server at "https://:8070"
192.168.10.106 - - [02/Mar/2021 14:32:26] "GET /simple_ota.bin HTTP/1.1" 200 -
```
#### Servidor basado en OpenSSL

* Para iniciar un servidor HTTPS basado en OpenSSL, ejecute el comando `openssl s_server -WWW -key ca_key.pem -cert ca_cert.pem -port 8070`.

Ejemplo de salida de consola:
```bash
$ openssl s_server -WWW -key ca_key.pem -cert ca_cert.pem -port 8070
FILE:hello_world.bin
ACCEPT
```

* **Nota:** El servidor OpenSSL no puede manejar solicitudes HTTP parciales, por lo que no admite descargas parciales. Alternativamente, puede iniciar un servidor basado en Python usando [Servidor basado en Python](#Servidor-basado-en-Python)
* **Nota:** Asegúrese de que el acceso entrante al puerto *8070* no esté bloqueado por reglas de firewall.
* **Nota:** Los usuarios de Windows pueden encontrar problemas al ejecutar `openssl s_server -WWW`, debido a la traducción CR/LF y/o al cierre prematuro de la conexión
  (Algunas compilaciones de Windows de openssl traducen las secuencias CR/LF a LF en los archivos servidos, lo que lleva a imágenes corruptas recibidas por el cliente OTA; otras interpretan el carácter `0x1a`/`SUB` en un binario como una secuencia de escape, es decir, fin de archivo, y cierran la conexión prematuramente, lo que impide que el cliente OTA reciba una imagen completa).
  * Recomendamos usar el binario `openssl` incluido en `Git For Windows` del [instalador de herramientas ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/get-started/windows-setup.html):
  Abra el símbolo del sistema ESP-IDF y añada el binario openssl interno a su ruta: `set PATH=%LocalAppData%\Git\usr\bin;%PATH%` y ejecute el comando del servidor http de openssl como se indicó anteriormente.


### Flashear el Certificado a "ESP-Dev-Board"

Finalmente, copie el certificado generado al directorio `server_certs` contenido en el directorio de ejemplo para que pueda ser flasheado en su dispositivo junto con el firmware, p.ej. `cp ca_cert.pem ../server_certs/`.

```
cp ca_cert.pem /path/to/ota/example/server_certs/
```

### Flujo de trabajo interno del Ejemplo OTA

Después de arrancar, el firmware:

1. imprime "OTA example app_main start" en la consola
2. Se conecta a través de Ethernet o al AP utilizando el SSID y la contraseña proporcionados (caso Wi-Fi)
3. imprime "Starting OTA example task" en la consola
4. Se conecta al servidor HTTPS y descarga la nueva imagen
5. Escribe la imagen en la flash e instruye al bootloader para que arranque desde esta imagen después del próximo reinicio
6. Reinicia

Si desea volver a la aplicación `factory` después de la actualización (o a la primera partición OTA en caso de que la partición `factory` no exista), ejecute el comando `idf.py erase_otadata`. Esto restaura la partición `ota_data` a su estado inicial.

**Nota:** Esto asume que la tabla de particiones de este proyecto es la que está presente en el dispositivo.

## Soporte para Rollback

Esta característica le permite volver a un firmware anterior si la nueva imagen no es utilizable. La opción de menuconfig `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE` le permite rastrear el primer arranque de la aplicación (consulte el artículo ``Over The Air Updates (OTA)``).

El ``native_ota_example`` contiene código para demostrar cómo funciona un rollback. Para usarlo, habilite la opción `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE` en el submenú `Example Configuration` de menuconfig para establecer `Number of the GPIO input for diagnostic` para manipular el proceso de rollback.

Para activar un rollback, este GPIO debe estar en nivel bajo mientras se muestra el mensaje `Diagnostics (5 sec)...` durante el primer arranque.

Si el GPIO no está en nivel bajo, la aplicación se confirma como operable.

## Soporte para Versionado de Aplicaciones

El ``native_ota_example`` contiene código para demostrar cómo verificar la versión de la aplicación y evitar bucles infinitos de actualización de firmware. Solo se descargan aplicaciones más nuevas. La verificación de la versión se realiza después de recibir el primer paquete de imagen de firmware que contiene datos de versión. La versión de la aplicación se obtiene de uno de estos tres lugares:

1. Si la opción `CONFIG_APP_PROJECT_VER_FROM_CONFIG` está establecida, se utiliza el valor de `CONFIG_APP_PROJECT_VER`
2. De lo contrario, si la variable ``PROJECT_VER`` está establecida en el archivo `CMakeLists.txt` del proyecto, se utiliza este valor
3. De lo contrario, si existe el archivo ``$PROJECT_PATH/version.txt``, su contenido se utiliza como ``PROJECT_VER``
4. De lo contrario, si el proyecto se encuentra en un repositorio Git, se utiliza la salida de ``git describe``
5. De lo contrario, ``PROJECT_VER`` será "1"

En ``native_ota_example``, se utiliza ``$PROJECT_PATH/version.txt`` para definir la versión de la aplicación. Cambie la versión en el archivo para compilar el nuevo firmware.

## Solución de problemas

* Compruebe que su PC puede hacer ping a la "ESP-Dev-Board" usando su IP, y que la IP, AP y otras configuraciones están correctamente configuradas en menuconfig
* Compruebe si algún software de firewall está impidiendo conexiones entrantes en el PC
* Compruebe si puede ver el archivo configurado (por defecto `hello_world.bin`), ejecutando el comando `curl -v https://<dirección-ip-host>:<puerto-host>/<nombre-archivo-firmware>`
* Intente ver el listado de archivos desde un host o teléfono separado

### Error "ota_begin error err=0x104"

Si ve este error, compruebe que el tamaño de flash configurado (y real) sea lo suficientemente grande para las particiones en la tabla de particiones. La tabla de particiones predeterminada "dos ranuras OTA" requiere al menos 4MB de tamaño de flash. Para usar OTA con tamaños de flash más pequeños, cree un CSV de tabla de particiones personalizado (para más detalles, vea [Tablas de Particiones](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/partition-tables.html)) y configúrelo en menuconfig.

Asegúrese de ejecutar "idf.py erase-flash" después de hacer cambios en la tabla de particiones.

### Servidor HTTPS Local

Ejecutar un servidor https local puede ser complicado en algunos casos (debido a certificados autofirmados o posibles problemas con `openssl s_server` en Windows). Aquí hay algunas sugerencias de alternativas:
* Ejecute un servidor HTTP simple para probar la conexión. (Tenga en cuenta que usar un http simple **no es seguro** y solo debe usarse para pruebas)
    - Ejecute `python -m http.server 8070` en el directorio con la imagen de firmware
    - Use http://<ip-host>:8070/<nombre-firmware> como URL de actualización de firmware
    - Habilite *Allow HTTP for OTA* (`CONFIG_ESP_HTTPS_OTA_ALLOW_HTTP`) en `Component config -> ESP HTTPS OTA` para que se acepte la URI sin TLS

* Publique la imagen de firmware en un servidor público (p.ej. github.com) y copie su certificado raíz al directorio `server_certs` como `ca_cert.pem`. El certificado se puede descargar usando el comando openssl `s_client` como se muestra a continuación:

```
echo "" | openssl s_client -showcerts -connect raw.githubusercontent.com:443 | sed -n "1,/Root/d; /BEGIN/,/END/p" | openssl x509 -outform PEM >ca_cert.pem
```

Tenga en cuenta que la URL utilizada aquí es `raw.githubusercontent.com`. Esta URL permite el acceso sin procesar a archivos alojados en el repositorio de github.com. Además, el comando anterior copia el último certificado de la cadena de certificados como el certificado raíz CA del servidor.

### Usando Servidor HTTPS en Producción

Consulte [ESP-TLS: Verificación del Servidor TLS](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/protocols/esp_tls.html#tls-server-verification) para más información sobre la verificación del servidor. El certificado raíz (en formato PEM) debe proporcionarse al miembro `cert_pem` de la configuración `esp_http_client_config_t`.

Tenga en cuenta que se debe utilizar el certificado **raíz** del punto final del servidor para la verificación en lugar de cualquier certificado intermedio de la cadena de certificados. La razón es que el certificado raíz tiene la máxima validez y generalmente permanece igual durante un largo período de tiempo.

Los usuarios también pueden utilizar la función `ESP x509 Certificate Bundle` para la verificación, que cubre la mayoría de los certificados raíz de confianza (usando el miembro `crt_bundle_attach` de la configuración `esp_http_client_config_t`). No es necesario añadir ningún certificado adicional. Consulte [simple_ota_example](simple_ota_example) para su uso.
