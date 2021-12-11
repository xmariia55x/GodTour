from mongoDB import trayecto_db
from mongoDB import usuario_db
from bson import json_util
from bson.objectid import ObjectId
import fechas as date_converter

def find_trayectos():
    trayectos = trayecto_db.find()
    return trayectos

def find_trayecto(id):
    trayecto = trayecto_db.find_one({'_id': ObjectId(id)})
    return trayecto

def find_trayectos_creador(id):
    trayectos_creador = trayecto_db.find({'creador': ObjectId(id)})
    return trayectos_creador

def create_trayecto(creador, origen_nombre, origen_latitud, origen_longitud, destino_nombre, destino_latitud, destino_longitud,
                    fecha, hora, duracion, periodicidad, precio, fotos_opcionales, plazas_totales, vehiculo, pasajeros):
    trayecto_db.insert_one(
        {
            "creador": ObjectId(creador),
            "destino": 
                {"nombre": destino_nombre, 
                 "latitud": destino_latitud,
                 "longitud": destino_longitud
                },
            "duracion": duracion,
            "timestamp": date_converter.date_to_timestamp(fecha, hora),
            "origen":
                {"nombre": origen_nombre, 
                 "latitud": origen_latitud,
                 "longitud": origen_longitud
                },
            "periodicidad": periodicidad,
            "precio": precio,
            "fotos_opcionales": fotos_opcionales,
            "plazas_totales": plazas_totales,
            "vehiculo": ObjectId(vehiculo), 
            "pasajeros": []
        })

def update_trayecto(id, origen_nombre, origen_latitud, origen_longitud, destino_nombre, destino_latitud, destino_longitud,
                    fecha, hora, duracion, periodicidad, precio, fotos_opcionales, plazas_totales, vehiculo):
    filter = {"_id": ObjectId(id)}

    new_values = {"$set":{
            "destino": 
                {"nombre": destino_nombre, 
                 "latitud": destino_latitud,
                 "longitud": destino_longitud
                },
            "duracion": duracion,
            "timestamp": date_converter.date_to_timestamp(fecha, hora),
            "origen": 
                {"nombre": origen_nombre, 
                 "latitud": origen_latitud,
                 "longitud": origen_longitud
                },
            "periodicidad": periodicidad,
            "precio": precio,
            "fotos_opcionales": fotos_opcionales,
            "plazas_totales": plazas_totales,
            "vehiculo": ObjectId(vehiculo), 
        }}
        
    result = trayecto_db.update_one(filter, new_values)


def delete_trayecto(id):
    trayecto_db.delete_one({'_id': ObjectId(id)})

'''
def update_restringido_trayecto(id, periodicidad, fotos_opcionales, plazas_totales, vehiculo):
    filter = {"_id": ObjectId(id)}
    new_values = {"$set":{
            "periodicidad": periodicidad,
            "fotos_opcionales": fotos_opcionales,
            "plazas_totales": plazas_totales,
            "vehiculo": ObjectId(vehiculo), 
        }}
        
    result = trayecto_db.update_one(filter, new_values)
'''

###################################################################################################################################
# QUERIES
###################################################################################################################################
def get_trayectos_by_destino(destino):
    trayectos = trayecto_db.find({'destino': destino})
    return trayectos

def get_trayectos_by_origen(origen):
    trayectos = trayecto_db.find({'origen': origen})
    return trayectos

def get_trayectos_by_origen_destino(origen, destino):
    trayectos = trayecto_db.find({'origen': origen, 'destino': destino})
    return trayectos

def get_trayectos_by_precio(precio):
    trayectos = trayecto_db.find({'precio': { "$lt" : precio }})
    return trayectos

def get_usuarios_by_trayecto(id):
    trayecto = find_trayecto(id)
    # Alomejor habrá que castear a ObjectId
    lista_usuarios = trayecto.get("pasajeros")
    usuarios = usuario_db.find({'_id': {"$in" : lista_usuarios}})
    
