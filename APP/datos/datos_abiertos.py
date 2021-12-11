from urllib import request
import json

from geopy.geocoders import Nominatim
import geocoder
from datetime import datetime, timedelta
from pprint import pprint


'''
LINKS DE INTERÉS:
    
    Puntos de interés de España: http://datos.santander.es/api/rest/datasets/puntos_interes.json
    Kilometros de carretera en España: https://opendata.arcgis.com/api/v3/datasets/c68d7c5e350c47cb9ad7ac491c327115_2/downloads/data?format=geojson&spatialRefId=4326
    Precio gasolineras España: 'https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/'
    Datos de incidencias de tráfico: 'https://opendata.arcgis.com/datasets/a64659151f0a42c69a38563e9d006c6b_0.geojson'

'''
ultima_actualizacion_gasolineras = datetime.now()
# ultima_actualizacion_trafico = datetime.now()
gasolineras_datos_abiertos = None 
# trafico_datos_abiertos = None 

def get_datos_gasolineras_actualizadas():
    global gasolineras_datos_abiertos, ultima_actualizacion_gasolineras #Llamada a la vbles globales para obtener y actualizar su valor
    proxima_actualizacion = ultima_actualizacion_gasolineras + timedelta(hours = 12) #Comprobamos que los datos se actualizan cada 12 horas
    if gasolineras_datos_abiertos is None:
        gasolineras_datos_abiertos = descargar_gasolineras()
    elif datetime.now() > proxima_actualizacion: #Descargar los datos y actualizar en caso de que este desactualizado
        ultima_actualizacion_gasolineras = proxima_actualizacion
        gasolineras_datos_abiertos = descargar_gasolineras()
    return gasolineras_datos_abiertos

def descargar_datos_trafico():
    link = 'https://opendata.arcgis.com/datasets/a64659151f0a42c69a38563e9d006c6b_0.geojson'
    file = request.urlopen(link)
    datos_trafico = file.read()
    incidencias_trafico = json.loads(datos_trafico)
    return incidencias_trafico

def descargar_gasolineras():
    link = 'https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/'
    file = request.urlopen(link)
    file_leido = file.read()
    gasolineras = json.loads(file_leido)
    return gasolineras

def calcula_ubicacion():

    # ------VÁLIDO PARA UBICACIÓN ACTUAL-----
    Nomi_locator = Nominatim(user_agent="My App")

    my_location= geocoder.ip('me')

    #my latitude and longitude coordinates
    latitude= my_location.geojson['features'][0]['properties']['lat']
    longitude = my_location.geojson['features'][0]['properties']['lng']
    #------- FIN DE UBICACIÓN ACTUAL
   
    return latitude, longitude

# --------------- OPERACIONES TRÁFICO ------------------------#

def get_incidencias_provincia(provincia):
    trafico_actualizado = descargar_datos_trafico()
    lista_incidencias = []
    for incidencia in trafico_actualizado["features"]:
        if incidencia["properties"]["provincia"].upper() == provincia.upper() :
            lista_incidencias.append(incidencia)
    incidencias_json_string = json.dumps(lista_incidencias)
    incidencias_json = json.loads(incidencias_json_string)
    return incidencias_json


def get_incidencias_rango(latitud, longitud, rango):
    trafico_actualizado = descargar_datos_trafico()
    if not latitud and not longitud:
        latitud, longitud = calcula_ubicacion()

    rangoGrados = rango/111.12
    latitud_min = latitud - rangoGrados
    latitud_max = latitud + rangoGrados
    longitud_min = longitud - rangoGrados
    longitud_max = longitud + rangoGrados
    lista_incidencias = []
    for incidencia in trafico_actualizado["features"]:
        if incidencia["geometry"] is not None: 
            cords = incidencia["geometry"]["coordinates"]
            lon = float(cords[0])
            lat = float(cords[1])
            if (latitud_min < lat < latitud_max) and (longitud_min < lon < longitud_max):
                lista_incidencias.append(incidencia)
    incidencias_json_string = json.dumps(lista_incidencias)
    incidencias_json = json.loads(incidencias_json_string)
    return incidencias_json

def get_incidencias_causa(latitud, longitud, rango, causa_solicitada):
    trafico_actualizado = descargar_datos_trafico()
    if not latitud and not longitud:
        latitud, longitud = calcula_ubicacion()

    rangoGrados = rango/111.12
    latitud_min = latitud - rangoGrados
    latitud_max = latitud + rangoGrados
    longitud_min = longitud - rangoGrados
    longitud_max = longitud + rangoGrados
    lista_incidencias = []
    for incidencia in trafico_actualizado["features"]:
        if incidencia["geometry"] is not None: 
            causa = incidencia["properties"]["tipo"]
            cords = incidencia["geometry"]["coordinates"]
            lon = float(cords[0])
            lat = float(cords[1])
            if (latitud_min < lat < latitud_max) and (longitud_min < lon < longitud_max) and causa == causa_solicitada:
                lista_incidencias.append(incidencia)
    incidencias_json_string = json.dumps(lista_incidencias)
    incidencias_json = json.loads(incidencias_json_string)
    return incidencias_json

'''def get_incidencias_nieve(latitud, longitud, rango):
    trafico_actualizado = descargar_datos_trafico()
    if not latitud and not longitud:
        latitud, longitud = calcula_ubicacion()

    rangoGrados = rango/111.12
    latitud_min = latitud - rangoGrados
    latitud_max = latitud + rangoGrados
    longitud_min = longitud - rangoGrados
    longitud_max = longitud + rangoGrados
    lista_incidencias = []
    for incidencia in trafico_actualizado["features"]:
        if incidencia["geometry"] is not None: 
            causa = incidencia["properties"]["tipo"]
            cords = incidencia["geometry"]["coordinates"]
            lon = float(cords[0])
            lat = float(cords[1])
            if (latitud_min < lat < latitud_max) and (longitud_min < lon < longitud_max) and causa == "PUERTOS DE MONTA?A":
                lista_incidencias.append(incidencia)
    incidencias_json_string = json.dumps(lista_incidencias)
    incidencias_json = json.loads(incidencias_json_string)
    return incidencias_json

def get_incidencias_obras(latitud, longitud, rango):
    trafico_actualizado = descargar_datos_trafico()
    if not latitud and not longitud:
        latitud, longitud = calcula_ubicacion()

    rangoGrados = rango/111.12
    latitud_min = latitud - rangoGrados
    latitud_max = latitud + rangoGrados
    longitud_min = longitud - rangoGrados
    longitud_max = longitud + rangoGrados
    lista_incidencias = []
    for incidencia in trafico_actualizado["features"]:
        if incidencia["geometry"] is not None: 
            causa = incidencia["properties"]["tipo"]
            cords = incidencia["geometry"]["coordinates"]
            lon = float(cords[0])
            lat = float(cords[1])
            if (latitud_min < lat < latitud_max) and (longitud_min < lon < longitud_max) and causa == "OBRAS":
                lista_incidencias.append(incidencia)
    incidencias_json_string = json.dumps(lista_incidencias)
    incidencias_json = json.loads(incidencias_json_string)
    return incidencias_json

def get_incidencias_cortes(latitud, longitud, rango):
    trafico_actualizado = descargar_datos_trafico()
    if not latitud and not longitud:
        latitud, longitud = calcula_ubicacion()

    rangoGrados = rango/111.12
    latitud_min = latitud - rangoGrados
    latitud_max = latitud + rangoGrados
    longitud_min = longitud - rangoGrados
    longitud_max = longitud + rangoGrados
    lista_incidencias = []
    for incidencia in trafico_actualizado["features"]:
        if incidencia["geometry"] is not None: 
            causa = incidencia["properties"]["tipo"]
            cords = incidencia["geometry"]["coordinates"]
            lon = float(cords[0])
            lat = float(cords[1])
            if (latitud_min < lat < latitud_max) and (longitud_min < lon < longitud_max) and causa == "CONO":
                lista_incidencias.append(incidencia)
    incidencias_json_string = json.dumps(lista_incidencias)
    incidencias_json = json.loads(incidencias_json_string)
    return incidencias_json

def get_incidencias_clima(latitud, longitud, rango):
    trafico_actualizado = descargar_datos_trafico()
    if not latitud and not longitud:
        latitud, longitud = calcula_ubicacion()

    rangoGrados = rango/111.12
    latitud_min = latitud - rangoGrados
    latitud_max = latitud + rangoGrados
    longitud_min = longitud - rangoGrados
    longitud_max = longitud + rangoGrados
    lista_incidencias = []
    for incidencia in trafico_actualizado["features"]:
        if incidencia["geometry"] is not None: 
            causa = incidencia["properties"]["tipo"]
            cords = incidencia["geometry"]["coordinates"]
            lon = float(cords[0])
            lat = float(cords[1])
            if (latitud_min < lat < latitud_max) and (longitud_min < lon < longitud_max) and causa == "METEOROLOGICA":
                lista_incidencias.append(incidencia)
    incidencias_json_string = json.dumps(lista_incidencias)
    incidencias_json = json.loads(incidencias_json_string)
    return incidencias_json
'''
# --------------- OPERACIONES GASOLINERAS ------------------------#

def get_gasolineras_gasolina95_lowcost_localidad(localidad):
    datos_gasolineras = get_datos_gasolineras_actualizadas()
    lista_gasolineras = []
    for gasolinera in datos_gasolineras["ListaEESSPrecio"]:
        if gasolinera["Localidad"] == localidad:
            lista_gasolineras.append(gasolinera)
    gasolineras_json_string = json.dumps(lista_gasolineras)
    gasolineras_json = json.loads(gasolineras_json_string)
    gasolineras_json_ordenadas = sorted(gasolineras_json, key=lambda k: k['Precio Gasolina 95 E5'], reverse=False)
    return gasolineras_json_ordenadas

def get_gasolineras_ubicacion(latitud, longitud, rango):
    datos_gasolineras = get_datos_gasolineras_actualizadas()
    #Si el parametro recibido es nulo, se actualiza con la ubicación actual
    if not latitud and not longitud:
        latitud, longitud = calcula_ubicacion()     

    latitud_min = latitud - float(rango)
    latitud_max = latitud + float(rango)
    longitud_min = longitud - float(rango)
    longitud_max = longitud + float(rango)
    lista = []
    for g in datos_gasolineras["ListaEESSPrecio"]:
        lat = float(g["Latitud"].replace(",","."))
        lon = float(g["Longitud (WGS84)"].replace(",","."))
        if (latitud_min < lat < latitud_max) and (longitud_min < lon < longitud_max):
            lista.append(g)

    gasolineras_json_string = json.dumps(lista)
    gasolineras_json = json.loads(gasolineras_json_string)

    return gasolineras_json

def get_gasolineras_24horas(provincia):
    datos_gasolineras = get_datos_gasolineras_actualizadas()
    lista = []
    for g in datos_gasolineras["ListaEESSPrecio"]:
        if g["Provincia"].upper() == provincia.upper() and g["Horario"].find("24H") != -1:
            lista.append(g)
    gasolineras_json_string = json.dumps(lista)
    gasolineras_json = json.loads(gasolineras_json_string)

    return gasolineras_json