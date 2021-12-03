from mongoDB import vehiculo_db
from bson import json_util
from bson.objectid import ObjectId

def find_vehiculos():
    vehiculos = vehiculo_db.find()
    return vehiculos 

def find_vehiculo(id):
    vehiculo = vehiculo_db.find_one({'_id': ObjectId(id)})
    return vehiculo

def create_vehiculo(marca, modelo, matricula, color, plazas, fotos):
    id = vehiculo_db.insert_one({"marca": marca, "modelo": modelo, "matricula": matricula, "color": color,"plazas": plazas, "fotos_vehiculo": fotos})