from mongoDB import trayecto_db
from bson import json_util
from bson.objectid import ObjectId

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
            "fecha": fecha,
            "hora": hora,
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
            "fecha": fecha,
            "hora": hora,
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