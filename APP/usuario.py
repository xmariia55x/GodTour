from mongoDB import usuario_db
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime
def find_usuarios():
    usuarios = usuario_db.find()
    return usuarios

def find_usuario(id):
    usuario = usuario_db.find_one({'_id': ObjectId(id)})
    return usuario