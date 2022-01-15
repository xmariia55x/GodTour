#from crypt import methods
from logging import NullHandler
from urllib.parse import urlparse
from flask import Flask, request, jsonify, Response, session, redirect, Blueprint,send_from_directory
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
import datos.datos_abiertos as datos_abiertos

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
def init():
    # Esto ira en el login
    session['id'] = "6194e4dbc76e95c373d80508"
    return render_template("inicio.html",municipios = datos_abiertos.municipios, trayectos = list(trayecto_data.find_trayectos()))

@bpclient.route('/favicon.ico')
def favicon():
    return "/static/images/favicon.ico", 200

@bpclient.route('/app/login', methods=["POST"])
def login():
    try:
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
        print(user_email)
        print(usuario)

        if usuario is None:
            # El usuario no está registrado, lo mandamos a la pantalla de registro
            user_name = idinfo['name']
            user_picture = idinfo['picture']
        else:
            # El usuario está ya registrado
            # Meter el usuario obtenido en sesión
            session['id'] = usuario.get('_id')
            session['usuario'] = usuario
            return "/"


    except ValueError:
    # Invalid token
        pass

    return "/"


# -----------------------------------------------------ADMINISTRADOR-------------------------------------------------------------
@bpclient.route('/app/admin', methods=['GET'])
def administrador():
    return render_template("/administrador/administrador.html") 
# -----------------------------------------------------FIN ADMINISTRADOR-------------------------------------------------------------
# -----------------------------------------------------USUARIO-------------------------------------------------------------
#Devuelve una lista con los usuarios
@bpclient.route('/app/administrador/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = usuario_data.find_usuarios()
    return render_template("/usuario/listaUsuarios.html",usuarios = list(usuarios), administrador = 1) 

#Devuelve un usuario cuyo id coincide con el que se pasa por parámetro
@bpclient.route('/app/usuarios/<id>/<administrador>', methods=['GET'])
def get_usuario(id, administrador):
    usuario = usuario_data.find_usuario(id)
    admin_value = int(administrador)
    fecha_nacimiento_format, hora_nacimiento_format = date_converter.timestamp_to_date(usuario["fecha_nacimiento"])
    fecha_permiso_format, hora_permiso_format = date_converter.timestamp_to_date(usuario["antiguedad_permiso"])
    if usuario is None:
        return render_template('usuario/listaUsuarios.html', error="No se ha encontrado el usuario")
    else:
        return render_template("usuario/infoUsuario.html",usuario = usuario, administrador = admin_value, 
        fecha_nacimiento = fecha_nacimiento_format, fecha_permiso = fecha_permiso_format)

#Crea un nuevo usuario
@bpclient.route('/app/usuarios/create', methods=['GET', 'POST'])
def create_usuario():
    if request.method == 'GET':
        return render_template('usuario/crearUsuario.html')
    else:
        nombre_completo = request.form.get('nombre_completo')
        correo = request.form.get('correo')
        dni = request.form.get('dni')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        antiguedad_permiso = request.form.get('antiguedad_permiso')
        foto_perfil = request.form.get('foto_perfil')
        valoracion_media = 0

        if nombre_completo and correo and dni and fecha_nacimiento:
            usuario_data.create_usuario(nombre_completo,correo,dni,fecha_nacimiento,
            antiguedad_permiso,foto_perfil,valoracion_media)
            return redirect("/app/usuarios")
        else:
            return render_template('usuario/nuevoUsuario.html', error="No se ha podido crear el usuario, faltan campos")

#Elimina un usuario cuyo id coincide con el que se pasa por parametro
@bpclient.route('/app/usuarios/delete/<id>', methods=['GET'])
def delete_usuario(id):
    usuario_data.delete_usuario(id) #Eliminar los vehiculos del usuario y los trayectos donde el usuario es creador y pasajero
    return redirect("/")

#Actualiza la informacion del usuario cuyo id coincide con el que se pasa por parametro
@bpclient.route('/app/usuarios/update/<id>', methods=['GET','POST'])
def update_usuario(id):
    if request.method == 'GET':
        usuario = usuario_data.find_usuario(id)
        fecha_format, hora_format = date_converter.timestamp_to_date(usuario["fecha_nacimiento"])
        if(usuario["antiguedad_permiso"] is not None):
            fecha_permiso, hora_permiso = date_converter.timestamp_to_date(usuario["antiguedad_permiso"])
            return render_template('usuario/actualizarUsuario.html', usuario=usuario, fecha_nacimiento = fecha_format, fecha_permiso = fecha_permiso)    
        else:
            return render_template('usuario/actualizarUsuario.html', usuario=usuario, fecha_nacimiento = fecha_format)    
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
                return render_template('/usuario/actualizarUsuario.html', error="El usuario no se ha podido actualizar, faltan campos")
         
@bpclient.route('/app/delete/trayecto/<id_trayecto>/pasajero/<id_pasajero>')
def delete_pasajero_trayecto(id_trayecto, id_pasajero):
    trayecto_data.delete_pasajero_trayecto(id_trayecto, id_pasajero)
    return redirect("/app/trayectos/usuarios/contratados/"+session['id'])
# ---------------------------------------------FIN USUARIO-----------------------------------------------------------

# ---------------------------------------------INICIO TRAYECTO-------------------------------------------------------
#Devuelve una lista de trayectos
@bpclient.route('/app/administrador/trayectos', methods=['GET'])
def get_trayectos():
    trayectos = trayecto_data.find_trayectos()
    return render_template("trayecto/listaTrayectos.html",trayectos=list(trayectos), administrador = 1)
'''
#Devuelve los trayectos de un creador
@bpclient.route('/app/trayectos/creador/<id>', methods=['GET'])
def get_trayectos_creador(id):
    trayectos_creador = trayecto_data.find_trayectos_creador(id)
    #response = json_util.dumps(trayectos_creador)
    #return Response(response, mimetype='application/json')
    return 
'''
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

    print(type(trayecto["creador"]))
    print(type(session["id"]))

    return render_template("trayecto/info_trayecto.html", trayecto = trayecto, fecha = fecha_format, hora= hora_format, pasajeros = lista_pasajeros,vehiculo=vehiculo, session = session)

@bpclient.route('/app/trayectos/create', methods=["GET", "POST"])
def create_trayecto():
    usuario = usuario_data.find_usuario("6194e4dbc76e95c373d80508")
    if request.method == "GET":
        vehiculos_id = usuario["vehiculos"]
        lista_vehiculos = []
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
    
    return redirect("/")

#Elimina un trayecto cuyo id coincide con el que se pasa por parametro
@bpclient.route('/app/trayectos/delete/<id>', methods=['GET'])
def delete_trayecto(id):
    trayecto_data.delete_trayecto(id)
    return redirect("/")

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

@bpclient.route('/app/trayectos/reservar/<id>', methods=["GET"])
def reserva_trayecto(id):
    trayecto = trayecto_data.find_trayecto(id)
    return render_template('trayecto/reservar_trayecto.html', trayecto = trayecto)

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
@bpclient.route('/app/administrador/vehiculos', methods=['GET'])
def get_vehiculos():
    vehiculos = vehiculo_data.find_vehiculos()
    return render_template('vehiculo/vehiculos.html', vehiculos = list(vehiculos), administrador = 1)

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

@bpclient.route('/app/vehiculos/create/<administrador>', methods=["GET","POST"])
def create_vehiculo(administrador):
    admin_value = int(administrador)
    users = usuario_data.find_usuarios()
    if request.method == 'GET':
        if admin_value == 1:
            return render_template('vehiculo/nuevoVehiculo.html', administrador = admin_value, usuarios = list(users))    
        else:
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
            if admin_value == 1:
                usuario = request.form.get('usuario_seleccionado')
                if usuario != "---":
                    id = vehiculo_data.create_vehiculo(marca, modelo, matricula, color, plazas, urls)
                    vehiculos_usuario = usuario_data.find_vehiculos_usuario_by_id(usuario)
                    vehiculos_usuario.append(ObjectId(id))
                    usuario_data.add_vehiculo_to_usuario(usuario, vehiculos_usuario)
                    return redirect('/app/administrador/vehiculos')
                else:
                    return render_template('vehiculo/nuevoVehiculo.html', error="Se debe asignar el vehiculo a un usuario", 
                    administrador = 1, usuarios = list(users))
            else:
                id = vehiculo_data.create_vehiculo(marca, modelo, matricula, color, plazas, urls)
                vehiculos.append(ObjectId(id))
                usuario_data.add_vehiculo_to_usuario(session['id'], vehiculos)
                return redirect('/app/vehiculos/usuarios/' + session['id'])
        else:
            return render_template('vehiculo/nuevoVehiculo.html', error="No se ha podido crear el vehiculo, faltan campos")

@bpclient.route('/app/vehiculos/update/<id>/<administrador>', methods=['GET', 'POST'])
def update_vehiculo(id, administrador):
    admin_value = int(administrador)
    if request.method == 'GET':
        vehiculo = vehiculo_data.find_vehiculo(id)
        if admin_value == 1:
            users = usuario_data.find_usuarios()
            return render_template('vehiculo/editarVehiculo.html', vehiculo=vehiculo, administrador = admin_value, usuarios = list(users))    
        else:
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
            if admin_value == 1:
                usuario = request.form.get('usuario_seleccionado')
                if usuario != "---":
                    vehiculos = usuario_data.find_vehiculos_usuario_by_id(usuario)
                    oid = ObjectId(id)
                    if not oid in vehiculos:
                        vehiculos.append(oid)
                        usuario_data.add_vehiculo_to_usuario(usuario, vehiculos)
            if response == "Acierto":
                if admin_value == 1:
                    return redirect('/app/administrador/vehiculos')
                else:
                    return redirect('/')
        else:
            return render_template('vehiculo/editarVehiculo.html', error="El vehiculo no se ha podido actualizar, faltan campos") 

@bpclient.route('/app/vehiculos/delete/<id>/<administrador>', methods=['GET'])
def delete_vehiculo(id, administrador):
    admin_value = int(administrador)
    if admin_value == 1:
        usuario_data.delete_vehiculo_from_usuarios_list(id)
    else:
        usuario_data.delete_vehiculo_usuario(session['id'] , id)
    
    vehiculo_data.delete_vehiculo(id)

    if admin_value == 1:
        return redirect('/app/administrador/vehiculos')
    else :
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
