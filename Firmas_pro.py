from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives import serialization
import hashlib
import datetime
import os
import pandas as pd

import psycopg2, os, subprocess
from sqlalchemy.types import Integer, DateTime
from sqlalchemy.engine.create import create_engine
DATABASE_URL = 'postgres://uvckgmhwmiagwk:6b99200cfa9d20dd1d347cc31b5ba25db9797d11c9880b7b27c0bd729ee86ece@ec2-52-86-56-90.compute-1.amazonaws.com:5432/de90ls0m3u0mm1'
final_db_url = "postgresql+psycopg2://" + DATABASE_URL.lstrip("postgres://")  # lstrip() is more suitable here than replace() function since we only want to replace postgres at the start!
engine = create_engine(final_db_url)

#usuario: quien se registra
#ruta: directorio de donde se depositará el certificado
#psw: contraseña del usuario
# =============================================================================
#  DECLARE VARIABLES, KEYS, AND PATHS
# =============================================================================
from subir_blob import *
# Create a local directory to hold blob data
local_path = "./data"

# Create a file in the local data directory to upload and download
file_name = "pruebas.txt"
upload_file_path = os.path.join(local_path, file_name)


# Open an existent blob client
container_name = "certificados"
conn_str = "DefaultEndpointsProtocol=https;AccountName=certificadoscrypto;AccountKey=xJEXMrG7Dx5r85AUT4tfSFXzKYLQDcM8wAYfoijDw+vdl4L6kMRRN1xNdG2RI4FWI2kOjwEOXZFU+AStt6B6Kw==;EndpointSuffix=core.windows.net"

AB = AzureBlob(local_path, conn_str, container_name)



def generarCertificado(psw): 
    #Genera la llave privada utilizando ed25519 como algoritmo de firmado
    private_key = ed25519.Ed25519PrivateKey.generate()
    #Encripta la llave privada utilizando la contraseña
    private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm= serialization.BestAvailableEncryption(psw))
    
    return private_bytes
    
    
    
# =============================================================================
#     #Se crea un archivo con la llave privada encriptada (Certificado)
#     ruta_cer=ruta + "\\Certificado_" + str(usuario) +".pem"
#     with open(ruta_cer,"wb+") as f: 
#         f.write(private_bytes) 
#         f.close()
#     
#     return ruta_cer
# =============================================================================
# =============================================================================
#     dfa = pd.read_sql_table("admin_public_keys", con=engine)
#     dfu = pd.read_sql_table("public_keys", con=engine)
#     df= pd.concat([dfa,dfu])
#     dfc=pd.read_sql_table("users", con=engine)
# 
#     psw_db=dfc[dfc['email']==email]['password'].values[0]
#     nombre=dfc[dfc['email']==email]['name'].values[0]
# 
#     #emp_id, nombre, puesto, psw=datos_reg
#     
#     enc = psw.encode()
#     print("enc:", enc)
#     hashkey = hashlib.md5(enc).hexdigest()
#     print("psw:", psw)
#     print(hashkey, psw_db)
# =============================================================================
    

def generarNuevoCertificado(tipo, email, psw):   
    dfu = pd.read_sql_table("public_keys", con=engine)
    dfa = pd.read_sql_table("admin_public_keys", con=engine)
    df= pd.concat([dfa,dfu])
    dfc=pd.read_sql_table("users", con=engine)
    
    nombre=dfc[dfc['email']==email]['name'].values[0]
    psw = bytes(psw, "utf-8")

    #emp_id, nombre, puesto, psw=datos_reg
    while True:
        certificado = generarCertificado(psw)
        AB.upload(email, certificado)
        
        private_key = cargarPrivateKey(email, psw)
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw)
        hash_clavepub = hashea_clavepub(public_bytes)
        if hash_clavepub in df['public_key']:
            continue
        else:
            break
    #emp_id, nombre, puesto, psw=datos_reg
    if tipo == 1:
        puesto=dfu[dfu['email']==email]['position'].values[0]
        agregarClavePublica(email,nombre,hash_clavepub,puesto)
    else:
        puesto=dfa[dfa['email']==email]['position'].values[0]
        agregarClavePublicaAdmin(email,nombre,hash_clavepub,puesto)



#ruta: directorio del certificado que contiene la clave privada encriptada
#psw: contraseña con la que se encriptó la clave privada

def cargarPrivateKey(emp_id, psw):
    #Abre el certificado y desencripta la llave privada utilizando la contraseña
    certificado = AB.download(emp_id)
    private_key = serialization.load_pem_private_key(certificado, psw)
    return private_key

#Devuelve la clave privada

#ruta: directorio del documento a firmar

def hashea(ruta):
    filename = ruta
    sha256_hash = hashlib.sha256()
    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

#Devuelve el hash en formato hexadecimal

#función que haseha la clave pública.
#clave_pub: clave pública en bytes.

def hashea_clavepub(clave_pub):
    sha256_hash = hashlib.sha256(clave_pub)
    return sha256_hash.hexdigest()

#Devuelve el hash en formato hexadecimal

#rutas: directorios de los documentos a firmar
#directorio_firma: directorio de la carpeta donde está ubicado el certificado
#ruta_certificado: directorio del certificado del usuario que firmará

def firmar(rutas, emp_id, psw):
    psw = bytes(psw, 'utf-8')
    lista_rutas = rutas.split("\n")
    #directorio_firma=os.path.dirname(os.path.abspath(ruta_certificado))
    directorio_firma=os.path.dirname(os.path.abspath(lista_rutas[0]))

    private_key = cargarPrivateKey(emp_id, psw)
    
    #Obtención de clave pública en función de la privada.
    public_key = private_key.public_key()
    #Conversión de la clave pública a un objeto tipo bytes.
    public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw)
    
    #Crea lista de las rutas de documentos
    
    #Itera sobre cada ruta de documento
    for i, doc in enumerate(lista_rutas):
        #Hashea el documento 
        hasheo = hashea(doc)
        #Firma el haseho en bytes
        signature = private_key.sign(bytes(hasheo, 'utf-8'))
        #Crea un archivo que contiene el documento firmado y después de 3 tabs la clave pública en bytes.
        #nombre_archivo_firma = lista_rutas[i].split("\\")[-1].split(".")[0] + "_firma_" + str(usuario)
        nombre_archivo_firma = os.path.basename(doc) + "_firma_" + str(emp_id)
        #Obtiene la fecha (dia/mes/año) del día en el que se esta firmando el documento
        now = datetime.date.today()
        fecha_firm = now.strftime('%d/%m/%Y')

        with open(directorio_firma + "\\" + nombre_archivo_firma + ".pem","wb+") as f:
            f.write(signature)
            f.write(b"\t\t\t")
            f.write(public_bytes)
            f.write(b"\t\t\t")
            f.write(bytes(fecha_firm,'utf-8'))
            f.close()

#Agregar usuario y contraseña
def agregarUsuario(email, psw, user_type, curp, name):
    user_type=bool(user_type)
    add_new_user = """
    INSERT INTO users(email, password, user_type, created_on, curp, valid, name) VALUES('%s', '%s', %s, NOW(), '%s', false,'%s')
                              """ %(email, psw, user_type, curp, name)

    try:
        # create a new database connection by calling the connect() function
        conn = psycopg2.connect(DATABASE_URL)

        #  create a new cursor
        cur = conn.cursor()
        cur.execute(add_new_user)
        
        conn.commit()

         # close the communication with the HerokuPostgres
        cur.close()
    except Exception as error:
        print('Error: {}'.format(error))

    finally:
        # close the communication with the database server by calling the close()
        if conn is not None:
            conn.close()

#Agregar usuario a base de datos
def agregarClavePublica(email, name, public_key, position):
    
    deactivation_date = """
    UPDATE public_keys
    SET deactivation_date = NOW()
    WHERE email = '%s' AND active = True;
    """ %email
    
    deactivate_previous_keys = """
    UPDATE public_keys
    SET active = False
    WHERE email = '%s';
    """ %email
    
    add_new_key = """
    INSERT INTO public_keys(email, name, public_key, position, active, created_on) VALUES('%s', '%s', '%s', '%s', true, NOW())
                              """ %(email, name, public_key, position)

    try:
        # create a new database connection by calling the connect() function
        conn = psycopg2.connect(DATABASE_URL)

        #  create a new cursor
        cur = conn.cursor()
        cur.execute(deactivation_date)
        cur.execute(deactivate_previous_keys)
        cur.execute(add_new_key)
        
        conn.commit()

         # close the communication with the HerokuPostgres
        cur.close()
    except Exception as error:
        #print('Could not connect to the Database.')
        #print('Cause: {}'.format(error))
        pass

    finally:
        # close the communication with the database server by calling the close()
        if conn is not None:
            conn.close()

#Agregar administrador
def agregarClavePublicaAdmin(email, name, public_key, position):
    
    deactivation_date = """
    UPDATE admin_public_keys
    SET deactivation_date = NOW()
    WHERE email = '%s' AND active = True;
    """ %email
    
    deactivate_previous_keys = """
    UPDATE admin_public_keys
    SET active = False
    WHERE email = '%s';
    """ %email
    
    add_new_key = """
    INSERT INTO admin_public_keys(email, name, public_key, position, active, created_on) VALUES('%s', '%s', '%s', '%s', true, NOW())
                              """ %(email, name, public_key, position)

    try:
        # create a new database connection by calling the connect() function
        conn = psycopg2.connect(DATABASE_URL)

        #  create a new cursor
        cur = conn.cursor()
        cur.execute(deactivation_date)
        cur.execute(deactivate_previous_keys)
        cur.execute(add_new_key)
        
        conn.commit()

         # close the communication with the HerokuPostgres
        cur.close()
    except Exception as error:
        #print('Could not connect to the Database.')
        #print('Cause: {}'.format(error))
        pass

    finally:
        # close the communication with the database server by calling the close()
        if conn is not None:
            conn.close()

#ruta_df: directorio del csv con los datos de los usuarios o de los administradores
#ruta_df_contrasena: directorio del csv 
#ruta_carpeta: 
#ruta_certificado:
#tipo:

def registro(tipo, datos_reg):
    dfa = pd.read_sql_table("admin_public_keys", con=engine)
    dfu = pd.read_sql_table("public_keys", con=engine)
    df= pd.concat([dfa,dfu])
    
    emp_id, nombre, puesto, psw = datos_reg
    
    psw = bytes(psw, 'utf-8')
    while True:
        #SUBIR CERTIFICADO A AZURE STORAGE
        certificado = generarCertificado(psw) #crear certificado a partir de psw
        AB.upload(emp_id, certificado) # subir certificado a azure storage
        
        private_key = cargarPrivateKey(emp_id, psw)
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw)
        hash_clavepub = hashea_clavepub(public_bytes)
        if hash_clavepub in df['public_key']:
            continue
        else:
            break
    #Obtiene la fecha (dia/mes/año) del día en el que se esta creando el documento
    #now = datetime.date.today()
    #fecha_us = now.strftime('%d/%m/%Y')

    if tipo == 1:
        agregarClavePublica(emp_id,nombre,hash_clavepub,puesto)
    else:
        agregarClavePublicaAdmin(emp_id,nombre,hash_clavepub,puesto)
    
    
    #print(df)
    #print(dfc)

#ruta: del documento
#ruta_firma: directorio de la firma
#ruta_df: directorio del excel
def verifica(ruta, ruta_firma):
    print(ruta_firma)
    ln=[]
    df = pd.read_sql_table("public_keys", con=engine)
    dfa= pd.read_sql_table("admin_public_keys", con=engine)

    with open(ruta_firma,"rb") as f:
        contents = f.read().split(b"\n\n\n")
        hasheo = hashea(ruta)
        for i, content in enumerate(contents):
            content = content.split(b"\t\t\t")
            #separa la firma de los bytes de la clave pública y la fecha
            firma = content[0]
            public_bytes = content[1]
            fecha = str(content[2].decode('utf-8'))
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes) 
            df = df[df['active']==True]
            dfa = dfa[dfa['active']==True]
            try:
                public_key.verify(firma, bytes(hasheo, 'utf-8'))
                try:
                    usuario = df['email'][df.index[df['public_key'] == hashea_clavepub(public_bytes)]].tolist()[0]
                    ln.append(usuario+'-'+fecha)
                except:
                    
                    usuario = dfa['email'][dfa.index[dfa['public_key'] == hashea_clavepub(public_bytes)]].tolist()[0]
                    ln.append(usuario+'-'+fecha)
            except ValueError:
                return []

    return ln

#rutas: directorios de las firmas que vas a unificar 
#rutaunificada: en dónde se depositará el archivo con las firmas unificadas

def all_same(items):
    return all(x == items[0] for x in items)

def unificar_firmas(rutas):
    firmas = b""
    lista_rutas = rutas.split("\n")
    rutaunificada=os.path.dirname(os.path.abspath(lista_rutas[0]))

    nomdocs=[os.path.basename(ruta).split(".")[0] for ruta in lista_rutas]
    print(nomdocs)
    exts=[os.path.basename(ruta).split(".")[-1] for ruta in lista_rutas]
    print(exts)

    if all_same(nomdocs) and all_same(exts) and exts[0]=='pem':
        for i, doc in enumerate(lista_rutas):
            with open(doc, "rb") as f:
                content = f.read()
            firmas = firmas + b"\n\n\n" + content
        firmas = firmas[3:]
        with open(f"{rutaunificada}\{nomdocs[1]}_firmas_unificadas.pem","wb+") as f:
                f.write(firmas)
                f.close()

        return True
    else:
        False



#METER EN EL WII #######################################################################

#Con esta función el admin puede desactivar el usuario
def borrar(email,tipo):

    if tipo == 1:
        deactivation_date_keys = """
        UPDATE public_keys
        SET deactivation_date = NOW()
        WHERE email = '%s' AND active = True;
        """ %email
        
        deactivate_previous_keys = """
        UPDATE public_keys
        SET active = False
        WHERE email = '%s';
        """ %email
    
        deactivation_date_us = """
        UPDATE users
        SET deactivation_date = NOW()
        WHERE email = '%s' AND active = True;
        """ %email
        
        deactivate_user = """
        UPDATE users
        SET valid = False
        WHERE email = '%s';
        """ %email
        try:
            # create a new database connection by calling the connect() function
            conn = psycopg2.connect(DATABASE_URL)

            #  create a new cursor
            cur = conn.cursor()
            cur.execute(deactivation_date_keys)
            cur.execute(deactivate_previous_keys)
            cur.execute(deactivation_date_us)
            cur.execute(deactivate_user)
            
            conn.commit()

            # close the communication with the HerokuPostgres
            cur.close()
        except Exception as error:
            pass

        finally:
            # close the communication with the database server by calling the close()
            if conn is not None:
                conn.close()
    else:
        deactivation_date = """
        UPDATE public_keys_admin
        SET deactivation_date = NOW()
        WHERE email = '%s' AND active = True;
        """ %email
        
        deactivate_previous_keys = """
        UPDATE public_keys_admin
        SET active = False
        WHERE email = '%s';
        """ %email
        try:
            # create a new database connection by calling the connect() function
            conn = psycopg2.connect(DATABASE_URL)

            #  create a new cursor
            cur = conn.cursor()
            cur.execute(deactivation_date)
            cur.execute(deactivate_previous_keys)
            
            conn.commit()

            # close the communication with the HerokuPostgres
            cur.close()
        except Exception as error:
            pass

        finally:
            # close the communication with the database server by calling the close()
            if conn is not None:
                conn.close()
        

#que onda con el email?????
def cambiarcontraseña(emp_id,psw,psw_new,email):
    psw = bytes(psw, 'utf-8')
    psw_new = bytes(psw_new, 'utf-8')
    privatekey = cargarPrivateKey(emp_id, psw)
    private_bytes = privatekey.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm= serialization.BestAvailableEncryption(psw_new))
    print(private_bytes)
    with open(ruta_certificado,"wb+") as f:
        f.write(private_bytes)
        f.close()

    enc = psw_new.encode()
    hashkey = hashlib.md5(enc).hexdigest()
    update_password = """
        UPDATE users
        SET password = '%s'
        WHERE email = '%s'; 
        """ %(hashkey,email)
        
    try:
        # create a new database connection by calling the connect() function
        conn = psycopg2.connect(DATABASE_URL)

        #  create a new cursor
        cur = conn.cursor()
        cur.execute(update_password)
        
        conn.commit()

        # close the communication with the HerokuPostgres
        cur.close()
    except Exception as error:
        pass

    finally:
        # close the communication with the database server by calling the close()
        if conn is not None:
            conn.close()


#el admin cambia la contraseña y con esto se le permite al usuario generar un nuevo certificado
def Admin_cambiarcontraseña(email,psw_new):
    enc = psw_new.encode()
    hashkey = hashlib.md5(enc).hexdigest()
    update_password = """
        UPDATE users
        SET password = '%s'
        WHERE email = '%s'; 
        """ %(hashkey,email)
        
    try:
        # create a new database connection by calling the connect() function
        conn = psycopg2.connect(DATABASE_URL)

        #  create a new cursor
        cur = conn.cursor()
        cur.execute(update_password)
        
        conn.commit()

        # close the communication with the HerokuPostgres
        cur.close()
    except Exception as error:
        pass

    finally:
        # close the communication with the database server by calling the close()
        if conn is not None:
            conn.close()


#Esta función le permite al admin validar un usuario
def validar(email):
    validation = """
    UPDATE users
    SET valid = true
    WHERE email = '%s';
    """ %email

    try:
        # create a new database connection by calling the connect() function
        conn = psycopg2.connect(DATABASE_URL)

        #  create a new cursor
        cur = conn.cursor()
        cur.execute(validation)
        
        conn.commit()

         # close the communication with the HerokuPostgres
        cur.close()
    except Exception as error:
        print('Error: {}'.format(error))

    finally:
        # close the communication with the database server by calling the close()
        if conn is not None:
            conn.close()
            print('Database connection closed.')


#Le entrega a los admins los usuarios no validados
def obtenerNoValidados():
    return pd.read_sql_query("SELECT email, name, curp FROM users WHERE valid = false", con=engine)


#Revisa si el certificado 
def verificarVigencia():
    check = """
    UPDATE public_keys
    SET active = False
    WHERE created_on + INTERVAL '1 year' < NOW() ;
    """

    try:
        # create a new database connection by calling the connect() function
        conn = psycopg2.connect(DATABASE_URL)

        #  create a new cursor
        cur = conn.cursor()
        cur.execute(check)
        
        conn.commit()

         # close the communication with the HerokuPostgres
        cur.close()
    except Exception as error:
        print('Could not connect to the Database.')
        print('Cause: {}'.format(error))

    finally:
        # close the communication with the database server by calling the close()
        if conn is not None:
            conn.close()

# psw = bytes("4d186321c1a7f0f354b297e8914ab240", "utf-8" )
# admin_ser = generarCertificado(psw)
# email = "admin@adminmail.com"
# AB.upload(email, admin_ser)
# private_key = cargarPrivateKey(email, psw)
# public_key = private_key.public_key()
# public_bytes = public_key.public_bytes(
# encoding=serialization.Encoding.Raw,
# format=serialization.PublicFormat.Raw)
# hash_clavepub = hashea_clavepub(public_bytes)
