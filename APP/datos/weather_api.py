from urllib import request
import json

API_KEY = '60e0e0d9804a4905b54154321220102'
NUMERO_DE_DIAS = 4 
def get_prediccion_tiempo(latitud, longitud):

    link = 'http://api.weatherapi.com/v1/forecast.json?key=' + API_KEY + '&q=' + latitud + ',' + longitud + '&days=' + str(NUMERO_DE_DIAS) +'&aqi=no&alerts=no'
    file = request.urlopen(link)
    file_leido = file.read()
    prediccion = json.loads(file_leido)
    informacion_destino = {'nombre_destino': prediccion["location"]["name"], 'comunidad_autonoma' : prediccion["location"]["region"], 'pais' : prediccion["location"]["country"]}
    tiempo_actual = {'temperatura_celsius' : prediccion["current"]["temp_c"], 'icono' : prediccion["current"]["condition"]["icon"]} #El icono es para mostrar un sol u otra cosa
    predicciones = []
    for dia in prediccion["forecast"]["forecastday"]:
        diccionario_dia_prediccion = {'fecha':dia["date"], 'temp_max' : dia["day"]["maxtemp_c"], 'temp_min' : dia["day"]["mintemp_c"], 'icono':dia["day"]["condition"]["icon"]}
        predicciones.append(diccionario_dia_prediccion)
    return predicciones, informacion_destino, tiempo_actual