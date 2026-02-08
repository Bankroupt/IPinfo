# IPinfo
Es una herramienta de terminal para una inspección  básica de la red. Sus funcionalidades se basan en:
- Identificar clase IPv4 (A/B/C), determinar si es privada o pública
- Convertir máscaras IPv4 a prefijos (/xx)
- Obtener IP local, puerta de enlace (AP) y consultar IP pública con ISP/país
## Requisitos

- Python 3.7+
- Módulos estándar:
	- argparse
	- ipaddress
	- socket
	- urllib.request
	- json, entre otros
## Instalación

1. Marcar ejecutable (opcional):

```bash
git clone https://github.com/Bankroupt/IPinfo.git
chmod +x IPinfo.py
```

2. Ejecutar con Python:

```bash
python3 IPinfo.py
```
## Uso

- Mostrar ayuda:

```bash
python3 IPinfo.py -h
python3 IPinfo.py --help
```
 
- Comprobar una IP (IPv4 o IPv6). Para IPv4 mostrará clase y privacidad:
 
```bash
python3 IPinfo.py --ip xxx.xxx.xxx.xxx
```
 
- Convertir máscara a prefijo:

```bash
python3 IPinfo.py --ip xxx.xxx.xxx.xxx
```
   
- Mostrar IP local, puerta de enlace y datos públicos (ISP/país):
 
```bash
python3 IPinfo.py --ip xxx.xxx.xxx.xxx
```
 
## Detalles de comportamiento

- **Detección de sistema**: usa platform.system(). macOS devuelve "Darwin", por eso el script comprueba 'Darwin' para ejecutar netstat con -f inet/inet6.
- **Puerta de enlace**: intenta leer la tabla de ruteo con comandos nativos según OS. Si falla, devuelve valores de fallback ('192.168.0.1' o '::1' o el local con último octeto = 1).
- **IP pública**: consulta servicios públicos (ipinfo.io e ifconfig.co) con timeout; si falla, devuelve campos "No disponible".
## Buenas prácticas 

- Ejecutar en entornos controlados: máquinas de laboratorio o con permisos administrativos. 
- Evitar exponer información sensible:  úsese en redes de pruebas cuando no se quiera divulgar ubicación o ISP.
- Validar dependencias: en entornos restringidos, instalar iproute2 en Linux si no existe el comando ip.
- Evitar ejecución con privilegios innecesarios: el script no requiere root.
## Ejemplos rápidos

- Obtener clase y privacidad:
 
```bash
python3 IPinfo.py --ip 172.16.5.10
IP: 172.16.5.10 >> Clase: B >> privada
```
 
- Obtener prefijo desde máscara:
 
```bash
python3 IPinfo.py --mask 255.255.254.0
Máscara: 255.255.254.0 >> Prefijo: /23
```
   
- Obtener todas las IPs y datos públicos:
 
```bash
python3 IPinfo.py --all-ips
IP local: xxx.xxx.xxx.xx
IP del AP: xxx.xxx.xxx.x
IP pública: xxx.xxx.xxx.xxx
ISP: xxxxxxxx xxxxxx xxxx
País: xx, xxxxxxx, xxxxxxx
Localización: xx.xxxx,-xx.xxxx
```

## Sugerencias de mejora (priorizadas)

Estaba conversando con un vaso de café y la ia me dio unas sugerencias que si me gustaron si te llama la atención este proyecto te gustaría mejorar con las sugerencias únete.

1. Añadir tests unitarios para funciones clave (clase_ip, prefijo_de_red, parseo de rutas).
2. Añadir opción --json para salida estructurada (útil en pipelines/automatización).
3. Usar requests con control de TLS y retries para consultas externas (actualmente urllib.request).
4. Mejorar detección de gateway en Windows usando API nativa o PowerShell (más fiable que parseo de route).
5. Soporte de prefijos IPv6 y detección de alcance (link-local, unique-local, global).
6. Añadir logging configurable (niveles DEBUG/INFO/ERROR).
