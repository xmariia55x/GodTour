from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
import pymongo
import sys
from bson import json_util
from bson.objectid import ObjectId
from werkzeug.wrappers import response
import datos_abiertos
from datetime import datetime, timedelta

app = Flask(__name__)	
client = pymongo.MongoClient("mongodb+srv://Gestionpymongo:Gestionpymongo@cluster0.iixvr.mongodb.net/iweb?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = client.get_default_database()
# -- ESTO ES PARA LOCAL --
# app.config['MONGO_URI'] = 'mongodb://localhost/pythonmongodb'
# mongo = PyMongo(app)

# Este código sirve para sacar los datos del link, en este caso es un GeoJSON.
@app.route('/pruebaGeoJSON', methods=['GET'])
def buscaSpain():
    return datos_abiertos.get_datos_abiertos()

# -----------------------------------------------------USUARIO-------------------------------------------------------------
# Obtengo la colección de usuarios
usuario_db = db['Usuario']

# Obtiene la lista de usuarios
@app.route('/usuario', methods=['GET'])
def get_usuarios():
    usuarios = usuario_db.find()
    response = json_util.dumps(usuarios)
    return Response(response, mimetype='application/json')

# Obtiene un usuario con el id que se le pasa por parámetro
@app.route('/usuario/<id>', methods=['GET'])
def get_usuario(id):
    usuario = usuario_db.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(usuario)
    return Response(response, mimetype='application/json')

# Inserta un usuario 
@app.route('/usuario/create', methods=['POST'])
def create_usuario():
    nombre_completo = request.json['nombre_completo']
    correo = request.json['correo']
    dni = request.json['dni']
    fecha_nacimiento = request.json['fecha_nacimiento']
    antiguedad_permiso = request.json['antiguedad_permiso']
    foto_perfil = request.json['foto_perfil']
    permiso_conduccion = request.json['permiso_conduccion']
    valoracion_media = 0

    if nombre_completo and correo and dni and fecha_nacimiento:
        id = usuario_db.insert_one(
            {
             "nombre_completo": nombre_completo,
             "correo": correo,
             "dni": dni,
             "fecha_nacimiento": fecha_nacimiento,
             "antiguedad_permiso": antiguedad_permiso,
             "foto_perfil": foto_perfil,
             "permiso_conduccion": permiso_conduccion,
             "valoracion_media": valoracion_media
            }
        )
        response = {
            "id": str(id),
            "nombre_completo": nombre_completo,
            "correo": correo,
            "dni": dni,
            "fecha_nacimiento": fecha_nacimiento,
            "antiguedad_permiso": antiguedad_permiso,
            "foto_perfil": foto_perfil,
            "permiso_conduccion": permiso_conduccion,
            "valoracion_media": valoracion_media
        }
        
        return response
    else:
        return {"message":"error"}

# Borra un usuario
@app.route('/usuario/delete/<id>', methods=['DELETE'])
def delete_usuario(id):
    usuario_db.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message': 'El usuario con id '+id+' se ha eliminado exitosamente'})
    return response

#Updatea un usuario
@app.route('/usuario/update/<id>', methods=['PUT'])
def update_usuario(id):
    nombre_completo = request.json['nombre_completo']
    correo = request.json['correo']
    dni = request.json['dni']
    fecha_nacimiento = request.json['fecha_nacimiento']
    antiguedad_permiso = request.json['antiguedad_permiso']
    foto_perfil = request.json['foto_perfil']
    permiso_conduccion = request.json['permiso_conduccion']
    valoracion_media = request.json['valoracion_media']

    if nombre_completo and correo and dni and fecha_nacimiento:
        filter = {"_id": ObjectId(id)}
        new_values = {"$set":{
            "nombre_completo": nombre_completo,
            "correo": correo,
            "dni": dni,
            "fecha_nacimiento": fecha_nacimiento,
            "antiguedad_permiso": antiguedad_permiso,
            "foto_perfil": foto_perfil,
            "permiso_conduccion": permiso_conduccion,
            "valoracion_media": valoracion_media
        }}
        
        usuario_db.update_one(filter, new_values) 

        response = jsonify({'message': 'El usuario con id '+id+' se ha actualizado exitosamente'})
        
        return response
    else:
        return {"message":"error"}

# Obtiene los usuarios ordenados alfabeticamente, orden ascendente -> python.ASCENDING , orden descendente -> python.DESCENDING
@app.route('/usuario/byname', methods=['GET'])
def get_usuario_ordered_by_name():
    usuarios = usuario_db.find().sort("nombre_completo", pymongo.ASCENDING)
    response = json_util.dumps(usuarios)
    return Response(response, mimetype='application/json')

# Obtiene un usuario a partir de (parte de) su correo electronico 
@app.route('/usuario/byemail', methods=['POST'])
def get_usuario_by_email():
    email = request.json['correo']
    usuarios = usuario_db.find( { 'correo': { "$regex": email + '.*', "$options" :'i' }} )
    response = json_util.dumps(usuarios)
    return Response(response, mimetype='application/json')


# ---------------------------------------------FIN USUARIO-----------------------------------------------------------

# Javi yo hago los métodos IMPARES lista Trayecto, inserta trayecto, delte trayecto y tu los PARES trayectoId,update trayecto
# Son más o menos las mismas líneas de código a ojo =)

# ---------------------------------------------INICIO TRAYECTO-----------------------------------------------------------

# Obtengo la colección de trayectos
trayecto_db = db['Trayecto']

# Obtiene la lista de trayectos
@app.route('/trayecto', methods=['GET'])
def get_trayectos():
    trayectos = trayecto_db.find()
    response = json_util.dumps(trayectos)
    return Response(response, mimetype='application/json')

# TODO (JAVI)
# Obtiene un trayecto con el id que se le pasa por parámetro 
@app.route('/trayecto/<id>', methods=['GET'])
def get_trayecto(id):
    trayecto = trayecto_db.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(trayecto)
    return Response(response, mimetype='application/json')


# Inserta un trayecto
@app.route('/trayecto/create', methods=["POST"])
def create_trayecto():
    destino= request.json['destino']
    duracion= int(request.json['duracion'])
    fecha= request.json['fecha']
    hora= request.json['hora']
    origen= request.json['origen']
    periodicidad= request.json['periodicidad']
    precio= float(request.json['precio'])
    fotos_opcionales= request.json['fotos_opcionales']
    plazas_totales= int(request.json['plazas_totales'])
    vehiculo= request.json['vehiculo']
    creador= request.json['creador']

    if creador and destino and fecha and hora and precio and plazas_totales and vehiculo:
        id=trayecto_db.insert_one({
            "creador": creador,
            "destino":destino,
            "duracion":duracion,
            "fecha":fecha,
            "hora":hora,
            "origen":origen,
            "periodicidad":periodicidad,
            "precio":precio,
            "fotos_opcionales":fotos_opcionales,
            "plazas_totales":plazas_totales,
            "vehiculo":vehiculo, 
            "pasajeros": []
        })
        response = {
            "id":str(id),
            "creador":creador,
            "destino":destino,
            "duracion":duracion,
            "fecha":fecha,
            "hora":hora,
            "origen":origen,
            "periodicidad":periodicidad,
            "precio":precio,
            "fotos_opcionales":fotos_opcionales,
            "plazas_totales":plazas_totales,
            "vehiculo":vehiculo, 
            "pasajeros": []
        }
        return response
    else:
        return {"message":"error"}


# Borra un trayecto
@app.route('/trayecto/delete/<id>', methods=['DELETE'])
def delete_trayecto(id):
    trayecto_db.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message': 'El trayecto con id '+id+' se ha eliminado exitosamente'})
    return response

# (JAVI)
#Updatea un trayecto 

@app.route('/trayecto/update/<id>', methods=['PUT'])
def update_trayecto(id):
    destino = request.json['destino']
    duracion= int(request.json['duracion'])
    fecha = request.json['fecha']
    hora = request.json['hora']
    origen = request.json['origen']
    periodicidad = request.json['periodicidad']
    precio= float(request.json['precio'])
    fotos_opcionales = request.json['fotos_opcionales']
    plazas_totales= int(request.json['plazas_totales'])
    vehiculo = request.json['vehiculo']
    pasajeros = request.json['pasajeros']

    if destino and fecha and hora and precio and plazas_totales and vehiculo:
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
            "vehiculo": vehiculo, 
            "pasajeros": pasajeros
        }}
        
        trayecto_db.update_one(filter, new_values) 

        response = jsonify({'message': 'El trayecto con id '+id+' se ha actualizado exitosamente'})
        
        return response
    else:
        return {"message":"error"}

# Obtiene los trayectos cuyo destino se le pasa por parámetro 
@app.route('/trayecto/bydestino/<destino>', methods=['GET'])
def get_trayecto_destino(destino):
    trayecto = trayecto_db.find({'destino': destino})
    response = json_util.dumps(trayecto)
    return Response(response, mimetype='application/json')

# Obtiene los trayectos que tienen como origen y destino los indicados. Ej trayectos de Malaga a Cadiz
@app.route('/trayecto/byorigenanddestino/<origen>/<destino>', methods=['GET'])
def get_trayecto_origen_destino(origen, destino):
    trayecto = trayecto_db.find({'origen': origen}, {'destino': destino})
    response = json_util.dumps(trayecto)
    return Response(response, mimetype='application/json')

# Obtiene los trayectos que cuesten menos que la cantidad indicada
@app.route('/trayecto/byprecio/<precio>', methods=['GET'])
def get_trayecto_precio(precio):
    trayecto = trayecto_db.find({'precio': { "$lt" : precio }})
    response = json_util.dumps(trayecto)
    return Response(response, mimetype='application/json')

# Obtiene los usuarios de un trayecto a partir del id del trayecto
@app.route('/usuario/bytrayecto/<id>', methods=['GET'])
def get_usuario_trayecto(id):
    trayecto = trayecto_db.find_one({'_id': ObjectId(id)})
    pasajeros = trayecto.get("pasajeros")
    response = json_util.dumps(pasajeros)
    return Response(response, mimetype='application/json')

# ---------------------------------------------FIN TRAYECTO-----------------------------------------------------------


# --------------------------------------------- DATOS ABIERTOS - GASOLINERA -----------------------------------------------------------
@app.route('/gasolineras', methods=['GET'])
def get_gasolineras():
    return datos_abiertos.descargar_gasolineras()

@app.route('/gasolineras/gasolina95_lowcost', methods=['POST'])
def get_gasolineras_gasolina95_lowcost():
    # Devuelve una lista de las gasolineras de una ubicacion ordenada por el precio de la gasolina 95
    return datos_abiertos.get_gasolineras_ubicacion(ubicacion)

@app.route('/gasolineras/rango', methods=['POST'])
def get_gasolineras_rango(): 
    # Devuelve una lista de gasolineras de un rango X de una ubicación pasada por parámetro o la ubicación real
    #PRUEBA
    '''
    {
        "latitude": 36.73428,
        "longitude": -4.56591,
        "rango": 0.1
    }
    '''
    latitude = request.json["latitude"]
    longitude = request.json["longitude"]
    rango = request.json["rango"]
    lista = None
    if rango:
        if latitude and longitude:
            lista = datos_abiertos.get_gasolineras_ubicacion(get_gasolineras(), latitude, longitude, rango)
        else:
            lista = datos_abiertos.get_gasolineras_ubicacion(get_gasolineras(), None, None, rango)
        
        response = {
            "consulta": lista
        }
        return response

    else:
        return {"message":"error"}

@app.route('/gasolineras/provincia_24horas', methods=['POST'])
def get_gasolineras_provincia_24horas():
    # Devuelve las gasolineras abiertas 24 horas de una provincia pasada por parametro
    provincia = request.json["Provincia"]

    if provincia:
        lista = datos_abiertos.get_gasolineras_24horas(get_gasolineras(), provincia)
        response = {
            "consulta": lista
        }
        return response
    else:
        return {"message":"error"}
# ---------------------------------------------FIN DATOS ABIERTOS-----------------------------------------------------------



app.run()

client.close()