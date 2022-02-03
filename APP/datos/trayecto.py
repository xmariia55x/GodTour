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

def create_trayecto(creador, origen_nombre, origen_latitud, origen_longitud, destino_nombre, 
                                               destino_latitud, destino_longitud, fecha, hora, duracion, periodicidad, precio, 
                                               fotos_opcionales, plazas_totales, vehiculo):
    lista_fotos_trayecto = []
    for foto in fotos_opcionales:
        lista_fotos_trayecto.append(foto)
    trayecto_db.insert_one(
        {
            "creador": ObjectId(creador),
            "destino": 
                {"nombre": destino_nombre, 
                 "latitud": float(destino_latitud),
                 "longitud": float(destino_longitud)
                },
            "duracion": int(duracion),
            "timestamp": float(date_converter.date_to_timestamp(fecha, hora)),
            "origen":
                {"nombre": origen_nombre, 
                 "latitud": float(origen_latitud),
                 "longitud": float(origen_longitud)
                },
            "periodicidad": int(periodicidad),
            "precio": float(precio),
            "fotos_opcionales": lista_fotos_trayecto,
            "plazas_totales": int(plazas_totales),
            "vehiculo": ObjectId(vehiculo), 
            "pasajeros": []
        })

def update_trayecto(id, origen_nombre, origen_latitud, origen_longitud, destino_nombre, destino_latitud, destino_longitud,
                    fecha, hora, duracion, periodicidad, precio, fotos_opcionales, plazas_totales, vehiculo, pasajeros):
    filter = {"_id": ObjectId(id)}
    
    lista_fotos_trayecto = []
    for foto in fotos_opcionales:
        lista_fotos_trayecto.append(foto)

    new_values = {"$set":{
            "destino": 
                {"nombre": destino_nombre, 
                 "latitud": float(destino_latitud),
                 "longitud": float(destino_longitud)
                },
            "duracion": int(duracion),
            "timestamp": float(date_converter.date_to_timestamp(fecha, hora)),
            "origen":
                {"nombre": origen_nombre, 
                 "latitud": float(origen_latitud),
                 "longitud": float(origen_longitud)
                },
            "periodicidad": int(periodicidad),
            "precio": float(precio),
            "fotos_opcionales": lista_fotos_trayecto,
            "plazas_totales": int(plazas_totales),
            "vehiculo": ObjectId(vehiculo), 
            "pasajeros": pasajeros
    }}
        
    result = trayecto_db.update_one(filter, new_values)
    return result


def delete_trayecto(id):
    result = trayecto_db.delete_one({'_id': ObjectId(id)})
    return result

def add_pasajero(idTrayecto, idPasajero):
    trayecto = find_trayecto(idTrayecto)
    pasajeros = trayecto["pasajeros"]
    pasajeros.append(ObjectId(idPasajero))
    filter = {"_id": ObjectId(idTrayecto)}
    
    new_values = {"$set":{
            "pasajeros": pasajeros
    }}
        
    result = trayecto_db.update_one(filter, new_values)
    return result


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
    trayectos = trayecto_db.find({'destino.nombre': { "$regex": destino + '.*', "$options" :'i' }})
    return trayectos

def get_trayectos_by_origen(origen):
    trayectos = trayecto_db.find({'origen.nombre': { "$regex": origen + '.*', "$options" :'i' }})
    return trayectos

def get_trayectos_by_origen_destino(origen, destino):
    trayectos = trayecto_db.find({'destino.nombre': { "$regex": destino + '.*', "$options" :'i' }, "origen.nombre":  { "$regex": origen + '.*', "$options" :'i' }})
    return trayectos

def get_trayectos_by_precio(precio):
    try:
        trayectos = trayecto_db.find({'precio': {"$lte": float(precio) }})
    except:
        trayectos = None
    return trayectos

def get_usuarios_by_trayecto(id):
    trayecto = find_trayecto(id)
    # Alomejor habrá que castear a ObjectId
    lista_usuarios = trayecto.get("pasajeros")
    lista_oid = []
    for x in lista_usuarios:
        lista_oid.append(ObjectId(x))
    usuarios = usuario_db.find({'_id': {"$in" : lista_oid}})
    return usuarios

# Devuelve los trayectos que un usuario es propietario

def get_trayectos_of_usuario(id):
    trayectos = trayecto_db.find({'creador':ObjectId(id)})
    return trayectos


def get_trayectos_of_not_usuario(id):
    trayectos = trayecto_db.find({'creador': { "$ne": ObjectId(id)}})
    return trayectos

# Devuelve los trayectos donde un usuario es pasajero
# Se le pasa el id de usuario
# Hay que comprobar
def get_trayectos_usuario_pasajero(id):
    todos_trayectos = find_trayectos()
    lista_trayectos = [] 
    for t in todos_trayectos:
        if ObjectId(id) in t.get("pasajeros"):
            lista_trayectos.append(t)
    #id_buscar = str(ObjectId(id))
    #trayectos=trayecto_db.find({'pasajeros' : {"$in" : id_buscar}})
    return lista_trayectos

#Elimina al usuario del trayecto especificado con dicho id
def delete_pasajero_trayecto(id_trayecto, id_pasajero):
    trayecto = find_trayecto(id_trayecto)
    pasajeros = trayecto.get("pasajeros")
    pasajeros.remove(ObjectId(id_pasajero))
    filter = {"_id": ObjectId(id_trayecto)}

    new_values = {"$set":{ 
            "pasajeros": pasajeros
    }}
    trayecto_db.update_one(filter, new_values)

def get_trayectos_composedQuery(lista):
    
    results = trayecto_db.find({'$and': lista})
   
    return results

def delete_trayecto_vehiculo(id_vehiculo):
    result = trayecto_db.delete_many({'vehiculo': ObjectId(id_vehiculo)})
    return result

def get_trayectos_by_vehiculo(id_vehiculo):
    trayectos = trayecto_db.find({'vehiculo': ObjectId(id_vehiculo)})
    return trayectos