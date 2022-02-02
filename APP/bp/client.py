#from crypt import methods
from logging import NullHandler
from urllib.parse import urlparse
from flask import Flask, request, jsonify, Response, session, redirect, Blueprint,send_from_directory, url_for
from flask.templating import render_template
from flask_pymongo import PyMongo
import pymongo
import sys
from bson import json_util
from bson.objectid import ObjectId
from pymongo import message
from pymongo.uri_parser import parse_userinfo
from werkzeug.wrappers import response
from datetime import datetime, timedelta
#Importamos los metodos para las fechas
import fechas as date_converter
#Importamos las entidades
import datos.trayecto as trayecto_data
import datos.usuario as usuario_data
import datos.vehiculo as vehiculo_data
import datos.conversacion as conversacion_data
import datos.datos_abiertos as datos_abiertos
import datos.weather_api as prediccion_tiempo
#Subir archivos
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

#Login
from google.oauth2 import id_token
from google.auth.transport import requests

import json

cloudinary.config(
  cloud_name = 'cloudgodtour',  
  api_key = '435589662959849',  
  api_secret = 'kfUawr3yMrsnYmeHbO--B0STtnI'  
)

bpclient = Blueprint('bpclient', __name__, template_folder='templates')

@bpclient.route('/')
def arranque():
    return redirect('/login')

@bpclient.route('/app')
def init():
    # Esto ira en el login
    # session['id'] = "6194e4dbc76e95c373d80508"
    # return render_template("login.html")
    if 'id' not in session:
        return render_template("login.html")
    else:
        return render_template("inicio.html",municipios = datos_abiertos.municipios, trayectos = list(trayecto_data.find_trayectos()))


@bpclient.route('/favicon.ico')
def favicon():
    return "/static/images/favicon.ico", 200

@bpclient.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        #try:
            token = request.form.get('idtoken')
            CLIENT_ID = "892536618714-0r5ftehtfat890vn603mu7jtq80bcnfd.apps.googleusercontent.com"
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            userid = idinfo['sub']
            user_email = idinfo['email']
            usuario = usuario_data.find_usuario_by_email(user_email)

            if usuario is None:
                # El usuario no está registrado, lo mandamos a la pantalla de registro
                return "0"
            else:
                # El usuario está ya registrado
                # Meter el usuario obtenido en sesión
                session['id'] = str(usuario["_id"])
                return "1"
        #except ValueError:
            # Invalid token
        #    return "error"

@bpclient.route('/logout')
def logout():
    session.pop('id', None)
    return redirect('/app')

# ---------------------------------------------CONVERSACION-----------------------------------------------------------
#
@bpclient.route('/app/conversacion/<trayecto>', methods=['GET'])
def get_conversacion_trayecto(trayecto):
    lista = []
    listaConversaciones = conversacion_data.find_conversaciones_trayecto(trayecto) #Pasa el trayecto actual como parametro
    for conver in listaConversaciones:
        fecha,hora = date_converter.timestamp_to_date(conver["stamp"])
        dato = {'texto':conver["texto"], 'autor':usuario_data.find_usuario(conver["autor"])["nombre_completo"], 'fecha': fecha, 'hora': hora,
        'id': conver["autor"], 'id_trayecto':trayecto}
        lista.append(dato)
    return render_template('conversacion/conversacionesTrayecto.html', listaConversaciones = list(lista), trayecto = trayecto)

@bpclient.route('/app/conversacion/add/message', methods=['GET'])
def add_message_to_conversation(): 
    
    trayecto = request.args.get("trayecto")
    autor = request.args.get("author")
    texto = request.args.get("message")
    conversacion_data.create_conversacion(trayecto,autor,texto)
    return redirect('/app/conversacion/'+trayecto, code=302)
 

# ---------------------------------------------FIN CONVERSACION-----------------------------------------------------------

# -----------------------------------------------------USUARIO-------------------------------------------------------------

#Devuelve un usuario cuyo id coincide con el que se pasa por parámetro
@bpclient.route('/app/usuarios/<id>', methods=['GET'])
def get_usuario(id):
    usuario = usuario_data.find_usuario(id)
    vehiculos = usuario_data.find_vehiculos_usuario(id)
    fecha_nacimiento_format, hora_nacimiento_format = date_converter.timestamp_to_date(usuario["fecha_nacimiento"])
    if usuario is None:
        return render_template('usuario/listaUsuarios.html', error="No se ha encontrado el usuario")
    else:
        if(usuario["antiguedad_permiso"] is not None):
            fecha_permiso_format, hora_permiso_format = date_converter.timestamp_to_date(usuario["antiguedad_permiso"])
        return render_template("usuario/infoUsuario.html",usuario = usuario, 
        fecha_nacimiento = fecha_nacimiento_format, fecha_permiso = fecha_permiso_format, vehiculos = list(vehiculos))

#Crea un nuevo usuario
@bpclient.route('/app/usuarios/create', methods=['GET', 'POST'])
def create_usuario():
    nombre_completo = request.form.get('nombre_completo')
    correo = request.form.get('correo')
    dni = request.form.get('dni')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    antiguedad_permiso = request.form.get('antiguedad_permiso')
    valoracion_media = 0
    foto_perfil = request.files.getlist("foto_perfil")[0]
    foto_url = None
    if foto_perfil.filename:
        response = cloudinary.uploader.upload(foto_perfil)
        foto_url = response["url"]
    else:
        foto_url = "https://res.cloudinary.com/cloudgodtour/image/upload/v1642355490/perfil-del-usuario_fmvduw.png"

    if nombre_completo and correo and dni and fecha_nacimiento and foto_url:
        userid = usuario_data.create_usuario(nombre_completo,correo,dni,fecha_nacimiento,
        antiguedad_permiso,foto_url,valoracion_media)
        usuario = usuario_data.find_usuario_by_email(correo)
        session['id'] = str(usuario["_id"])
        return redirect('/app')
    else:
        return render_template('login.html', error="No se ha podido crear el usuario, faltan campos")

#Elimina un usuario cuyo id coincide con el que se pasa por parametro
@bpclient.route('/app/usuarios/delete/<id>', methods=['GET'])
def delete_usuario(id):
    usuario_data.delete_usuario(id) #Eliminar los vehiculos del usuario y los trayectos donde el usuario es creador y pasajero
    return redirect("/app")

#Actualiza la informacion del usuario cuyo id coincide con el que se pasa por parametro
@bpclient.route('/app/usuarios/update/<id>', methods=['GET','POST'])
def update_usuario(id):
    usuario = usuario_data.find_usuario(id)
    fecha_format, hora_format = date_converter.timestamp_to_date(usuario["fecha_nacimiento"])
    fecha_permiso = None
    if(usuario["antiguedad_permiso"] is not None):
        fecha_permiso, hora_permiso = date_converter.timestamp_to_date(usuario["antiguedad_permiso"])
    if request.method == 'GET':
        if fecha_permiso != None: 
            return render_template('usuario/actualizarUsuario.html', usuario=usuario, 
            fecha_nacimiento = fecha_format, fecha_permiso = fecha_permiso)      
        else:
            return render_template('usuario/actualizarUsuario.html', usuario=usuario, 
            fecha_nacimiento = fecha_format)    
    else:    
        nombre_completo = request.form.get('nombre_completo')
        correo = request.form.get('correo')
        dni = request.form.get('dni')
        fecha_nacimiento = date_converter.formatear_fecha(request.form.get('fecha_nacimiento'), "%Y-%m-%d", "%Y-%m-%d")
        antiguedad = request.form.get('antiguedad_permiso')
        if antiguedad:
            antiguedad_permiso = date_converter.formatear_fecha(antiguedad, "%Y-%m-%d", "%Y-%m-%d")
        else:
            antiguedad_permiso = None
        
        foto_perfil=  request.files['foto_perfil']
        if foto_perfil:
            response = cloudinary.uploader.upload(foto_perfil)
            url= response["url"]
        else:
            url = ""
        
        if nombre_completo and correo and dni and fecha_nacimiento:
            response = usuario_data.update_usuario(id, nombre_completo, correo, dni, fecha_nacimiento, antiguedad_permiso, url)
            if response == "Acierto":
                return redirect('/app/usuarios/'+id)
        else:
                if fecha_permiso != None: 
                    return render_template('usuario/actualizarUsuario.html', error="El usuario no se ha podido actualizar, faltan campos", usuario=usuario,  
                    fecha_nacimiento = fecha_format, fecha_permiso = fecha_permiso)     
                else:
                    return render_template('usuario/actualizarUsuario.html', error="El usuario no se ha podido actualizar, faltan campos", usuario=usuario,  
                    fecha_nacimiento = fecha_format)        
                
         
@bpclient.route('/app/delete/trayecto/<id_trayecto>/pasajero/<id_pasajero>')
def delete_pasajero_trayecto(id_trayecto, id_pasajero):
    trayecto_data.delete_pasajero_trayecto(id_trayecto, id_pasajero)
    return redirect("/app/trayectos/usuarios/contratados/"+session['id'])
# ---------------------------------------------FIN USUARIO-----------------------------------------------------------

# ---------------------------------------------INICIO TRAYECTO-------------------------------------------------------

#Devuelve un trayecto cuyo id coincide con el que se pasa por parámetro
@bpclient.route('/app/trayectos/ver/<id>', methods=['GET'])
def get_trayecto(id):
    trayecto = trayecto_data.find_trayecto(id)
    pasajeros = trayecto["pasajeros"]
    fecha_format, hora_format = date_converter.timestamp_to_date(trayecto["timestamp"])

    # Esto no se trae nada de la bd

    vehiculo= vehiculo_data.find_vehiculo(trayecto["vehiculo"])
    lista_pasajeros = []
    
    for p in pasajeros:
        pasajero = usuario_data.find_usuario(p)
        lista_pasajeros.append(pasajero)

    puedePagar = True

    idSession = ObjectId(session["id"])

    #Si es el creador, no podrá pagar
    if idSession == trayecto["creador"]:
        puedePagar = False
    else:
        if idSession in pasajeros:
            puedePagar = False
    
    return render_template("trayecto/info_trayecto.html", trayecto = trayecto, fecha = fecha_format, hora= hora_format, pasajeros = lista_pasajeros,vehiculo=vehiculo, session = session, puedePagar = puedePagar)

@bpclient.route('/app/trayectos/create', methods=["GET", "POST"])
def create_trayecto():
    usuario = usuario_data.find_usuario(session['id'])
    if request.method == "GET":
        vehiculos_id = usuario.get("vehiculos")
        lista_vehiculos = []
        if vehiculos_id is not None:
            for v in vehiculos_id:
                vehiculo = vehiculo_data.find_vehiculo(v)
                lista_vehiculos.append(vehiculo)
        return render_template("trayecto/nuevoTrayecto.html", usuario = usuario, vehiculos = lista_vehiculos)
    else: #POST
        creador = request.form.get("creador")
        origen_nombre = request.form.get("origen_nombre")
        origen_latitud = request.form.get("origen_latitud")
        origen_longitud = request.form.get("origen_longitud")
        destino_nombre = request.form.get("destino_nombre")
        destino_latitud = request.form.get("destino_latitud")
        destino_longitud = request.form.get("destino_longitud")
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")
        duracion = request.form.get("duracion")
        periodicidad = request.form.get("periodicidad")
        precio = request.form.get("precio")
        plazas_totales = request.form.get("plazas_totales")
        vehiculo = request.form.get("vehiculo")
        fotos_opcionales = request.files.getlist("fotos_trayecto")
        urls = []
        for foto in fotos_opcionales:
            if foto.filename:
                response = cloudinary.uploader.upload(foto)
                urls.append(response["url"])
        # Crea el nuevo trayecto
        trayecto_data.create_trayecto(creador, origen_nombre, origen_latitud, origen_longitud, destino_nombre, destino_latitud, destino_longitud,
                                      fecha, hora, duracion, periodicidad, precio, urls, plazas_totales, vehiculo)
    
    return redirect("/app")

#Elimina un trayecto cuyo id coincide con el que se pasa por parametro
@bpclient.route('/app/trayectos/delete/<id>', methods=['GET'])
def delete_trayecto(id):
    trayecto_data.delete_trayecto(id)
    return redirect("/app")

#Actualiza la informacion del trayecto cuyo id coincide con el que se pasa por parametro
@bpclient.route('/app/trayectos/update/<id>', methods=['GET', 'POST'])
def update_trayecto(id):
    # Si hay pasajeros ya apuntados al trayecto no se puede modificar información delicada - origne, destino, precio...
    trayecto = trayecto_data.find_trayecto(id)
    usuario = usuario_data.find_usuario(trayecto["creador"])
    pasajeros = trayecto["pasajeros"]

    if request.method == "GET":
        fecha_format, hora_format = date_converter.timestamp_to_date(trayecto["timestamp"])

        vehiculos_id = usuario["vehiculos"] 
        lista_vehiculos = []
        for v in vehiculos_id:
            vehiculo = vehiculo_data.find_vehiculo(v)
            lista_vehiculos.append(vehiculo)

        lista_pasajeros = []
        for p in pasajeros:
            pasajero = usuario_data.find_usuario(p)
            lista_pasajeros.append(pasajero)
        
        return render_template("trayecto/editar_trayecto.html", trayecto = trayecto, usuario = usuario, vehiculos = lista_vehiculos, 
                                                                pasajeros = lista_pasajeros, fecha = fecha_format, hora = hora_format)
    else: #POST
        # creador = request.form.get("creador")
        origen_nombre = request.form.get("origen_nombre")
        origen_latitud = request.form.get("origen_latitud")
        origen_longitud = request.form.get("origen_longitud")
        destino_nombre = request.form.get("destino_nombre")
        destino_latitud = request.form.get("destino_latitud")
        destino_longitud = request.form.get("destino_longitud")
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")
        duracion = request.form.get("duracion")
        periodicidad = request.form.get("periodicidad")
        precio = request.form.get("precio")
        fotos_opcionales = [] #Modificar cuando se manejen las fotos
        plazas_totales = request.form.get("plazas_totales")
        vehiculo = request.form.get("vehiculo")
        imagenes_guardadas = request.form.getlist("imagenes")
        fotos_opcionales = request.files.getlist("fotos_trayecto")
        print(fotos_opcionales)
        urls = imagenes_guardadas
        for foto in fotos_opcionales:
            if foto.filename:
                response = cloudinary.uploader.upload(foto)
                urls.append(response["url"])

        # Actualiza el trayecto
        trayecto_data.update_trayecto(id, origen_nombre, origen_latitud, origen_longitud, destino_nombre, destino_latitud, destino_longitud,
                                      fecha, hora, duracion, periodicidad, precio, urls, plazas_totales, vehiculo, pasajeros)

    return redirect("/app/trayectos/usuarios/creados/"+str(trayecto["creador"]))
#cambiar
@bpclient.route('/app/trayectos/reservar/<id>', methods=["GET"])
def reserva_trayecto(id):
    #Aqui vamos a modelar lo de reservar el trayecto    
    idPasajero = session["id"]
    trayecto_data.add_pasajero(id,idPasajero)
    return redirect("/app")

@bpclient.route('/app/trayectos/usuarios/creados/<id>')
def get_trayectos_creados_usuario(id):
    trayectos = trayecto_data.get_trayectos_of_usuario(id)
    return render_template('trayecto/misTrayectos.html', trayectos = list(trayectos))

@bpclient.route('/app/trayectos/usuarios/contratados/<id>')
def get_trayectos_contratados_usuario(id):
    trayectos = trayecto_data.get_trayectos_usuario_pasajero(id)
    return render_template('trayecto/lista_reservas.html', trayectos = list(trayectos))

@bpclient.route('/app/trayectos/composedQuery',methods=["POST"])
def get_composedQuery():
    listQuerys = []

    origen = request.form.get("origen")
    if origen != "":
        listQuerys.append({'origen.nombre': { "$regex": origen + '.*', "$options" :'i'}})
        
    
    destino = request.form.get("destino")
    if destino != "":
        listQuerys.append({'destino.nombre': { "$regex": destino + '.*', "$options" :'i'}})
    
    precio = request.form.get("precio")
    if precio != "":
        precio = float(precio)
        listQuerys.append({'precio': {'$lte': precio}})


    fecha = request.form.get("fecha")
    if fecha != "":
        stampMin =  date_converter.date_to_timestamp(fecha, "00:00")
        stampMax =  date_converter.date_to_timestamp(fecha, "23:59")
        listQuerys.append({'timestamp': { '$gt' :  stampMin, '$lt' : stampMax}})
    

    trayectos=trayecto_data.get_trayectos_composedQuery(listQuerys)
    if origen == "" and destino == "" and precio == "" and fecha == "":
        trayectos = trayecto_data.find_trayectos()
    
    return render_template("inicio.html",municipios = datos_abiertos.municipios, trayectos=list(trayectos))
    

# ---------------------------------------------FIN TRAYECTO-----------------------------------------------------------

# --------------------------------------------- VEHICULO -----------------------------------------------------------
##Este por ahora no haria falta
'''@bpclient.route('/app/administrador/vehiculos', methods=['GET'])
def get_vehiculos():
    vehiculos = vehiculo_data.find_vehiculos()
    return render_template('vehiculo/vehiculos.html', vehiculos = list(vehiculos), administrador = 1)
'''
#Devuelve los vehiculos del usuario con dicho id
@bpclient.route('/app/vehiculos/usuarios/<id>', methods=['GET'])
def get_vehiculos_usuario(id):
    vehiculos = usuario_data.find_vehiculos_usuario(id)
    return render_template('vehiculo/vehiculos.html', vehiculos = list(vehiculos))

@bpclient.route('/app/vehiculos/<id>', methods=['GET'])
def get_vehiculo(id):
    vehiculo = vehiculo_data.find_vehiculo(id)
    if vehiculo is None:
        return render_template('vehiculo/infoVehiculo.html', error="No se ha encontrado el vehiculo")
    else: 
        return render_template('vehiculo/infoVehiculo.html', vehiculo=vehiculo)    

@bpclient.route('/app/vehiculos/create', methods=["GET","POST"])
def create_vehiculo():
    if request.method == 'GET':
        return render_template('vehiculo/nuevoVehiculo.html')
    else:
        marca= request.form.get('marca')
        modelo= request.form.get('modelo')
        matricula= request.form.get('matricula')
        color= request.form.get('color')
        plazas= int(request.form.get('plazas'))
        #fotos_vehiculo=  request.files['fotos_vehiculo']
        fotos_vehiculo = request.files.getlist("fotos_vehiculo")
        urls = []
        for foto in fotos_vehiculo:
            response = cloudinary.uploader.upload(foto)
            urls.append(response["url"])
        vehiculos = usuario_data.find_vehiculos_usuario_by_id(session['id'])
        if marca and modelo and matricula and color and plazas:
            id = vehiculo_data.create_vehiculo(marca, modelo, matricula, color, plazas, urls)
            vehiculos.append(ObjectId(id))
            usuario_data.add_vehiculo_to_usuario(session['id'], vehiculos)
            return redirect('/app/vehiculos/usuarios/' + session['id'])
        else:
            return render_template('vehiculo/nuevoVehiculo.html', error="No se ha podido crear el vehiculo, faltan campos")

@bpclient.route('/app/vehiculos/update/<id>', methods=['GET', 'POST'])
def update_vehiculo(id):
    vehiculo = vehiculo_data.find_vehiculo(id)
    if request.method == 'GET':
        return render_template('vehiculo/editarVehiculo.html', vehiculo=vehiculo)    
    else:    
        marca= request.form.get('marca')
        modelo= request.form.get('modelo') 
        matricula= request.form.get('matricula')
        color= request.form.get('color')
        plazas= request.form.get('plazas')
        imagenes_guardadas = request.form.getlist("imagenes")
        fotos_opcionales = request.files.getlist("fotos_vehiculo")
        urls = imagenes_guardadas
        for foto in fotos_opcionales:
            if foto.filename:
                response = cloudinary.uploader.upload(foto)
                urls.append(response["url"])
        if marca and modelo and matricula and color and plazas:
            response = vehiculo_data.update_vehiculo(id, marca, modelo, matricula, color, int(plazas), urls)
            if response == "Acierto":
                return redirect('/app/vehiculos/usuarios/'+session['id'])
        else:
            return render_template('vehiculo/editarVehiculo.html', error="El vehiculo no se ha podido actualizar, faltan campos",
            vehiculo=vehiculo) 

@bpclient.route('/app/vehiculos/delete/<id>', methods=['GET'])
def delete_vehiculo(id): #HABRIA QUE ELIMINAR LOS TRAYECTOS DONDE EL VEHICULO PARTICIPA
    usuario_data.delete_vehiculo_usuario(session['id'] , id)
    vehiculo_data.delete_vehiculo(id)
    return redirect('/app/vehiculos/usuarios/' + session['id'])
# ---------------------------------------------FIN VEHICULO -----------------------------------------------------------

# --------------------------------------------- DATOS ABIERTOS - TRAFICO -----------------------------------------------------------

#Redirige al usuario a la plantilla correspondiente para visualizar los datos de trafico
@bpclient.route('/app/trafico', methods=['GET'])
def get_trafico():
    return render_template("datos_abiertos/trafico.html", provincias = datos_abiertos.provincias_trafico)

# --------------------------------------------- FIN DATOS ABIERTOS - TRAFICO -------------------------------------------------------

# --------------------------------------------- DATOS ABIERTOS - GASOLINERA -----------------------------------------------------------

#Redirige al usuario a la plantilla correspondiente para visualizar los datos de las gasolineras
@bpclient.route('/app/gasolineras', methods=['GET'])
def get_gasolineras():    
    return render_template("datos_abiertos/gasolineras.html", provincias = datos_abiertos.provincias, municipios = datos_abiertos.municipios)
# --------------------------------------------- FIN DATOS ABIERTOS - GASOLINERA -----------------------------------------------------------
# --------------------------------------------- API PREDICCION DEL TIEMPO -----------------------------------------------------------
@bpclient.route("/app/tiempo/<latitud>/<longitud>", methods=['GET'])
def get_prediccion(latitud, longitud):
    predicciones, informacion_destino, tiempo_actual = prediccion_tiempo.get_prediccion_tiempo(latitud, longitud)
    return render_template("weather/informacion_tiempo.html", predicciones = predicciones, informacion_destino = informacion_destino, tiempo_actual = tiempo_actual)
# --------------------------------------------- FIN API PREDICCION DEL TIEMPO -----------------------------------------------------------
