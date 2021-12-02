from mongoDB import trayecto_db
from bson import json_util
from bson.objectid import ObjectId

def find_trayectos():
    trayectos = trayecto_db.find()
    return trayectos

def find_trayecto(id):
    trayecto = trayecto_db.find_one({'_id': ObjectId(id)})
    return trayecto
