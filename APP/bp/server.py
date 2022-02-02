from logging import NullHandler
from flask import Flask, request, jsonify, Response, Blueprint
from flask_pymongo import PyMongo
import pymongo
import sys
from bson import json_util
from bson.objectid import ObjectId
from pymongo import message
from werkzeug.wrappers import response
import datos.datos_abiertos as datos_abiertos
from datetime import datetime, timedelta
# from app import ultima_actualizacion_gasolineras

#Importamos los metodos para las fechas
import fechas as date_converter
#Importamos las entidades
import datos.trayecto as trayecto_data
import datos.usuario as usuario_data
import datos.vehiculo as vehiculo_data

bpserver = Blueprint('bpserver', __name__)
# -----------------------------------------------------USUARIO-------------------------------------------------------------
#Devuelve una lista con los usuarios ordenados alfabeticamente o con los usuarios cuyo email o parte del mismo coincide
@bpserver.route('/api/usuarios', methods=['GET'])
def get_usuarios():

    email = request.args.get("email")
    if len(request.args) == 0:
        usuarios = usuario_data.find_usuarios.sort("nombre_completo", pymongo.ASCENDING)
    else:
        if email:
            usuarios = usuario_data.find_usuarios_by_email(email)
        else:
            return not_found("Parámetros introducidos no válidos")

    response = json_util.dumps(usuarios)
    if response == "[]":
        return not_found("No se han encontrado usuarios")
    else:
        return Response(response, mimetype='application/json')

#Devuelve un usuario cuyo id coincide con el que se pasa por parámetro
@bpserver.route('/api/usuarios/<id>', methods=['GET'])
def get_usuario(id):
    usuario = usuario_data.find_usuario(id)
    
    if usuario is None:
        return not_found("No se han encontrado usuarios con el id: " + id)
    else: 
        response = json_util.dumps(usuario)    
        return Response(response, mimetype='application/json')

#Crea un nuevo usuario
@bpserver.route('/api/usuarios', methods=['POST'])
def create_usuario():
    nombre_completo = request.json.get('nombre_completo')
    correo = request.json.get('correo')
    dni = request.json.get('dni')
    fecha_nacimiento = request.json.get('fecha_nacimiento')
    antiguedad_permiso = request.json.get('antiguedad_permiso')
    foto_perfil = request.json.get('foto_perfil')
    valoracion_media = 0

    if nombre_completo and correo and dni and fecha_nacimiento:
        id = usuario_data.create_usuario(nombre_completo,correo,dni,fecha_nacimiento,antiguedad_permiso,foto_perfil,valoracion_media) 

        if id is None:
             return not_found("No se hapodido crear el usuario")

        response = {
            "id": str(id),
            "nombre_completo": nombre_completo,
            "correo": correo,
            "dni": dni,
            "fecha_nacimiento": fecha_nacimiento,
            "antiguedad_permiso": antiguedad_permiso,
            "foto_perfil": foto_perfil,
            "valoracion_media": valoracion_media,
            "vehiculos" : []
        }
        return response
    else:
        return not_found("No se ha podido crear el usuario")

#Elimina un usuario cuyo id coincide con el que se pasa por parametro
@bpserver.route('/api/usuarios/<id>', methods=['DELETE'])
def delete_usuario(id):
    usuario_data.delete_usuario(id)
    response = jsonify({'message': 'El usuario con id '+id+' se ha eliminado exitosamente'})
    return response

#Actualiza la informacion del usuario cuyo id coincide con el que se pasa por parametro
@bpserver.route('/api/usuarios/<id>', methods=['PUT'])
def update_usuario(id):
    nombre_completo = request.json.get('nombre_completo')
    correo = request.json.get('correo')
    dni = request.json.get('dni')
    fecha_nacimiento = request.json.get('fecha_nacimiento')
    antiguedad_permiso = request.json.get('antiguedad_permiso')
    foto_perfil = request.json.get('foto_perfil')
    valoracion_media = request.json.get('valoracion_media')

    if nombre_completo and correo and dni and fecha_nacimiento:     
        usuario_data.update_usuario(nombre_completo,correo,dni,fecha_nacimiento,antiguedad_permiso,foto_perfil,valoracion_media)
        response = jsonify({'message': 'El usuario con id '+id+' se ha actualizado exitosamente'})
        
        return response
    else:
        return not_found("No se ha podido actualizar el usuario con el id: " + id)
# ---------------------------------------------FIN USUARIO-----------------------------------------------------------

# ---------------------------------------------INICIO TRAYECTO-----------------------------------------------------------
#Devuelve una lista de trayectos
@bpserver.route('/api/trayectos', methods=['GET'])
def get_trayectos():
    origen = request.args.get("origen")
    destino = request.args.get("destino")
    precio = request.args.get("precio")

    if len(request.args) == 0:
        trayectos = trayecto_data.find_trayectos()
    else:
        if origen and destino and origen!="" and destino!="":
            trayectos = trayecto_data.get_trayectos_by_origen_destino(origen, destino)
        elif origen and origen != "":
            trayectos = trayecto_data.get_trayectos_by_origen(origen)
        elif destino and destino != "":
            trayectos = trayecto_data.get_trayectos_by_destino(destino)
        elif precio and precio != "":
            trayectos = trayecto_data.get_trayectos_by_precio(precio)
        else:
            return not_found("Parámetros introducidos no válidos")

    response = json_util.dumps(trayectos)
    if response == "[]":
        return not_found("No se han encontrado trayectos")
    else:
        return Response(response, mimetype='application/json')

#Devuelve un trayecto cuyo id coincide con el que se pasa por parámetro
@bpserver.route('/api/trayectos/<id>', methods=['GET'])
def get_trayecto(id):
    trayecto = trayecto_data.find_trayecto(id)

    if trayecto is None:
        return not_found("No se han encontrado trayectos con el id: " + id)
    else:
        response = json_util.dumps(trayecto)
        return Response(response, mimetype='application/json')

#Crea un nuevo trayecto
@bpserver.route('/api/trayectos', methods=["POST"])
def create_trayecto():
    creador = request.json.get('creador')
    destino_nombre = request.json.get('destino_nombre')
    destino_latitud = request.json.get('destino_latitud')
    destino_longitud = request.json.get('destino_longitud')
    duracion = request.json.get('duracion')
    fecha = date_converter.formatear_fecha(request.json.get('fecha'), "%d/%m/%Y", "%Y-%m-%d")
    hora = request.json.get('hora')
    origen_nombre = request.json.get('origen_nombre')
    origen_latitud = request.json.get('origen_latitud')
    origen_longitud = request.json.get('origen_longitud')
    periodicidad = request.json.get('periodicidad')
    precio = request.json.get('precio')
    fotos_opcionales = request.json.get('fotos_opcionales')
    plazas_totales = request.json.get('plazas_totales')
    vehiculo = request.json.get('vehiculo')
    #Cuidado con destino y origen que ya no se llaman asi 
    if creador and destino_nombre and destino_latitud and destino_longitud and origen_nombre and origen_latitud and origen_longitud and fecha and hora and precio and plazas_totales and vehiculo:
        id = trayecto_data.create_trayecto(creador, origen_nombre, origen_latitud, origen_longitud, destino_nombre, 
                                               destino_latitud, destino_longitud, fecha, hora, duracion, periodicidad, precio, 
                                               fotos_opcionales, plazas_totales, vehiculo)
        response = {
            "id":str(id),
            "creador":creador,
            "destino": 
                {
                 "nombre": destino_nombre,
                 "latitud": destino_latitud,
                 "longitud": destino_longitud
                },
            "duracion":duracion,
            "fecha":fecha,
            "hora":hora,
            "origen":
                {
                 "nombre": origen_nombre,
                 "latitud": origen_latitud,
                 "longitud": origen_longitud
                },
            "periodicidad":periodicidad,
            "precio":precio,
            "fotos_opcionales":fotos_opcionales,
            "plazas_totales":plazas_totales,
            "vehiculo":vehiculo, 
            "pasajeros": []
        }
        return response
    else:
        return not_found("No se ha podido crear el trayecto")

#Elimina un trayecto cuyo id coincide con el que se pasa por parametro
@bpserver.route('/api/trayectos/<id>', methods=['DELETE'])
def delete_trayecto(id):
    result = trayecto_data.delete_trayecto(id)

    if result.deleted_count == 0:
        return not_found("No se han encontrado trayectos con id "+ id)
    else:
        response = jsonify({'message': 'El trayecto con id '+id+' se ha eliminado exitosamente'})
        return response

#Actualiza la informacion del trayecto cuyo id coincide con el que se pasa por parametro
@bpserver.route('/api/trayectos/<id>', methods=['PUT'])
def update_trayecto(id):
    destino_nombre = request.json.get('destino_nombre')
    destino_latitud = request.json.get('destino_latitud')
    destino_longitud = request.json.get('destino_longitud')
    duracion= request.json.get('duracion')
    fecha = date_converter.formatear_fecha(request.json.get('fecha'), "%d/%m/%Y", "%Y-%m-%d")
    hora = request.json.get('hora')
    origen_nombre = request.json.get('origen_nombre')
    origen_latitud = request.json.get('origen_latitud')
    origen_longitud = request.json.get('origen_longitud')
    periodicidad = request.json.get('periodicidad')
    precio= request.json.get('precio')
    fotos_opcionales = request.json.get('fotos_opcionales')
    plazas_totales= request.json.get('plazas_totales')
    vehiculo = request.json.get('vehiculo')
    pasajeros = request.json.get('pasajeros')

    lista_pasajeros = []
    #Cuidado con destino y origen que ya no se llaman asi 
    if destino_nombre and destino_latitud and destino_longitud and origen_nombre and origen_latitud and origen_longitud and fecha and hora and precio and plazas_totales and vehiculo:
        if pasajeros:
            for pasajero in pasajeros:
                lista_pasajeros.append(ObjectId(pasajero))
        
        result = trayecto_data.update_trayecto(id, origen_nombre, origen_latitud, origen_longitud, destino_nombre, destino_latitud, destino_longitud, 
                                               fecha, hora, duracion, periodicidad, precio, fotos_opcionales, plazas_totales, vehiculo, pasajeros)

        if result.matched_count == 0:
            return not_found("No se ha encontrado el trayecto con id " +id)
        else:
            response = jsonify({'message': 'El trayecto con id '+id+' se ha actualizado exitosamente'})
            return response
    else:
        return not_found("No se ha podido actualizar el trayecto con id: " + id)

#Devuelve los usuarios de un trayecto a partir del id del trayecto indicado por parametro
@bpserver.route('/api/trayectos/<id>/usuarios', methods=['GET'])
def get_usuario_trayecto(id):
    lista_pasajeros = trayecto_data.get_usuarios_by_trayecto(id)
    if lista_pasajeros is None:
        return not_found("El trayecto con id: " + id + " no tiene usuarios")
    else:
        response = json_util.dumps(lista_pasajeros)
        return Response(response, mimetype='application/json')

# ---------------------------------------------FIN TRAYECTO-----------------------------------------------------------
# ---------------------------------------------INICIO VEHICULO--------------------------------------------------------
#Devuelve una lista con los vehiculos
@bpserver.route('/api/vehiculos', methods=['GET'])
def get_vehiculos():
    vehiculos = vehiculo_data.find_vehiculos()
    response = json_util.dumps(vehiculos)
    if response == "[]":
        return not_found("No se han encontrado vehiculos")
    else:
        return Response(response, mimetype='application/json')

#Devuelve un vehiculo cuyo id coincide con el que se pasa por parámetro
@bpserver.route('/api/vehiculos/<id>', methods=['GET'])
def get_vehiculo(id):
    vehiculo = vehiculo_data.find_vehiculo(id)
    if vehiculo is None:
        return not_found("No se han encontrado vehiculos con el id: " + id)
    else: 
        response = json_util.dumps(vehiculo)    
        return Response(response, mimetype='application/json')

#Crea un nuevo vehiculo
@bpserver.route('/api/vehiculos', methods=['POST'])
def create_vehiculo():
    marca = request.json.get('marca')
    modelo = request.json.get('modelo')
    matricula = request.json.get('matricula')
    color = request.json.get('color')
    plazas = request.json.get('plazas')
    fotos = request.json.get('fotos_vehiculo')
    if marca and modelo and matricula and color and plazas:
        id = vehiculo_data.create_vehiculo(marca, modelo, matricula, color, plazas, fotos)

        response = {
            "id": str(id),
            "marca": marca,
            "modelo": modelo,
            "matricula": matricula,
            "color": color,
            "plazas": plazas
        }
        return response
    else:
        return not_found("No se ha podido crear el vehiculo, faltan campos")

#Elimina un vehiculo cuyo id coincide con el que se pasa por parametro
@bpserver.route('/api/vehiculos/<id>', methods=['DELETE'])
def delete_vehiculo(id):
    vehiculo_data.delete_vehiculo(id)
    response = jsonify({'message': 'El vehiculo con id '+id+' se ha eliminado exitosamente'})
    return response

#Actualiza la informacion del vehiculo cuyo id coincide con el que se pasa por parametro
@bpserver.route('/api/vehiculos/<id>', methods=['PUT'])
def update_vehiculo(id):
    marca = request.json.get('marca')
    modelo = request.json.get('modelo')
    matricula = request.json.get('matricula')
    color = request.json.get('color')
    plazas = request.json.get('plazas')
    fotos = request.json.get('fotos_vehiculo')
    if marca and modelo and matricula and color and plazas:     
        vehiculo_data.update_vehiculo(id, marca, modelo, matricula, color, plazas, fotos)
        response = jsonify({'message': 'El vehiculo con id '+id+' se ha actualizado exitosamente'})
        return response
    else:
        return not_found("No se ha podido actualizar el vehiculo con el id: " + id + " , faltan campos")
# ---------------------------------------------FIN VEHICULO-----------------------------------------------------------
# --------------------------------------------- DATOS ABIERTOS - TRAFICO ---------------------------------------------------------
#Devuelve una lista con las incidencias de trafico del conjunto de datos abiertos
@bpserver.route('/api/incidencias', methods=['GET'])
def get_trafico():
    provincia = request.args.get("provincia")
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    rango = request.args.get("rango")
    causa = request.args.get("causa")

    if provincia:
        datos_trafico = datos_abiertos.get_incidencias_provincia(provincia) #FUNCIONA
    elif causa and latitude and longitude and rango:
        datos_trafico = datos_abiertos.get_incidencias_causa(latitude, longitude, rango, causa) #FUNCIONA
    elif causa and rango:
        datos_trafico =  datos_abiertos.get_incidencias_causa(None, None, rango, causa) #FUNCIONA
    elif latitude and longitude and rango:                                  
        datos_trafico = datos_abiertos.get_incidencias_rango(latitude, longitude, rango) #FUNCIONA
    elif rango:
        datos_trafico = datos_abiertos.get_incidencias_rango(None, None, rango) #FUNCIONA
    else:
        datos_trafico = datos_abiertos.descargar_datos_trafico()  #FUNCIONA

    if not datos_trafico: 
        return not_found("No se han encontrado incidencias de trafico")
    else:    
        response = json_util.dumps(datos_trafico)
        return Response(response, mimetype='application/json')
# --------------------------------------------- FIN DATOS ABIERTOS - TRAFICO -------------------------------------------------------

# --------------------------------------------- DATOS ABIERTOS - GASOLINERA -----------------------------------------------------------
#Devuelve una lista con todas las gasolineras del conjunto de datos abiertos
@bpserver.route('/api/gasolineras', methods=['GET'])
def get_gasolineras():
    localidad = request.args.get("localidad")
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    rango = request.args.get("rango")
    provincia = request.args.get("provincia")
    municipio = request.args.get("municipio")
    if localidad:
        gasolineras = datos_abiertos.get_gasolineras_gasolina95_lowcost_localidad(localidad) #FUNCIONA
    elif municipio:
        gasolineras = datos_abiertos.get_gasolineras_gasolina95_lowcost_municipio(municipio) #FUNCIONA
    elif provincia:
        gasolineras = datos_abiertos.get_gasolineras_24horas(provincia) #FUNCIONA
    elif latitude and longitude and rango:
        gasolineras = datos_abiertos.get_gasolineras_ubicacion(latitude, longitude, rango) #FUNCIONA
    elif rango:
        gasolineras = datos_abiertos.get_gasolineras_ubicacion(None, None, rango) #FUNCIONA
    else:
        gasolineras = datos_abiertos.get_datos_gasolineras_actualizadas() #FUNCIONA
        
    if not gasolineras:    
        return not_found("No se han encontrado gasolineras") 
    else:
        response = json_util.dumps(gasolineras)    
        return Response(response, mimetype='application/json')

'''   
    "latitude": 36.73428,
    "longitude": -4.56591,
    "rango": 5
''' 
# ---------------------------------------------FIN DATOS ABIERTOS-----------------------------------------------------------

# ---------------------------------------------MANEJO DE ERRORES------------------------------------------------------------

#Error 400
@bpserver.errorhandler(400)
def not_found(error=None):
    if error is None:
        response = jsonify({
            'message': 'Bad request: ' + request.url,
            'status': 400
        })
    else:
        response = jsonify({
            'message': error,
            'status': 400
        })
    response.status_code = 400
    return response

#Error 404
@bpserver.errorhandler(404)
def not_found(error=None):
    if error is None : 
        response = jsonify({
        'message': 'Recurso no encontrado: ' + request.url,
        'status': 404
        })
    else: 
        response = jsonify({
        'message': error,
        'status': 404
        })
    response.status_code = 404
    return response

#Error 500
@bpserver.errorhandler(500)
def server_error(error):
    response = jsonify({
        'message': 'Error del servidor: ' + request.url,
        'status': 500
    })
    response.status_code = 500
    return response

# --------------------------------------------- FIN MANEJO DE ERRORES-----------------------------------------------------------