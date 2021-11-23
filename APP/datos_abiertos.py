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
def get_datos_abiertos():
        # Esto devuelve todos los datos de esta/nuestra patria
    link = 'https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/'
    f = request.urlopen(link)
    myfile = f.read()
    y=json.loads(myfile)
    for g in y["ListaEESSPrecio"]:
        print(g["Localidad"])

    return y

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

def calculaLatMaxyMinActual(rango):

    # ------VÁLIDO PARA UBICACIÓN ACTUAL-----
    Nomi_locator = Nominatim(user_agent="My App")

    my_location= geocoder.ip('me')

    #my latitude and longitude coordinates
    latitude= my_location.geojson['features'][0]['properties']['lat']
    longitude = my_location.geojson['features'][0]['properties']['lng']
    #------- FIN DE UBICACIÓN ACTUAL

    #   get the location
    location = Nomi_locator.reverse(f"{latitude}, {longitude}")
    
    '''
    print("Mi latitud es",latitude)
    print("Mi longitud es",longitude)
    print("Mi rango de latitud es",latitude+float(rango))
    print("Mi rango de longitud es",longitude+float(rango))
    print("Your Current IP location is", location)
    
    '''
    
    dict = {"Longitud_max":longitude+float(rango),"Longitud_min":longitude-float(rango),"Latitud_max":latitude+float(rango),"Latitud_min":latitude-float(rango)}
    print(dict)
    return dict


#def calculaLatMaxyMin(longitude,latitude,rango): 
def calculaLatMaxyMin(latitude,longitude,rango):
    
    dict = {"Longitud_max":longitude+float(rango),"Longitud_min":longitude-float(rango),"Latitud_max":latitude+float(rango),"Latitud_min":latitude-float(rango)}
    print(dict)
    return dict