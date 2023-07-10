# Implementación segura de protocolos basados en criptografía de clave pública para organización Teletón.

Hoy en día, es cada vez más evidente que las actividades que lleva a cabo cada individuo o una organización involucran la intervención de elementos relacionados con Seguridad Informática y Criptografía buscando contramedidas que no afecten el desempeño del algoritmo criptográfico utilizado, manteniendo así un protocolo criptográfico eficiente y seguro. El objetivo principal del código presentado es implementar protocolos de criptografía de clave pública para proteger ambientes que requieren rápido intercambio y almacenamiento de información. En el presente repositorio se presentará a la organización socio-formadora Teletón una implementación de firmado digital para documentos a través de algoritmos de criptografía de clave pública implementado en  Python 3.3.

## Archivos en el repositorio
En el repositorio se cuenta con los siguientes archivos y carpetas que son escenciales para la corrida exitosa y total comprensión del código.
### *firma.ipynb*
Archivo que contiene el código completo.

### *Contraseña admin.csv*
Base de datos con el número de identificación del administrador y su contraseña.

### *Admin.csv*
Base de datos con el número de identificación del administrador, su nombre, clave pública, su puesto y contraseña.

### *Contraseña usuarios.csv*
Base de datos con el número de identificación de los usuarios, sus nombres y contraseñas.

### *Usuarios y claves publicas.csv*
Base de datos que contiene la siguiente información de todos los usuarios: ID, Nombre, Clave Pública, Puesto y la columna "Vigente" explica si el usuario es válido o no conteniendo un 1 en caso de serlo y, de lo contrario, un 0.

### *Carpeta "Admins"*
Contiene los certificados que se generan para las firmas de los administradores.

### *Carpeta "Pruebas firma"*
Contiene los siguientes docuemtos (archivos de texto): los certificados de cada uno de los usuarios, los documentos que ya han sido firmados y las firmas unificadas

## **Librerías**

### cryptography.hazmat.primitives
Esta librería incluye interfaces de alto y bajo nivel para los algoritmos criptográficos más comunes como cifrados simétricos, resúmenes de mensajes y funciones de derivación de claves. Contiene un módulo de "Hazardous Materials" que incluye en la rama de Primitives algoritmos criptográficos de bajo nivel que son utilizados frecuentemente para crear protocolos criptográficos para sistemas de seguridad informática.
### hashlib
Esta librería permite implementar una interfaz común para acceder a diferentes algoritmos criptográficos de hash. Los algoritmos de hash que incluye son FIPS SHA1, SHA224, SHA256, SHA384, SHA512 y MD5 de RSA.

## **Funciones del código**

### generarCertificado(*usuario, ruta, psw*)

Esta función genera la clave privada utilizando el algoritmo de firmado ed25519, después se encripta la clave privada con la contraseña otorgada y por último se crea un archivo con dicha encripción, en este caso le llamaremos certificado. El certificado se guardará en la ruta otorgada de la forma "Certificado_usuario" como un archivo de texto.

**Parámetros:**
- ***usuario:*** *str*, la persona que se registra.
- ***ruta:*** *str*, directorio de donde se registrará el certificado.
- ***psw:*** *str*, contraseña del usuario.


### cargarPrivateKey(*ruta, psw*)
Esta función primeramente abre y lee el archivo que contiene el certificado, posteriormente desencripta la clave privada con ayuda de la contraseña y finalmente devuelve la clave privada.

**Parámetros:**
- ***ruta:*** *str*, directorio del certificado que contiene la clave privada encriptada.
- ***psw:*** *str*, contraseña con la que la clave privada fue encriptada previamente.

**Returns:** ***private_key:*** *Ed25519PrivateKey*, clave privada.

### hashea(*ruta*)
La función abre el archivo y, con ayuda del algoritmo Hash 256, lee y actualiza el valor del string de hash en bloques de 4K.

**Parámetros:**
- ***ruta:*** *str*, directorio donde se localiza el documento a firmar.

**Returns:** ***sha256_hash.hexdigest():*** *str*, hash en formato hexadecimal.

### hashea_clavepub(*clave_pub*)

Utilizando la librería hashlib, se pasa la clave pública por la función *hashlib.sha256* para convertirla en un hash.

**Parámetros:**
- ***clave_pub:*** *bytes*, clave pública en bytes.

**Returns:** ***sha256_hash.hexdigest():*** *str*, hash en formato hexadecimal.

### firmar(*rutas, ruta_certificado, psw*)

Carga la clave privada del usuario, obtiene la clave pública derivada de ésta y la convierte en un objeto tipo bytes. Posteriormente haseha cada uno de los documentos que recibe y firma dichos hashes. Por cada documento se crea un archivo pem que contiene la firma, la clave pública del firmador en bytes, y la fecha de la acción, todo serparado por tres tabulaciones.

**Parámetros:**

- ***rutas:*** *str*, directorios de los documentos a firmar, si son varios deben estar separados por "\n".
- ***directorio_firma:*** *str*, directorio de la carpeta donde está ubicado el certificado.
- ***ruta_certificado:*** *str*, directorio del certificado del usuario que firmará.


### registro(*ruta_df, ruta_carpeta, tipo, datos_reg*)

Utilizada para registrar a un usuario o administrador. En primer lugar se leen los datos necesarios para registrar al usuario . Se genera su certificado y se revisa si el hash de la clave pública no se encuentra ya en la base de datos, si es así se genera un certificado nuevo. Finalmente la base de datos correspondiente (ya sea usuario o administrador) se actualiza.

**Parámetros:**
- ***ruta_df:*** *str*, directorio del csv con los datos de los usuarios o de los administradores.
- ***ruta_carpeta:*** *str*, directorio de la carpeta donde se desea almacenar el certificado del registro.
- ***tipo:*** *str*, tipo de registro, 1 para usuarios regulares y 0 para administradores.
- ***datos_reg:*** *lst*, lista de datos necesarios necesarios para generar un registro (correo, nombre, puesto y contraseña).


### verifica (*ruta, ruta_firma, ruta_df, ruta_dfadmn*)

Hashea el documento a verificar, lee el archivo con la firma y extrae por cada firmado la firma, la clave pública del firmador y la fecha del firmado. Teniendo la clave pública, se revisa si la firma es válida y con el hash de la clave pública verifica que existe un usuario en la base de datos que tenga esa clave pública. Si esto es correcto, la función imprime el nombre del usuario firmador y la fecha de firmado junto con el hecho de que la firma es válida. Por otro lado, hay dos maneras por las cuales la función regresaría que la firma es inválida:
- Que la firma no sea válida si es que quieres verificar con un documento donde no esté esa firma.
- Que no exista ningún usuario con esa clave pública en el dataframe.

**Parámetros:**
- ***ruta:*** *str*, dirección de donde se encuentra el documento a verificar.
- ***ruta_firma:*** *str*, ruta donde se encuentra el archivo con la firma
- ***ruta_df:*** *str*, ruta donde se encuentra la base de datos de los usuarios
- ***ruta_dfadmn*** *str*, ruta donde se encuentra la base de datos de los administradores.

**Returns:** ***ln:*** *lst*, lista de nombres y fechas de las firmas válidas.

### all_same(*items*)

Regresa True si todos los elementos en una lista son iguales. False en caso contrario. Se utiliza en unificarFirmas.

-***items*** *lst*, lista con elementos a revisar.

**Returns:** *bool*

### unificarFirmas (*rutas*)

Une las firmas de varios usuarios de un solo documento en un archivo. Para ello la función revisa si las firmas corresponden a un mismo documento, si sí regresa True, False en caso contrario. La información de los usuarios firmadores está separada por tres intros. El nombre del archivo resultante tiene la forma "nombre_del_documento_firmas_unificadas".

**Parámetros:**
- ***rutas:*** *str*, rutas de los archivos de firma que se desean unificar, deben estar separados por "\n".

**Returns:** *bool*

### cambiarContraseña (*ruta_certificado, psw, psw_new*)

Desencripta la clave privada del certificado con la contraseña original para volver a encriptarla con la contraseña nueva. Reescribir el archivo del Certificado con esta nueva información.

**Parámetros:**
- ***ruta_certificado:*** *str*, directorio del certificado.
- ***psw:*** *str*, contraseña original.
- ***psw_new:*** *str*, contraseña nueva.

### borrar (*ruta_df, ruta_certificado, id_borrar*)
Esta función fue generada con el fin de que un administrador pueda eliminar a algún usuario. Borrar consiste en eliminar su certificado y en cambiar el valor de la columna "Vigente" de la base de datos de usuarios a 0, en lugar de 1, y también elimina el identificador del usuario para que sea posible volverse a registrar si se necesitara.

**Parámetros:**
- ***ruta_df:*** *str*, directorio de la base de datos que contiene a los usuarios.
- ***ruta_certificado:*** str, directorio del certificado del usuario a borrar.
- ***id_borrar:*** str, identificador del usuario a eliminar.
