from urllib import request
import json

from geopy.geocoders import Nominatim
import geocoder

from pprint import pprint


'''
LINKS DE INTERÉS:
    
    Puntos de interés de España: http://datos.santander.es/api/rest/datasets/puntos_interes.json
    Kilometros de carretera en España: https://opendata.arcgis.com/api/v3/datasets/c68d7c5e350c47cb9ad7ac491c327115_2/downloads/data?format=geojson&spatialRefId=4326
    Precio gasolineras España: 'https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/'

'''
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

def get_incidencias_comunidad_autonoma_and_provincia(comunidad_autonoma, provincia, trafico_actualizado):
    lista_incidencias = []
    for incidencia in trafico_actualizado["features"]:
        if incidencia["properties"]["autonomia"] == comunidad_autonoma and incidencia["properties"]["provincia"] == provincia:
            lista_incidencias.append(incidencia)
    incidencias_json_string = json.dumps(lista_incidencias)
    incidencias_json = json.loads(incidencias_json_string)
    return incidencias_json

def get_gasolineras_gasolina95_lowcost_localidad(localidad, datos_gasolineras):
    lista_gasolineras = []
    for gasolinera in datos_gasolineras["ListaEESSPrecio"]:
        if gasolinera["Localidad"] == localidad:
            lista_gasolineras.append(gasolinera)
    gasolineras_json_string = json.dumps(lista_gasolineras)
    gasolineras_json = json.loads(gasolineras_json_string)
    gasolineras_json_ordenadas = sorted(gasolineras_json, key=lambda k: k['Precio Gasolina 95 E5'], reverse=False)
    return gasolineras_json_ordenadas

def get_gasolineras_ubicacion(ubicacion):
        # Esto devuelve todos los datos de esta/nuestra patria
    link = 'https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/'
    f = request.urlopen(link)
    myfile = f.read()
    y=json.loads(myfile)

    lista = []
    for g in y["ListaEESSPrecio"]:
        #print(g)
        if g["Localidad"] == ubicacion:
            lista.append(g)
    cadena = "".join(lista)
    data = json.loads(cadena)
    # print(data)

    # Esto intenta ordena con una función 
   # data.sort(key=lambda x: x["Precio Gasolina 95 E5"])
    return data

# lines.sort() is more efficient than lines = lines.sorted()

# Esta función calcula la latitud y longitud maxima dada un rango y la ubicación actual, lo devuelve en forma de diccionario

def calcula_ubicacion():

    # ------VÁLIDO PARA UBICACIÓN ACTUAL-----
    Nomi_locator = Nominatim(user_agent="My App")

    my_location= geocoder.ip('me')

    #my latitude and longitude coordinates
    latitude= my_location.geojson['features'][0]['properties']['lat']
    longitude = my_location.geojson['features'][0]['properties']['lng']
    #------- FIN DE UBICACIÓN ACTUAL
    '''
    #   get the location
    #location = Nomi_locator.reverse(f"{latitude}, {longitude}")

    print("Mi latitud es",latitude)
    print("Mi longitud es",longitude)
    print("Mi rango de latitud es",latitude+float(rango))
    print("Mi rango de longitud es",longitude+float(rango))
    print("Your Current IP location is", location)
    
    #dict = {"Longitud_max":longitude+float(rango),"Longitud_min":longitude-float(rango),"Latitud_max":latitude+float(rango),"Latitud_min":latitude-float(rango)}
    #print(dict)
    '''
    return latitude, longitude


def get_gasolineras_ubicacion(gasolineras_datos_abiertos, latitud, longitud, rango):
    #Si el parametro recibido es nulo, se actualiza con la ubicación actual
    if not latitud and not longitud:
        latitud, longitud = calcula_ubicacion()     

    latitud_min = latitud - float(rango)
    latitud_max = latitud + float(rango)
    longitud_min = longitud - float(rango)
    longitud_max = longitud + float(rango)
    lista = []
    for g in gasolineras_datos_abiertos["ListaEESSPrecio"]:
        lat = float(g["Latitud"].replace(",","."))
        lon = float(g["Longitud (WGS84)"].replace(",","."))
        if (latitud_min < lat < latitud_max) and (longitud_min < lon < longitud_max):
            lista.append(g)
    return lista

def get_gasolineras_24horas(gasolineras_datos_abiertos, provincia):
    #Si el parametro recibido es nulo, se actualiza con la ubicación actual
    lista = []
    for g in gasolineras_datos_abiertos["ListaEESSPrecio"]:
        if g["Provincia"].upper() == provincia.upper() and g["Horario"].find("24H") != -1:
            lista.append(g)
    return lista