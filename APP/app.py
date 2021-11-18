from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
import pymongo
import sys
from bson import json_util
from bson.objectid import ObjectId
from werkzeug.wrappers import response

app = Flask(__name__)	
client = pymongo.MongoClient("mongodb+srv://Gestionpymongo:Gestionpymongo@cluster0.iixvr.mongodb.net/iweb?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = client.get_default_database()
# -- ESTO ES PARA LOCAL --
# app.config['MONGO_URI'] = 'mongodb://localhost/pythonmongodb'
# mongo = PyMongo(app)


@app.route('/')
def hello_world():
    return "Hello world"

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
# Obtiene un usuario con el id que se le pasa por parámetro (JAVI)


# Inserta un trayecto
@app.route('/trayecto/create', methods=["POST"])
def create_trayecto():
    destino= request.json['destino']
    duracion= request.json['duracion']
    fecha= request.json['fecha']
    hora= request.json['hora']
    origen= request.json['origen']
    periodicidad= request.json['periodicidad']
    precio= request.json['precio']
    fotos_opcionales= request.json['fotos_opcionales']
    plazas_totales= request.json['plazas_totales']
    vehiculo= request.json['vehiculo']
    creador= request.json['creador']

    if creador and destino and fecha and hora and precio :
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

# TODO (JAVI)
#Updatea un trayecto 


# ---------------------------------------------FIN TRAYECTO-----------------------------------------------------------

app.run()

client.close()