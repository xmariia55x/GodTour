from logging import NullHandler
from flask import Flask, request, jsonify, Response, session, redirect, Blueprint
from flask.templating import render_template
from flask_pymongo import PyMongo
import pymongo
import sys
from bson import json_util
from bson.objectid import ObjectId
from pymongo import message
from werkzeug.wrappers import response
import datos.datos_abiertos
from datetime import datetime, timedelta
# Importamos el patron singleton - Quizás no haga falta aquí, solo en las entidades (REVISAR DESPUES)
from mongoDB import client, db, usuario_db, trayecto_db, vehiculo_db
#Importamos las entidades
import datos.trayecto as trayecto_data
import datos.usuario as usuario_data
import datos.vehiculo as vehiculo_data

bpclient = Blueprint('bpclient', __name__, template_folder='templates')

# Para formatear fechas con un formato de entrada y formato salida
def formatear_fecha(str_fecha, formatoEntrada, formatoSalida):
    date_obj = datetime.strptime(str_fecha, formatoEntrada)
    return datetime.strftime(date_obj, formatoSalida)

#PRUEBA JINJA
@bpclient.route('/')
def prueba_Jinja():
    #return render_template("pruebaJinja.html",variable="soy una variable")
    return redirect("/usuario", code=302)

#Si se quita esto y se ejecuta un GET, en la consola de python salta una excepcion aunque  muestra los vehiculos
#NO TOCAR!!!!
@bpclient.route("/favicon.ico")
def favicon():
   return "", 200

# -----------------------------------------------------USUARIO-------------------------------------------------------------
# Obtengo la colección de usuarios
usuario_db = db['Usuario']

#Devuelve una lista con los usuarios
@bpclient.route('/usuario', methods=['GET'])
def get_usuarios():
    usuarios = usuario_data.find_usuarios()
    # response = json_util.dumps(usuarios)
    #return Response(response, mimetype='application/json')
    return render_template("/usuario/listaUsuarios.html",usuarios = list(usuarios)) 

#Devuelve un usuario cuyo id coincide con el que se pasa por parámetro
@bpclient.route('/usuario/<id>', methods=['GET'])
def get_usuario(id):
    usuario = usuario_data.find_usuario(id)
    #response = json_util.dumps(usuario)
    #if usuario == 'null':
    #    return not_found("No se han encontrado usuarios con el id: " + id)
    #else:     
        #return Response(response, mimetype='application/json')
    return render_template("/usuario/infoUsuario.html",usuario = usuario)

#Metodo necesario para crear un usuario
@bpclient.route('/usuario/link_create/', methods=['GET'])
def link_create_usuario():
    return render_template("/usuario/crearUsuario.html")

#Metodo necesario para actualizar un usuario
@bpclient.route('/usuario/link_update/<id>', methods=['GET'])
def link_update_usuario(id):
    usuario = usuario_data.find_usuario(id)
    return render_template("/usuario/actualizarUsuario.html", usuario = usuario)

#Crea un nuevo usuario
@bpclient.route('/usuario/create', methods=['POST'])
def create_usuario():
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
        return redirect("/usuario")
    else:
        return not_found("No se ha podido crear un usuario")

#Elimina un usuario cuyo id coincide con el que se pasa por parametro
@bpclient.route('/usuario/delete/<id>', methods=['GET','DELETE'])
def delete_usuario(id):
    usuario_db.delete_one({'_id': ObjectId(id)})
    #response = jsonify({'message': 'El usuario con id '+id+' se ha eliminado exitosamente'})
    return redirect("/usuario",code = 302)

#Actualiza la informacion del usuario cuyo id coincide con el que se pasa por parametro
@bpclient.route('/usuario/update/<id>', methods=['POST'])
def update_usuario(id):
    nombre_completo = request.form.get('nombre_completo')
    correo = request.form.get('correo')
    dni = request.form.get('dni')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    antiguedad_permiso = request.form.get('antiguedad_permiso')
    foto_perfil = request.form.get('foto_perfil')
    valoracion_media = request.form.get('valoracion_media')
    
    if nombre_completo and correo and dni and fecha_nacimiento:
        response = usuario_data.update_usuario(id, nombre_completo, correo, dni, fecha_nacimiento, antiguedad_permiso, foto_perfil, valoracion_media)
        #response = jsonify({'message': 'El usuario con id '+id+' se ha actualizado exitosamente'})
        
        if response == "Acierto":
            return redirect('/usuario')
        else:
            return render_template('usuario/actualizarUsuario.html', error="El usuario no se ha podido actualizar, faltan campos")

#Devuelve una lista de usuarios ordenados alfabeticamente, orden ascendente -> python.ASCENDING , orden descendente -> python.DESCENDING
@bpclient.route('/usuario/by_name', methods=['GET'])
def get_usuario_ordered_by_name():
    usuarios = usuario_db.find().sort("nombre_completo", pymongo.ASCENDING)
    response = json_util.dumps(usuarios)
    return Response(response, mimetype='application/json')

#Devuelve un usuario a partir de (parte de) su correo electronico pasado por parametro
@bpclient.route('/usuario/by_email', methods=['POST'])
def get_usuario_by_email():
    email = request.json['correo']
    if email:
        usuarios = usuario_db.find( { 'correo': { "$regex": email + '.*', "$options" :'i' }} )
        response = json_util.dumps(usuarios)
        if response == '[]':
            return not_found("No se ha encontrado ningún usuario con el email " + email)
        else:     
            return Response(response, mimetype='application/json')
    else:
        return not_found("No se ha introducido ningun email")


# ---------------------------------------------FIN USUARIO-----------------------------------------------------------

# ---------------------------------------------INICIO TRAYECTO-----------------------------------------------------------

# Obtengo la colección de trayectos
trayecto_db = db['Trayecto']

#Devuelve una lista de trayectos
@bpclient.route('/trayecto', methods=['GET'])
def get_trayectos():
    trayectos = trayecto_data.find_trayectos()
    response = json_util.dumps(trayectos)
    return Response(response, mimetype='application/json')

#Devuelve los trayectos de un creador
@bpclient.route('/trayecto/creador/<id>', methods=['GET'])
def get_trayectos_creador(id):
    trayectos_creador = trayecto_data.find_trayectos_creador(id)
    #response = json_util.dumps(trayectos_creador)
    #return Response(response, mimetype='application/json')
    return render_template("trayecto/misTrayectos.html", trayectos_creador = list(trayectos_creador))

#Devuelve un trayecto cuyo id coincide con el que se pasa por parámetro
@bpclient.route('/trayecto/<id>', methods=['GET'])
def get_trayecto(id):
    trayecto = trayecto_data.find_trayecto(id)
    response = json_util.dumps(trayecto)
    if response == 'null':
        return not_found("No se han encontrado trayectos con el id: " + id)
    else:     
        return Response(response, mimetype='application/json')

@bpclient.route('/trayecto/create', methods=["GET", "POST"])
def create_trayecto():
    usuario = usuario_data.find_usuario("6194e4dbc76e95c373d80508")
    if request.method == "GET":
        vehiculos_id = usuario["vehiculos"]
        lista_vehiculos = []
        for v in vehiculos_id:
            vehiculo = vehiculo_db.find_one({'_id': ObjectId(v)})
            lista_vehiculos.append(vehiculo)
        return render_template("trayecto/nuevo_trayecto.html", usuario = usuario, vehiculos = lista_vehiculos)
    else: #POST
        creador = request.form.get("creador")
        origen_nombre = request.form.get("origen_nombre")
        origen_latitud = float(request.form.get("origen_latitud"))
        origen_longitud = float(request.form.get("origen_longitud"))
        destino_nombre = request.form.get("destino_nombre")
        destino_latitud = float(request.form.get("destino_latitud"))
        destino_longitud = float(request.form.get("destino_longitud"))
        fecha = formatear_fecha(request.form.get("fecha")) #datetime.strptime(request.form.get("fecha"), '%Y-%m-%d') 
        hora = request.form.get("hora")
        duracion = int(request.form.get("duracion"))
        periodicidad = int(request.form.get("periodicidad"))
        precio = float(request.form.get("precio"))
        fotos_opcionales = [] #Modificar cuando se manejen las fotos
        plazas_totales = int(request.form.get("plazas_totales"))
        vehiculo = request.form.get("vehiculo")
        pasajeros = []  #Modificar para edit

        # Crea el nuevo trayecto
        trayecto_data.create_trayecto(creador, origen_nombre, origen_latitud, origen_longitud, destino_nombre, destino_latitud, destino_longitud,
                                      fecha, hora, duracion, periodicidad, precio, fotos_opcionales, plazas_totales, vehiculo, pasajeros)
    
    return redirect("/")

'''
#Crea un nuevo trayecto
@app.route('/trayecto/create', methods=["POST"])
def create_trayecto():
    
    PRUEBA
    {
    "creador":"6194e4dbc76e95c373d80508",
    "destino":{"nombre":"ZARAGOZA","latitud":-33.56,"longitud":41.9},
    "duracion":500,
    "fecha":"05/12/2021",
    "hora":"16:00",
    "origen":{"nombre":"SEVILLA","latitud":-141.9,"longitud":54.8},
    "periodicidad":7,
    "precio":20.5,
    "fotos_opcionales":["http://www.google.drive.com/fotocoche.jpg"],
    "plazas_totales":3,
    "vehiculo":"61a6769c6df626e2acba5868"
    }
    
    creador= request.json['creador']
    destino= request.json['destino'] 
    duracion= int(request.json['duracion'])
    fecha= request.json['fecha']
    hora= request.json['hora']
    origen= request.json['origen']
    periodicidad= int(request.json['periodicidad'])
    precio= float(request.json['precio'])
    fotos_opcionales= request.json['fotos_opcionales']
    plazas_totales= int(request.json['plazas_totales'])
    vehiculo= request.json['vehiculo']

    if creador and destino and origen and fecha and hora and precio and plazas_totales and vehiculo:
        id=trayecto_db.insert_one({
            "creador": ObjectId(creador),
            "destino": destino,
            "duracion": duracion,
            "fecha": fecha,
            "hora": hora,
            "origen": origen,
            "periodicidad": periodicidad,
            "precio": precio,
            "fotos_opcionales": fotos_opcionales,
            "plazas_totales": plazas_totales,
            "vehiculo": ObjectId(vehiculo), 
            "pasajeros": []
        })
        response = {
            "id": str(id),
            "creador": creador,
            "destino": destino,
            "duracion": duracion,
            "fecha": fecha,
            "hora": hora,
            "origen": origen,
            "periodicidad": periodicidad,
            "precio": precio,
            "fotos_opcionales": fotos_opcionales,
            "plazas_totales": plazas_totales,
            "vehiculo": vehiculo, 
            "pasajeros": []
        }
        return response
    else:
        return not_found("No se ha podido crear el trayecto")
'''

#Elimina un trayecto cuyo id coincide con el que se pasa por parametro
@bpclient.route('/trayecto/delete/<id>', methods=['GET'])
def delete_trayecto(id):
    trayecto_db.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message': 'El trayecto con id '+id+' se ha eliminado exitosamente'})
    return response

#Actualiza la informacion del trayecto cuyo id coincide con el que se pasa por parametro
@bpclient.route('/trayecto/update/<id>', methods=['GET', 'POST'])
def update_trayecto(id):
    # Si hay pasajeros ya apuntados al trayecto no se puede modificar información delicada - origne, destino, precio...
    if request.method == "GET":
        trayecto = trayecto_data.find_trayecto(id)
        usuario = usuario_data.find_usuario(trayecto["creador"])
        vehiculos_id = usuario["vehiculos"]
        fecha_format = formatear_fecha(trayecto["fecha"], '%d/%m/%Y', '%Y-%m-%d')
        lista_vehiculos = []
        for v in vehiculos_id:
            vehiculo = vehiculo_db.find_one({'_id': ObjectId(v)})
            lista_vehiculos.append(vehiculo)
        return render_template("trayecto/editar_trayecto.html", trayecto = trayecto, usuario = usuario, vehiculos = lista_vehiculos, fecha = fecha_format)
    else: #POST
        # creador = request.form.get("creador")
        origen_nombre = request.form.get("origen_nombre")
        origen_latitud = float(request.form.get("origen_latitud"))
        origen_longitud = float(request.form.get("origen_longitud"))
        destino_nombre = request.form.get("destino_nombre")
        destino_latitud = float(request.form.get("destino_latitud"))
        destino_longitud = float(request.form.get("destino_longitud"))
        fecha = formatear_fecha(request.form.get("fecha"), '%Y-%m-%d', '%d/%m/%Y')
        hora = request.form.get("hora")
        duracion = int(request.form.get("duracion"))
        periodicidad = int(request.form.get("periodicidad"))
        precio = float(request.form.get("precio"))
        fotos_opcionales = [] #Modificar cuando se manejen las fotos
        plazas_totales = int(request.form.get("plazas_totales"))
        vehiculo = request.form.get("vehiculo")
        # pasajeros = []  #Modificar para edit

        # Crea el nuevo trayecto
        trayecto_data.update_trayecto(id, origen_nombre, origen_latitud, origen_longitud, destino_nombre, destino_latitud, destino_longitud,
                                      fecha, hora, duracion, periodicidad, precio, fotos_opcionales, plazas_totales, vehiculo)

    return redirect("/")

'''

#Actualiza la informacion del trayecto cuyo id coincide con el que se pasa por parametro
@app.route('/trayecto/update/<id>', methods=['PUT'])
def update_trayecto(id):
    destino = request.json['destino']
    duracion= int(request.json['duracion'])
    fecha = request.json['fecha']
    hora = request.json['hora']
    origen = request.json['origen']
    periodicidad = int(request.json['periodicidad'])
    precio= float(request.json['precio'])
    fotos_opcionales = request.json['fotos_opcionales']
    plazas_totales= int(request.json['plazas_totales'])
    vehiculo = request.json['vehiculo']
    pasajeros = request.json['pasajeros']

    lista_pasajeros = []
    if destino and origen and fecha and hora and precio and plazas_totales and vehiculo:
        if pasajeros:
            for pasajero in pasajeros:
                lista_pasajeros.append(ObjectId(pasajero))
                
        filter = {"_id": ObjectId(id)}
        new_values = {"$set":{
            "destino": destino,
            "duracion": duracion,
            "fecha": fecha,
            "hora": hora,
            "origen": origen,
            "periodicidad": periodicidad,
            "precio": precio,
            "fotos_opcionales": fotos_opcionales,
            "plazas_totales": plazas_totales,
            "vehiculo": ObjectId(vehiculo), 
            "pasajeros": lista_pasajeros
        }}
        
        result = trayecto_db.update_one(filter, new_values) 

        if result.matched_count == 0:
            return not_found("No se ha encontrado el trayecto con id: " + id)
        else:
            response = jsonify({'message': 'El trayecto con id '+id+' se ha actualizado exitosamente'})
        
        return response
    else:
        return not_found("No se ha podido actualizar el trayecto con id: " + id)
'''

#Devuelve los trayectos cuyo destino coincide con el que se pasa por parámetro 
@bpclient.route('/trayecto/by_destino', methods=['POST'])
def get_trayecto_destino():
    destino_nombre = request.json['destino_nombre'].upper()
    
    if destino_nombre:
        trayecto = trayecto_db.find({'destino.nombre': destino_nombre})
        response = json_util.dumps(trayecto)
        if response == '[]':
            return not_found("No se han encontrado trayectos con destino " + destino_nombre)
        else:     
            return Response(response, mimetype='application/json')
    else:
        return not_found("No se ha indicado un destino")

#Devuelve los trayectos cuyo origen coincide con el que se pasa por parámetro 
@bpclient.route('/trayecto/by_origen', methods=['POST'])
def get_trayecto_origen():
    origen_nombre = request.json['origen.nombre'].upper()
    
    if origen_nombre:
        trayecto = trayecto_db.find({'origen.nombre': origen_nombre})
        response = json_util.dumps(trayecto)
        if response == '[]':
            return not_found("No se han encontrado trayectos con origen " + origen_nombre)
        else:     
            return Response(response, mimetype='application/json')
    else:
        return not_found("No se ha indicado un origen")
    
#Devuelve los trayectos cuyos origenes y destinos coinciden con los pasados por parámetro 
@bpclient.route('/trayecto/by_origen_destino', methods=['POST'])
def get_trayecto_origen_destino():
    origen_nombre = request.json['origen'].upper()
    destino_nombre = request.json['destino'].upper()
    if origen_nombre and destino_nombre:
        trayecto = trayecto_db.find({'origen.nombre': origen_nombre, 'destino.nombre': destino_nombre})
        response = json_util.dumps(trayecto)
        if response == '[]':
            return not_found("No se han encontrado trayectos con origen " + origen_nombre + " y destino " + destino_nombre)
        else:     
            return Response(response, mimetype='application/json')
    else:
        return not_found("No se han indicado trayectos con origen " + origen_nombre + " y destino " + destino_nombre)

#Devuelve los trayectos ordenados por la fecha y hora
@bpclient.route('/trayecto/by_fecha_hora', methods=['POST'])
def get_trayecto_fecha_hora():
    fecha = request.json['origen'].upper()
    hora = request.json['destino'].upper()
    if origen_nombre and destino_nombre:
        trayecto = trayecto_db.find({'origen.nombre': origen_nombre, 'destino.nombre': destino_nombre})
        response = json_util.dumps(trayecto)
        if response == '[]':
            return not_found("No se han encontrado trayectos con origen " + origen_nombre + " y destino " + destino_nombre)
        else:     
            return Response(response, mimetype='application/json')
    else:
        return not_found("No se han indicado trayectos con origen " + origen_nombre + " y destino " + destino_nombre)

#Devuelve los trayectos cuyo precio es menor que la cantidad indicada por parametro
@bpclient.route('/trayecto/by_precio', methods=['POST'])
def get_trayecto_precio():
    precio = request.json['precio']
    if precio:
        trayecto = trayecto_db.find({'precio': { "$lt" : precio }})
        response = json_util.dumps(trayecto)
        if response == '[]':
            return not_found("Trayectos con precio menor a " + str(precio) + " no encontrados")
        else:     
            return Response(response, mimetype='application/json')
    else:
        return not_found("No se ha indicado un precio")

#Devuelve los usuarios de un trayecto a partir del id del trayecto indicado por parametro
@bpclient.route('/usuario/by_trayecto/<id>', methods=['GET'])
def get_usuario_trayecto(id):
    trayecto = trayecto_db.find_one({'_id': ObjectId(id)})
    pasajeros = trayecto.get("pasajeros")
    lista_pasajeros = []
    for pasajero in pasajeros:
        usuario = usuario_db.find_one({'_id': pasajero})
        lista_pasajeros.append(usuario)
    response = json_util.dumps(lista_pasajeros)
    if response == '[]':
        return not_found("El trayecto con id: " + id + " no tiene usuarios")
    else:     
        return Response(response, mimetype='application/json')

# ---------------------------------------------FIN TRAYECTO-----------------------------------------------------------

# --------------------------------------------- VEHICULO -----------------------------------------------------------
vehiculo_db = db['Vehiculo']

@bpclient.route('/vehiculo', methods=['GET'])
def get_vehiculos():
    vehiculos = vehiculo_data.find_vehiculos()
    #response = json_util.dumps(vehiculos)
    #return Response(response, mimetype='application/json')
    return render_template('vehiculo/vehiculos.html', vehiculos = list(vehiculos))

@bpclient.route('/vehiculo/<id>', methods=['GET'])
def get_vehiculo(id):
    vehiculo = vehiculo_data.find_vehiculo(id)
    response = json_util.dumps(vehiculo)
    if response == 'null':
        return render_template('vehiculo/infoVehiculo.html', error="No se ha encontrado el vehiculo")
        #return not_found("No se han encontrado vehiculos con el id: " + id)
    else: 
        return render_template('vehiculo/infoVehiculo.html', vehiculo=vehiculo)    
        #return Response(response, mimetype='application/json')

@bpclient.route('/vehiculo/create', methods=["GET","POST"])
def create_vehiculo():
    if request.method == 'GET':
        return render_template('vehiculo/nuevoVehiculo.html')
    else:
        '''
        PRUEBA
        {
        "marca":"Opel",
        "modelo":"Astra",
        "matricula":"5588CDF",
        "color":"Negro",
        "plazas":5,
        "fotos_vehiculo":["http://www.google.drive.com/fotocoche.jpg"]
        }
        '''
        marca= request.form['marca']
        modelo= request.form['modelo'] 
        matricula= request.form['matricula']
        color= request.form['color']
        plazas= int(request.form['plazas'])
        fotos_vehiculo= request.form['fotos_vehiculo']

        if marca and modelo and matricula and color and plazas:
            '''id=vehiculo_db.insert_one({
                "marca": marca,
                "modelo": modelo,
                "matricula": matricula,
                "color": color,
                "plazas": plazas,
                "fotos_vehiculo": fotos_vehiculo
            })
            response = {
                "id": str(id),
                "marca": marca,
                "modelo": modelo,
                "matricula": matricula,
                "color": color,
                "plazas": plazas,
                "fotos_vehiculo": fotos_vehiculo
            }
            return response'''
            vehiculo_data.create_vehiculo(marca, modelo, matricula, color, plazas, fotos_vehiculo)
            return redirect('/vehiculo')
        else:
            return render_template('vehiculo/nuevoVehiculo.html', error="No se ha podido crear el vehiculo, faltan campos")
            #return not_found("No se ha podido crear el vehiculo")

@bpclient.route('/vehiculo/update/<id>', methods=['GET', 'POST'])
def update_vehiculo(id):
    if request.method == 'GET':
        vehiculo = vehiculo_data.find_vehiculo(id)
        response = json_util.dumps(vehiculo)
        return render_template('vehiculo/editarVehiculo.html', vehiculo=vehiculo)    
        #return Response(response, mimetype='application/json')
    else:    
        marca= request.form['marca']
        modelo= request.form['modelo'] 
        matricula= request.form['matricula']
        color= request.form['color']
        plazas= request.form['plazas']
        fotos_vehiculo= request.form['fotos_vehiculo']
       
        if marca and modelo and matricula and color and plazas:
            response = vehiculo_data.update_vehiculo(id, marca, modelo, matricula, color, int(plazas), fotos_vehiculo)
            if response == "Acierto":
                return redirect('/vehiculo')
        else:
            return render_template('vehiculo/editarVehiculo.html', error="El vehiculo no se ha podido actualizar, faltan campos") 

@bpclient.route('/vehiculo/delete/<id>', methods=['GET'])
def delete_vehiculo(id):
    vehiculo_data.delete_vehiculo(id)
    return redirect("/vehiculo",code = 302)
    #response = jsonify({'message': 'El vehiculo con id '+id+' se ha eliminado exitosamente'})
    #return response
# ---------------------------------------------FIN VEHICULO -----------------------------------------------------------

# --------------------------------------------- DATOS ABIERTOS - TRAFICO -----------------------------------------------------------
def get_datos_trafico_actualizados():
    trafico_datos_abiertos = datos_abiertos.descargar_datos_trafico()
    return trafico_datos_abiertos

#Devuelve una lista con las incidencias de trafico del conjunto de datos abiertos
@bpclient.route('/trafico', methods=['GET'])
def get_trafico():
    datos_trafico = get_datos_trafico_actualizados()
    response = json_util.dumps(datos_trafico)
    return Response(response, mimetype='application/json')

#Devuelve las incidencias de trafico de una provincia
@bpclient.route('/trafico/by_provincia', methods=['POST'])
def get_incidencias_provincia():
    provincia = request.json["provincia"]
    if provincia:
        trafico_actualizado = get_datos_trafico_actualizados()
        incidencias_trafico = datos_abiertos.get_incidencias_provincia(provincia, trafico_actualizado)
        response = json_util.dumps(incidencias_trafico)    
        if response == '[]':
            return not_found("No hay incidencias en " + provincia) 
        else: 
            return Response(response, mimetype='application/json')
    else:
        return not_found("No se ha indicado provincia")
        
@bpclient.route('/trafico/rango', methods=['POST'])
def get_trafico_in_rango():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
    except :
        print("Latitud, longitud o rango no introducidos")
    
    rango = float(request.json["rango"])
    
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_rango(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_rango(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias de trafico en un rango de " + str(rango) + " kms")
    else:
        return Response(response, mimetype='application/json')

@bpclient.route('/trafico/nieve', methods=['POST'])
def get_trafico_nieve():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
    except :
        print("Latitud y longitud no introducidas")
    
    rango = float(request.json["rango"])
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_nieve(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_nieve(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias de nieve trafico a " + str(rango) + " kms")
    else:
        return Response(response, mimetype='application/json')    

@bpclient.route('/trafico/obras', methods=['POST'])
def get_trafico_obras():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
    except :
        print("Latitud y longitud no introducidas")
    
    rango = float(request.json["rango"])
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_obras(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_obras(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias de obras trafico a " + str(rango) + " kms")
    else:
        return Response(response, mimetype='application/json')  

@bpclient.route('/trafico/cortes', methods=['POST'])
def get_trafico_cortes():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
    except :
        print("Latitud y longitud no introducidas")
    
    rango = float(request.json["rango"])
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_cortes(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_cortes(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias de cortes de trafico a " + str(rango) + " kms")
    else:
        return Response(response, mimetype='application/json')  

@bpclient.route('/trafico/clima', methods=['POST'])
def get_trafico_clima():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
    except :
        print("Latitud y longitud no introducidas")
    
    rango = float(request.json["rango"])
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_clima(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_clima(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias climatologicas a " + str(rango) + " kms")
    else:
        return Response(response, mimetype='application/json')  

# --------------------------------------------- FIN DATOS ABIERTOS - TRAFICO -------------------------------------------------------

# ---------------------------------------------MANEJO DE ERRORES-----------------------------------------------------------

#Error 400
@bpclient.errorhandler(400)
def not_found(error=None):
    response = jsonify({
        'message': 'Bad request: ' + request.url,
        'status': 400
    })
    response.status_code = 400
    return response

#Error 404
@bpclient.errorhandler(404)
def not_found(error=None):
    if error is None : 
        response = jsonify({
        'message': 'Recurso no encontrado: ' + request.url,
        'status': 404
        })
        #response = json.dumps({'message': 'Recurso no encontrado: ' + request.url})
        #return Response(response, status=404, mimetype='application/json')
    else: 
        #response = json_util.dumps({'message': error})
        
        response = jsonify({
        'message': error,
        'status': 404
        })

        #return Response(response, status=404, mimetype='application/json')
    response.status_code = 404
    return response

#Error 500
@bpclient.errorhandler(500)
def server_error(error):
    response = jsonify({
        'message': 'Error del servidor: ' + request.url,
        'status': 500
    })
    response.status_code = 500
    return response

# --------------------------------------------- DATOS ABIERTOS - GASOLINERA -----------------------------------------------------------
def get_datos_gasolineras_actualizadas():
    global ultima_actualizacion_gasolineras, gasolineras_datos_abiertos #Llamada a la vbles globales para obtener y actualizar su valor
    proxima_actualizacion = ultima_actualizacion_gasolineras + timedelta(hours = 24) #Comprobamos que los datos se actualizan cada 24 horas
    if ultima_actualizacion_gasolineras > proxima_actualizacion: #Descargar los datos y actualizar en caso de que este desactualizado
        ultima_actualizacion_gasolineras = proxima_actualizacion
        gasolineras_datos_abiertos = datos_abiertos.descargar_gasolineras()
    return gasolineras_datos_abiertos

#Devuelve una lista con todas las gasolineras del conjunto de datos abiertos
@bpclient.route('/gasolineras', methods=['GET'])
def get_gasolineras():
    datos_actualizados = get_datos_gasolineras_actualizadas()
    response = json_util.dumps(datos_actualizados)    
    return Response(response, mimetype='application/json')

#Devuelve una lista con las gasolineras de una localidad pasada por parametro
#Las gasolineras estan ordenadas segun el precio de la gasolina 95 (de mas barata a mas cara)
@bpclient.route('/gasolineras/gasolina95_low_cost', methods=['POST'])
def get_gasolineras_gasolina95_lowcost():
    localidad = request.json["localidad"]
    if localidad:
        datos_actualizados = get_datos_gasolineras_actualizadas()
        gasolineras_lowcost = datos_abiertos.get_gasolineras_gasolina95_lowcost_localidad(localidad, datos_actualizados)
        response = json_util.dumps(gasolineras_lowcost) 
        if response == '[]':
            return not_found("No se han encontrado gasolineras en " + localidad)
        else:     
            return Response(response, mimetype='application/json')
    else:
        return not_found("No se ha especificado una localidad")
    
# Devuelve una lista de gasolineras de un rango X en km de una ubicación pasada por parámetro o la ubicación real
@bpclient.route('/gasolineras/rango', methods=['POST'])
def get_gasolineras_rango():  
    #PRUEBA
    '''
    {
        "latitude": 36.73428,
        "longitude": -4.56591,
        "rango": 5
    }
    '''
    latitude = None
    longitude = None

    try : 
        latitude = request.json["latitude"]
        longitude = request.json["longitude"]
    except :
        print("Latitud y longitud no introducidas")

    rango_km = float(request.json["rango"])
    consulta = None

    rango = rango_km / 111.12  # Paso de km a grados

    gasolineras_actualizadas = get_datos_gasolineras_actualizadas()
    # Si no le pasa ubicacion por parametro se pasa None en los campos para que calcule la ubicacion actual
    if latitude and longitude:
        consulta = datos_abiertos.get_gasolineras_ubicacion(gasolineras_actualizadas, latitude, longitude, rango)
    else:
        consulta = datos_abiertos.get_gasolineras_ubicacion(gasolineras_actualizadas, None, None, rango)
    
    response = json_util.dumps(consulta)

    # Controla los errores
    if response == '[]':
        return not_found("No hay gasolineras en el rango de " + str(rango_km) +" kms")
    else:
        return Response(response, mimetype='application/json')
    
# Devuelve las gasolineras abiertas 24 horas de una provincia pasada por parametro
@bpclient.route('/gasolineras/provincia_24_horas', methods=['POST'])
def get_gasolineras_provincia_24horas():
    # PRUEBA
    '''
    {
        "Provincia" : "Málaga"
    }
    '''
    provincia = request.json["Provincia"]
    if provincia:
        gasolineras_actualizadas = get_datos_gasolineras_actualizadas()
        consulta = datos_abiertos.get_gasolineras_24horas(gasolineras_actualizadas, provincia)
        response = json_util.dumps(consulta)
        
        if response == '[]':
            return not_found("No se han encontrado gasolineras abiertas 24 horas en " + provincia)
        else:
            return Response(response, mimetype='application/json')  
    else:
        return not_found("No se ha indicado una provincia")  
    
# ---------------------------------------------FIN DATOS ABIERTOS-----------------------------------------------------------
