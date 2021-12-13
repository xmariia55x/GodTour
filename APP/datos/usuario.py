from mongoDB import usuario_db
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

def find_usuarios_by_email(email):
    usuario = usuario_db.find({ 'correo': { "$regex": email + '.*', "$options" :'i' }})
    return usuario

def find_usuarios_ordered_by_name():
    usuarios = usuario_db.find().sort("nombre_completo", pymongo.ASCENDING)
    return usuarios

def create_usuario(nombre_completo,correo,dni,fecha_nacimiento,antiguedad_permiso,
foto_perfil,valoracion_media):
        #Lo creamos porque necesitamos una hora
        hora = "00:00"
        id = usuario_db.insert_one(
            {
             "nombre_completo": nombre_completo,
             "correo": correo,
             "dni": dni,
             "fecha_nacimiento": float(date_converter.date_to_timestamp(fecha_nacimiento, hora)),
             "antiguedad_permiso": float(date_converter.date_to_timestamp(antiguedad_permiso, hora)),
             "foto_perfil": foto_perfil,
             "valoracion_media": valoracion_media
            }
        )

def update_usuario(id, nombre_completo, correo, dni, fecha_nacimiento, antiguedad_permiso, foto_perfil, valoracion_media):
    #Lo creamos porque necesitamos una hora
    hora = "00:00"
    filter = {"_id": ObjectId(id)}
    new_values = {"$set":{
        "nombre_completo": nombre_completo,
        "correo": correo,
        "dni": dni,
        "fecha_nacimiento": float(date_converter.date_to_timestamp(fecha_nacimiento, hora)),
        "antiguedad_permiso": float(date_converter.date_to_timestamp(antiguedad_permiso, hora)),
        "foto_perfil": foto_perfil,
        "valoracion_media": valoracion_media
    }}
        
    result = usuario_db.update_one(filter, new_values)
    if result.matched_count == 0:
        return "Fallo"
    else:
        return "Acierto"

def delete_usuario(id):
    usuario_db.delete_one({'_id': ObjectId(id)})