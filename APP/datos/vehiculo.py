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
    lista_fotos_vehiculo = []
    if fotos:
        for foto in fotos:
            lista_fotos_vehiculo.append(foto)
    id = vehiculo_db.insert_one({"marca": marca, "modelo": modelo, "matricula": matricula, "color": color,"plazas": plazas, "fotos_vehiculo": lista_fotos_vehiculo})
    return id.inserted_id

def update_vehiculo(id, marca, modelo, matricula, color, plazas, fotos_vehiculo):
    lista_fotos_vehiculo = []
    if fotos_vehiculo:
        for foto in fotos_vehiculo:
            lista_fotos_vehiculo.append(foto)
                    
    filter = {"_id": ObjectId(id)}
    new_values = {"$set":{
        "marca": marca,
        "modelo": modelo,
        "matricula": matricula,
        "color": color,
        "plazas": plazas,
        "fotos_vehiculo": lista_fotos_vehiculo
    }}
  
    result = vehiculo_db.update_one(filter, new_values) 

    if result.matched_count == 0:
        return "Fallo"
    else:
        return "Acierto"

def delete_vehiculo(id):
    vehiculo_db.delete_one({'_id': ObjectId(id)})


