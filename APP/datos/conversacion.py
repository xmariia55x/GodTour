from mongoDB import trayecto_db
from mongoDB import usuario_db
from mongoDB import conversacion_db
from bson import json_util
from bson.objectid import ObjectId
import fechas as date_converter

def find_conversaciones():
    conversaciones = conversacion_db.find()
    return conversaciones

def find_conversacion(id):
    conversacion = conversacion_db.find_one({'_id': ObjectId(id)})
    return conversacion

def find_conversaciones_trayecto(id):
    conversaciones_trayecto = conversacion_db.find({'trayecto': ObjectId(id)})
    return conversaciones_trayecto

def find_conversaciones_autor(id):
    conversaciones_autor = conversacion_db.find({'autor': ObjectId(id)})
    return conversaciones_autor

def create_conversacion(trayecto, autor, texto, fecha, hora):
    trayecto_db.insert_one(
        {
            "trayecto": ObjectId(trayecto),
            "duracion": ObjectId(autor),
            "duracion": str(texto),
            "timestamp": float(date_converter.date_to_timestamp(fecha, hora)),
            })

def delete_conversacion(id):
    result = conversacion_db.delete_one({'_id': ObjectId(id)})
    return result

###################################################################################################################################
# QUERIES
###################################################################################################################################


