from logging import NullHandler
from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
import pymongo
import sys
from bson import json_util
from bson.objectid import ObjectId
from pymongo import message
from werkzeug.wrappers import response
import datos_abiertos
from datetime import datetime, timedelta

ultima_actualizacion_gasolineras = 0
ultima_actualizacion_trafico = 0
class FlaskApp(Flask):
  def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
    if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
      with self.app_context():
        global gasolineras_datos_abiertos, ultima_actualizacion_gasolineras, trafico_datos_abiertos, ultima_actualizacion_trafico
        gasolineras_datos_abiertos = datos_abiertos.descargar_gasolineras() 
        ultima_actualizacion_gasolineras = datetime.now()
        trafico_datos_abiertos = datos_abiertos.descargar_datos_trafico()
        ultima_actualizacion_trafico = datetime.now()
    super(FlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)
app = FlaskApp(__name__)

client = pymongo.MongoClient("mongodb+srv://Gestionpymongo:Gestionpymongo@cluster0.iixvr.mongodb.net/iweb?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = client.get_default_database()

# -----------------------------------------------------USUARIO-------------------------------------------------------------
# Obtengo la colección de usuarios
usuario_db = db['Usuario']

#Devuelve una lista con los usuarios
@app.route('/usuario', methods=['GET'])
def get_usuarios():
    usuarios = usuario_db.find()
    response = json_util.dumps(usuarios)
    return Response(response, mimetype='application/json')

#Devuelve un usuario cuyo id coincide con el que se pasa por parámetro
@app.route('/usuario/<id>', methods=['GET'])
def get_usuario(id):
    usuario = usuario_db.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(usuario)
    if response == 'null':
        return not_found("No se han encontrado usuarios con el id: " + id)
    else:     
        return Response(response, mimetype='application/json')

#Crea un nuevo usuario
@app.route('/usuario/create', methods=['POST'])
def create_usuario():
    nombre_completo = request.json['nombre_completo']
    correo = request.json['correo']
    dni = request.json['dni']
    fecha_nacimiento = request.json['fecha_nacimiento']
    antiguedad_permiso = request.json['antiguedad_permiso']
    foto_perfil = request.json['foto_perfil']
    permiso_conduccion = request.json['permiso_conduccion']
    valoracion_media = 0

    if nombre_completo and correo and dni and fecha_nacimiento:
        id = usuario_db.insert_one(
            {
             "nombre_completo": nombre_completo,
             "correo": correo,
             "dni": dni,
             "fecha_nacimiento": fecha_nacimiento,
             "antiguedad_permiso": antiguedad_permiso,
             "foto_perfil": foto_perfil,
             "permiso_conduccion": permiso_conduccion,
             "valoracion_media": valoracion_media
            }
        )
        response = {
            "id": str(id),
            "nombre_completo": nombre_completo,
            "correo": correo,
            "dni": dni,
            "fecha_nacimiento": fecha_nacimiento,
            "antiguedad_permiso": antiguedad_permiso,
            "foto_perfil": foto_perfil,
            "permiso_conduccion": permiso_conduccion,
            "valoracion_media": valoracion_media
        }
        
        return response
    else:
        return not_found("No se ha podido crear un usuario")

#Elimina un usuario cuyo id coincide con el que se pasa por parametro
@app.route('/usuario/delete/<id>', methods=['DELETE'])
def delete_usuario(id):
    usuario_db.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message': 'El usuario con id '+id+' se ha eliminado exitosamente'})
    return response

#Actualiza la informacion del usuario cuyo id coincide con el que se pasa por parametro
@app.route('/usuario/update/<id>', methods=['PUT'])
def update_usuario(id):
    nombre_completo = request.json['nombre_completo']
    correo = request.json['correo']
    dni = request.json['dni']
    fecha_nacimiento = request.json['fecha_nacimiento']
    antiguedad_permiso = request.json['antiguedad_permiso']
    foto_perfil = request.json['foto_perfil']
    permiso_conduccion = request.json['permiso_conduccion']
    valoracion_media = request.json['valoracion_media']

    if nombre_completo and correo and dni and fecha_nacimiento:
        filter = {"_id": ObjectId(id)}
        new_values = {"$set":{
            "nombre_completo": nombre_completo,
            "correo": correo,
            "dni": dni,
            "fecha_nacimiento": fecha_nacimiento,
            "antiguedad_permiso": antiguedad_permiso,
            "foto_perfil": foto_perfil,
            "permiso_conduccion": permiso_conduccion,
            "valoracion_media": valoracion_media
        }}
        
        usuario_db.update_one(filter, new_values) 

        response = jsonify({'message': 'El usuario con id '+id+' se ha actualizado exitosamente'})
        
        return response
    else:
        return not_found("No se ha podido actualizar el usuario con el id: " + id)

#Devuelve una lista de usuarios ordenados alfabeticamente, orden ascendente -> python.ASCENDING , orden descendente -> python.DESCENDING
@app.route('/usuario/by_name', methods=['GET'])
def get_usuario_ordered_by_name():
    usuarios = usuario_db.find().sort("nombre_completo", pymongo.ASCENDING)
    response = json_util.dumps(usuarios)
    return Response(response, mimetype='application/json')

#Devuelve un usuario a partir de (parte de) su correo electronico pasado por parametro
@app.route('/usuario/by_email', methods=['POST'])
def get_usuario_by_email():
    email = request.json['correo']
    usuarios = usuario_db.find( { 'correo': { "$regex": email + '.*', "$options" :'i' }} )
    response = json_util.dumps(usuarios)
    if response == '[]':
        return not_found("No se ha encontrado ningún usuario con el email " + email)
    else:     
        return Response(response, mimetype='application/json')


# ---------------------------------------------FIN USUARIO-----------------------------------------------------------

# ---------------------------------------------INICIO TRAYECTO-----------------------------------------------------------

# Obtengo la colección de trayectos
trayecto_db = db['Trayecto']

#Devuelve una lista de trayectos
@app.route('/trayecto', methods=['GET'])
def get_trayectos():
    trayectos = trayecto_db.find()
    response = json_util.dumps(trayectos)
    return Response(response, mimetype='application/json')

#Devuelve un trayecto cuyo id coincide con el que se pasa por parámetro
@app.route('/trayecto/<id>', methods=['GET'])
def get_trayecto(id):
    trayecto = trayecto_db.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(trayecto)
    if response == 'null':
        return not_found("No se han encontrado trayectos con el id: " + id)
    else:     
        return Response(response, mimetype='application/json')

#Crea un nuevo trayecto
@app.route('/trayecto/create', methods=["POST"])
def create_trayecto():
    destino= request.json['destino']
    duracion= int(request.json['duracion'])
    fecha= request.json['fecha']
    hora= request.json['hora']
    origen= request.json['origen']
    periodicidad= request.json['periodicidad']
    precio= float(request.json['precio'])
    fotos_opcionales= request.json['fotos_opcionales']
    plazas_totales= int(request.json['plazas_totales'])
    vehiculo= request.json['vehiculo']
    creador= request.json['creador']

    if creador and destino and fecha and hora and precio and plazas_totales and vehiculo:
        id=trayecto_db.insert_one({
            "creador": creador,
            "destino":destino,
            "duracion":duracion,
            "fecha":fecha,
            "hora":hora,
            "origen":origen,
            "periodicidad":periodicidad,
            "precio":precio,
            "fotos_opcionales":fotos_opcionales,
            "plazas_totales":plazas_totales,
            "vehiculo":vehiculo, 
            "pasajeros": []
        })
        response = {
            "id":str(id),
            "creador":creador,
            "destino":destino,
            "duracion":duracion,
            "fecha":fecha,
            "hora":hora,
            "origen":origen,
            "periodicidad":periodicidad,
            "precio":precio,
            "fotos_opcionales":fotos_opcionales,
            "plazas_totales":plazas_totales,
            "vehiculo":vehiculo, 
            "pasajeros": []
        }
        return response
    else:
        return not_found("No se ha podido crear el trayecto")

#Elimina un trayecto cuyo id coincide con el que se pasa por parametro
@app.route('/trayecto/delete/<id>', methods=['DELETE'])
def delete_trayecto(id):
    trayecto_db.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message': 'El trayecto con id '+id+' se ha eliminado exitosamente'})
    return response

#Actualiza la informacion del trayecto cuyo id coincide con el que se pasa por parametro
@app.route('/trayecto/update/<id>', methods=['PUT'])
def update_trayecto(id):
    destino = request.json['destino']
    duracion= int(request.json['duracion'])
    fecha = request.json['fecha']
    hora = request.json['hora']
    origen = request.json['origen']
    periodicidad = request.json['periodicidad']
    precio= float(request.json['precio'])
    fotos_opcionales = request.json['fotos_opcionales']
    plazas_totales= int(request.json['plazas_totales'])
    vehiculo = request.json['vehiculo']
    pasajeros = request.json['pasajeros']

    if destino and fecha and hora and precio and plazas_totales and vehiculo:
        filter = {"_id": ObjectId(id)}
        new_values = {"$set":{
            "destino": destino,
            "duracion": duracion,
            "fecha": fecha,
            "hora": hora,
            "origen": origen,
            "periodicidad": periodicidad,
            "precio": precio,
            "fotos_opcionales": fotos_opcionales,
            "plazas_totales": plazas_totales,
            "vehiculo": vehiculo, 
            "pasajeros": pasajeros
        }}
        
        trayecto_db.update_one(filter, new_values) 

        response = jsonify({'message': 'El trayecto con id '+id+' se ha actualizado exitosamente'})
        
        return response
    else:
        return not_found("No se ha podido actualizar el trayecto con id: " + id)

#Devuelve los trayectos cuyo destino coincide con el que se pasa por parámetro 
@app.route('/trayecto/by_destino', methods=['POST'])
def get_trayecto_destino():
    
    try : 
        destino = request.json['destino']
    except :
        print("destino no introducido")
    
    trayecto = trayecto_db.find({'destino': destino})
    response = json_util.dumps(trayecto)
    if response == '[]':
        return not_found("No se han encontrado trayectos con destino " + destino)
    else:     
        return Response(response, mimetype='application/json')
    
#Devuelve los trayectos cuyos origenes y destinos coinciden con los pasados por parámetro 
@app.route('/trayecto/by_origen_destino', methods=['POST'])
def get_trayecto_origen_destino():
    try : 
        origen = request.json['origen']
        destino = request.json['destino']
    except :
        print("destino u origen no introducidos")
    
    trayecto = trayecto_db.find({'origen': origen, 'destino': destino})
    response = json_util.dumps(trayecto)
    if response == '[]':
        return not_found("No se han encontrado trayectos con origen " + origen + " y destino " + destino)
    else:     
        return Response(response, mimetype='application/json')

#Devuelve los trayectos cuyo precio es menor que la cantidad indicada por parametro
@app.route('/trayecto/by_precio', methods=['POST'])
def get_trayecto_precio():
    try : 
        precio = request.json['precio']
    except :
        print("precio no introducido")
    
    trayecto = trayecto_db.find({'precio': { "$lt" : precio }})
    response = json_util.dumps(trayecto)
    if response == '[]':
        return not_found("Trayectos con precio menor a " + str(precio) + " no encontrados")
    else:     
        return Response(response, mimetype='application/json')

#Devuelve los usuarios de un trayecto a partir del id del trayecto indicado por parametro
@app.route('/usuario/by_trayecto/<id>', methods=['GET'])
def get_usuario_trayecto(id):
    trayecto = trayecto_db.find_one({'_id': ObjectId(id)})
    pasajeros = trayecto.get("pasajeros")
    response = json_util.dumps(pasajeros)
    if response == '[]':
        return not_found("El trayecto con id: " + id + " no tiene usuarios")
    else:     
        return Response(response, mimetype='application/json')

# ---------------------------------------------FIN TRAYECTO-----------------------------------------------------------

# --------------------------------------------- DATOS ABIERTOS - TRAFICO -----------------------------------------------------------
def get_datos_trafico_actualizados():
    global ultima_actualizacion_trafico, trafico_datos_abiertos #Llamada a la vbles globales para obtener y actualizar su valor
    proxima_actualizacion_trafico = ultima_actualizacion_trafico + timedelta(minutes = 2) #Comprobamos que los datos se actualizan cada 2 min
    if ultima_actualizacion_trafico > proxima_actualizacion_trafico: #Descargar los datos y actualizar en caso de que este desactualizado
        ultima_actualizacion_trafico = proxima_actualizacion_trafico
        trafico_datos_abiertos = datos_abiertos.descargar_datos_trafico()
    return trafico_datos_abiertos

#Devuelve una lista con las incidencias de trafico del conjunto de datos abiertos
@app.route('/trafico', methods=['GET'])
def get_trafico():
    datos_trafico = get_datos_trafico_actualizados()
    response = json_util.dumps(datos_trafico)
    return Response(response, mimetype='application/json')

#Devuelve las incidencias de trafico de una provincia
@app.route('/trafico/by_provincia', methods=['POST'])
def get_incidencias_provincia():
    try : 
        provincia = request.json["provincia"]
    except :
        print("provincia no introducida")
    
    trafico_actualizado = get_datos_trafico_actualizados()
    incidencias_trafico = datos_abiertos.get_incidencias_provincia(provincia, trafico_actualizado)
    response = json_util.dumps(incidencias_trafico)    
    if response == '[]':
        not_found("No hay incidencias en " + provincia) 
    else: 
        Response(response, mimetype='application/json')
        

@app.route('/trafico/rango', methods=['POST'])
def get_trafico_in_rango():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
        rango = float(request.json["rango"])
    except :
        print("Latitud, longitud o rango no introducidos")
    
    
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_rango(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_rango(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias de trafico a " + str(rango) + " kms de la ubicacion actual")
    else:
        return Response(response, mimetype='application/json')

@app.route('/trafico/nieve', methods=['POST'])
def get_trafico_nieve():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
    except :
        print("Latitud y longitud no introducidas")
    
    rango = float(request.json["rango"])
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_nieve(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_nieve(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias de nieve trafico a " + str(rango) + " kms de la ubicacion actual")
    else:
        return Response(response, mimetype='application/json')    

@app.route('/trafico/obras', methods=['POST'])
def get_trafico_obras():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
    except :
        print("Latitud y longitud no introducidas")
    
    rango = float(request.json["rango"])
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_obras(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_obras(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias de obras trafico a " + str(rango) + " kms de la ubicacion actual")
    else:
        return Response(response, mimetype='application/json')  


@app.route('/trafico/cortes', methods=['POST'])
def get_trafico_cortes():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
    except :
        print("Latitud y longitud no introducidas")
    
    rango = float(request.json["rango"])
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_cortes(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_cortes(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias de cortes de trafico a " + str(rango) + " kms de la ubicacion actual")
    else:
        return Response(response, mimetype='application/json')  

@app.route('/trafico/clima', methods=['POST'])
def get_trafico_clima():
    latitude = None
    longitude = None

    try : 
        latitude = float(request.json["latitude"])
        longitude = float(request.json["longitude"])
    except :
        print("Latitud y longitud no introducidas")
    
    rango = float(request.json["rango"])
    lista = None
    trafico_actualizado = get_datos_trafico_actualizados()
    if latitude and longitude:
        lista = datos_abiertos.get_incidencias_clima(latitude, longitude, rango, trafico_actualizado)
    else:
        lista = datos_abiertos.get_incidencias_clima(None, None, rango, trafico_actualizado)
        
    response = json_util.dumps(lista)

    if response == '[]':
        return not_found("No se han encontrado incidencias climatologicas a " + str(rango) + " kms de la ubicacion actual")
    else:
        return Response(response, mimetype='application/json')  

# --------------------------------------------- FIN DATOS ABIERTOS - TRAFICO -------------------------------------------------------

# ---------------------------------------------MANEJO DE ERRORES-----------------------------------------------------------

#Error 400
@app.errorhandler(400)
def not_found(error=None):
    response = jsonify({
        'message': 'Bad request: ' + request.url,
        'status': 400
    })
    response.status_code = 400
    return response

#Error 404
@app.errorhandler(404)
def not_found(error=None):
    if error is None : 
        response = jsonify({
        'message': 'Recurso no encontrado: ' + request.url,
        'status': 404
        })
    else: 
        response = jsonify({
        'message': error,
        'status': 404
        })
    response.status_code = 404
    return response

#Error 500
@app.errorhandler(500)
def server_error(error):
    response = jsonify({
        'message': 'Error del servidor: ' + request.url,
        'status': 500
    })
    response.status_code = 500
    return response

# --------------------------------------------- DATOS ABIERTOS - GASOLINERA -----------------------------------------------------------
def get_datos_gasolineras_actualizadas():
    global ultima_actualizacion_gasolineras, gasolineras_datos_abiertos #Llamada a la vbles globales para obtener y actualizar su valor
    proxima_actualizacion = ultima_actualizacion_gasolineras + timedelta(hours = 1) #Comprobamos que los datos se actualizan cada hora
    if ultima_actualizacion_gasolineras > proxima_actualizacion: #Descargar los datos y actualizar en caso de que este desactualizado
        ultima_actualizacion_gasolineras = proxima_actualizacion
        gasolineras_datos_abiertos = datos_abiertos.descargar_gasolineras()
    return gasolineras_datos_abiertos

#Devuelve una lista con todas las gasolineras del conjunto de datos abiertos
@app.route('/gasolineras', methods=['GET'])
def get_gasolineras():
    datos_actualizados = get_datos_gasolineras_actualizadas()
    response = json_util.dumps(datos_actualizados)    
    return Response(response, mimetype='application/json')

#Devuelve una lista con las gasolineras de una localidad pasada por parametro
#Las gasolineras estan ordenadas segun el precio de la gasolina 95 (de mas barata a mas cara)
@app.route('/gasolineras/gasolina95_low_cost', methods=['POST'])
def get_gasolineras_gasolina95_lowcost():
    try : 
         localidad = request.json["localidad"]
    except :
        print("Latitud y longitud no introducidas")
   
    datos_actualizados = get_datos_gasolineras_actualizadas()
    gasolineras_lowcost = datos_abiertos.get_gasolineras_gasolina95_lowcost_localidad(localidad, datos_actualizados)
    response = json_util.dumps(gasolineras_lowcost) 
    if response == '[]':
        not_found("No se han encontrado gasolineras en " + localidad)
    else:     
        return Response(response, mimetype='application/json')
    

@app.route('/gasolineras/rango', methods=['POST'])
def get_gasolineras_rango(): 
    # Devuelve una lista de gasolineras de un rango X en km de una ubicación pasada por parámetro o la ubicación real
    #PRUEBA
    '''
    {
        "latitude": 36.73428,
        "longitude": -4.56591,
        "rango": 5
    }
    '''
    latitude = None
    longitude = None

    try : 
        latitude = request.json["latitude"]
        longitude = request.json["longitude"]
    except :
        print("Latitud y longitud no introducidas")

    rango_km = float(request.json["rango"])
    consulta = None

    rango = rango_km / 111.12  # Paso de km a grados

    gasolineras_actualizadas = get_datos_gasolineras_actualizadas()
    # Si no le pasa ubicacion por parametro se pasa None en los campos para que calcule la ubicacion actual
    if latitude and longitude:
        consulta = datos_abiertos.get_gasolineras_ubicacion(gasolineras_actualizadas, latitude, longitude, rango)
    else:
        consulta = datos_abiertos.get_gasolineras_ubicacion(gasolineras_actualizadas, None, None, rango)
    
    response = json_util.dumps(consulta)

    # Controla los errores
    if response == '[]':
        not_found("No hay gasolineras en el rango de " + str(rango_km) +" a partir de la ubicación actual")
    else:
        return Response(response, mimetype='application/json')
    

@app.route('/gasolineras/provincia_24_horas', methods=['POST'])
def get_gasolineras_provincia_24horas():
    # Devuelve las gasolineras abiertas 24 horas de una provincia pasada por parametro
    # PRUEBA
    '''
    {
        "Provincia" : "Málaga"
    }
    '''
    try : 
         provincia = request.json["Provincia"]
    except :
        print("Latitud y longitud no introducidas")
   
    gasolineras_actualizadas = get_datos_gasolineras_actualizadas()
    consulta = datos_abiertos.get_gasolineras_24horas(gasolineras_actualizadas, provincia)
    response = json_util.dumps(consulta)
    
    if response == '[]':
        not_found("No se han encontrado gasolineras abiertas 24 horas en " + provincia)
    else:
        return Response(response, mimetype='application/json')    
    
# ---------------------------------------------FIN DATOS ABIERTOS-----------------------------------------------------------

app.run()

client.close()
