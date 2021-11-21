from urllib import request
import json
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
    print(data)
    data.sort(key=lambda x: x["Precio Gasolina 95 E5"])
    return data

# lines.sort() is more efficient than lines = lines.sorted()
