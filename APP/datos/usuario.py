from mongoDB import usuario_db, vehiculo_db
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime
import pymongo
import fechas as date_converter

def find_usuarios():
    usuarios = usuario_db.find()
    return usuarios

def find_usuario(id):
    usuario = usuario_db.find_one({'_id': ObjectId(id)})
    return usuario

def create_usuario(nombre_completo,correo,dni,fecha_nacimiento,antiguedad_permiso,
foto_perfil,valoracion_media):
    #Lo creamos porque necesitamos una hora
    hora = "00:00"
    if antiguedad_permiso is None:
        antiguedad = None
    else:    
        antiguedad = float(date_converter.date_to_timestamp(antiguedad_permiso, hora))
    id = usuario_db.insert_one(
        {
            "nombre_completo": nombre_completo,
            "correo": correo,
            "dni": dni,
            "fecha_nacimiento": float(date_converter.date_to_timestamp(fecha_nacimiento, hora)),
            "antiguedad_permiso": antiguedad,
            "foto_perfil": foto_perfil,
            "valoracion_media": valoracion_media
        }
    )

    return id


def update_usuario(id, nombre_completo, correo, dni, fecha_nacimiento, antiguedad_permiso, foto_perfil):
    #Lo creamos porque necesitamos una hora
    hora = "00:00"
    if antiguedad_permiso is None:
        antiguedad = None
    else:    
        antiguedad = float(date_converter.date_to_timestamp(antiguedad_permiso, hora))

    if foto_perfil != "": #El usuario pone una foto nueva
        filter = {"_id": ObjectId(id)}
        new_values = {"$set":{
            "nombre_completo": nombre_completo,
            "correo": correo,
            "dni": dni,
            "fecha_nacimiento": float(date_converter.date_to_timestamp(fecha_nacimiento, hora)),
            "antiguedad_permiso": antiguedad,
            "foto_perfil": foto_perfil,
            "valoracion_media": 0 #Cambiar cuando tengamos una tabla de valoraciones o algo
        }}
    else: #El usuario no modifica su foto actual
        filter = {"_id": ObjectId(id)}
        new_values = {"$set":{
            "nombre_completo": nombre_completo,
            "correo": correo,
            "dni": dni,
            "fecha_nacimiento": float(date_converter.date_to_timestamp(fecha_nacimiento, hora)),
            "antiguedad_permiso": antiguedad,
            "valoracion_media": 0 #Cambiar cuando tengamos una tabla de valoraciones o algo
        }}

    result = usuario_db.update_one(filter, new_values)
    if result.matched_count == 0:
        return "Fallo"
    else:
        return "Acierto"

def delete_usuario(id):
    usuario_db.delete_one({'_id': ObjectId(id)})

def add_vehiculo_to_usuario(id_usuario, vehiculos):
    filter = {"_id": ObjectId(id_usuario)}
    new_values = {"$set":{
            "vehiculos": vehiculos  }}
    result = usuario_db.update_one(filter, new_values)
    if result.matched_count == 0:
        return "Fallo"
    else:
        return "Acierto"

def delete_vehiculo_usuario(id_usuario, id_vehiculo):
    usuario_completo = usuario_db.find_one({'_id': ObjectId(id_usuario)})
    vehiculos = usuario_completo.get('vehiculos')
    vehiculos.remove(ObjectId(id_vehiculo))
    filter = {"_id": ObjectId(id_usuario)}
    new_values = {"$set":{
            "vehiculos": vehiculos  }}
    result = usuario_db.update_one(filter, new_values)
#----------QUERIES-------------

def find_usuario_by_email(email):
    usuario = usuario_db.find_one({ 'correo': { "$regex": email + '.*', "$options" :'i' }})
    return usuario

def find_usuarios_by_email(email):
    usuario = usuario_db.find({ 'correo': { "$regex": email + '.*', "$options" :'i' }})
    return usuario

def find_usuarios_ordered_by_name():
    usuarios = usuario_db.find().sort("nombre_completo", pymongo.ASCENDING)
    return usuarios

def find_vehiculos_usuario(id):
    usuario_completo = usuario_db.find_one({'_id': ObjectId(id)})
    vehiculos = usuario_completo.get('vehiculos')
    lista_vehiculos = []
    for vehiculo in vehiculos:
        lista_vehiculos.append(vehiculo_db.find_one({'_id': ObjectId(vehiculo)}))
    return lista_vehiculos

def find_vehiculos_usuario_by_id(id):
    usuario_completo = usuario_db.find_one({'_id': ObjectId(id)})
    vehiculos = usuario_completo.get('vehiculos')
    lista_vehiculos = []
    for vehiculo in vehiculos:
        lista_vehiculos.append(ObjectId(vehiculo_db.find_one({'_id': ObjectId(vehiculo)}).get('_id')))
    return lista_vehiculos

def delete_vehiculo_from_usuarios_list(id_vehiculo):
    usuarios = usuario_db.find()
    for usuario in usuarios:
       if ObjectId(id_vehiculo) in usuario.get('vehiculos'): 
        delete_vehiculo_usuario(usuario.get('_id'), id_vehiculo)
    