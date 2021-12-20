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
    
    if not latitud or not longitud:
        latitud, longitud = calcula_ubicacion()
    else:
        latitud = float(latitud)
        longitud = float(longitud)

    rangoGrados = float(rango)/111.12
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

#FUNCIONA
def get_incidencias_causa(latitud, longitud, rango, causa_solicitada):
    # trafico_actualizado = descargar_datos_trafico()
    trafico_actualizado = get_incidencias_rango(latitud, longitud, rango)
    print(type(trafico_actualizado))
    print(trafico_actualizado)
    '''
    if not latitud and not longitud:
        latitud, longitud = calcula_ubicacion()

    rangoGrados = rango/111.12
    latitud_min = latitud - rangoGrados
    latitud_max = latitud + rangoGrados
    longitud_min = longitud - rangoGrados
    longitud_max = longitud + rangoGrados
    '''
    lista_incidencias = []
    #Ponemos la causa en UPPER para que haga la comprobacion correcta
    causa_solicitada_upper = causa_solicitada.upper()
    for incidencia in trafico_actualizado:
        causa = incidencia["properties"]["tipo"]
            
        #cords = incidencia["geometry"]["coordinates"]
        #lon = float(cords[0])
        #lat = float(cords[1])
            
        # if (latitud_min < lat < latitud_max) and (longitud_min < lon < longitud_max) and causa == causa_solicitada:
        if causa == causa_solicitada_upper:
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
        if gasolinera["Localidad"].upper() == localidad.upper():
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
    else: 
        latitud = float(latitud)
        longitud = float(longitud)
    
    #Refactor de los cerebro grande
    rangoGrados = float(rango)/111.12
    latitud_min = latitud - rangoGrados
    latitud_max = latitud + rangoGrados
    longitud_min = longitud - rangoGrados
    longitud_max = longitud + rangoGrados

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


municipios = ["Madrid","Barcelona","Valencia","Sevilla","Zaragoza","Málaga","Murcia","Palma","Las Palmas de Gran Canaria",
"Bilbao","Alicante","Córdoba","Valladolid","Vigo","Gijón","Hospitalet de Llobregat","Vitoria","La Coruña","Granada","Elche",
"Oviedo","Badalona","Tarrasa","Cartagena","Jerez de la Frontera","Sabadell","Móstoles","Santa Cruz de Tenerife","Alcalá de Henares"
,"Pamplona","Almería","Fuenlabrada","Leganés","San Sebastián","Getafe","Burgos","Santander","Albacete","Castellón de la Plana",
"Alcorcón","San Cristóbal de la Laguna","Logroño","Badajoz","Huelva","Salamanca","Marbella","Lérida","Dos Hermanas","Tarragona",
"Torrejón de Ardoz","León","Mataró","Parla","Algeciras","Cádiz","Santa Coloma de Gramanet","Jaén","Alcobendas","Orense","Reus",
"Telde","Baracaldo","Lugo","Gerona","San Fernando","Cáceres","Santiago de Compostela","Las Rozas de Madrid","Lorca",
"Roquetas de Mar","Torrevieja","Coslada","El Puerto de Santa María","San Cugat del Vallés","Talavera de la Reina",
"Cornellá de Llobregat","Ceuta","Melilla","Pozuelo de Alarcón","El Ejido","Guadalajara","Orihuela","Toledo",
"San Sebastián de los Reyes","San Baudilio de Llobregat","Pontevedra","Chiclana de la Frontera","Avilés","Torrente",
"Rivas-Vaciamadrid","Palencia","Arona","Guecho","Vélez-Málaga","Fuengirola","Mijas","Gandía","Manresa","Ciudad Real",
"Alcalá de Guadaíra","Rubí","Valdemoro","Ferrol","Majadahonda","Benidorm","Molina de Segura","Santa Lucía de Tirajana",
"Torremolinos","Sanlúcar de Barrameda","Ponferrada","Paterna","Estepona","Benalmádena","Villanueva y Geltrú","Viladecans",
"Sagunto","Zamora","Casteldefels","La Línea de la Concepción","El Prat de Llobregat","Collado Villalba","Irún","Motril","Linares",
"Granollers","Alcoy","Mérida","Ávila","Aranjuez","Sardañola del Vallés","Arrecife","San Vicente del Raspeig","Cuenca",
"Arganda del Rey","S. Bartolomé de Tirajana","Torrelavega","Elda","Segovia","Huesca","Utrera","Siero","Mollet del Vallés",
"Villarreal","Puertollano","Calviá","Ibiza","Boadilla del Monte","Pinto","Colmenar Viejo","Portugalete","Adeje","Santurce",
"Gavá","Esplugas de Llobregat","Figueras","Alcira","Denia","Mislata","San Feliú de Llobregat","Langreo","Rincón de la Victoria"
,"Mairena del Aljarafe","Lucena","Granadilla de Abona","Mieres","Basauri","Antequera","La Orotava","Alcantarilla",
"San Fernando de Henares","Puerto Real","Tres Cantos","Vich","Plasencia","Lloret de Mar","Manacor","Écija","Soria","Blanes",
"Rentería","Narón","Igualada","Tomelloso","Villafranca del Panadés","Andújar","Miranda de Ebro","Burjasot","Los Realejos",
"Los Palacios y Villafranca","Villagarcía de Arosa","La Rinconada","Onteniente","Ripollet","Lluchmayor","Arucas","Ronda",
"Alhaurín de la Torre","Don Benito","Vendrell","Úbeda","Puerto del Rosario","Mazarrón","Burriana","Tudela","Cieza","Teruel",
"Águilas","Villena","Yecla","Petrel","Tortosa","Marrachí","Almendralejo","Moncada y Reixach","Azuqueca de Henares",
"San Adrián de Besós","Oleiros","Santa Eulalia del Río","Olot","Santa Pola","Aranda de Duero","Torre Pacheco","Cambrils",
"Vall de Uxó","Puerto de la Cruz","Villajoyosa","Galapagar","Jávea","San Juan Despí","Castro-Urdiales","San Javier",
"Barberá del Vallés","Alcázar de San Juan","San Andrés del Rabanedo","Camargo","Arcos de la Frontera","Carballo","Hellín",
"Valdepeñas","Manises","Aldaya","Arteijo","Lejona","Puente Genil","Chirivella","Salt","Alacuás","Coria del Río","Redondela",
"Inca","San Roque","Totana","Ingenio","Agüimes","Calpe","Játiva","Ciudadela","Níjar","Culleredo","Rota","Galdácano","Sueca",
"Sestao","Mahón","Ames","San Pedro de Ribas","Carmona","Sitges","Vinaroz","Morón de la Frontera","Oliva","Crevillente",
"Premiá de Mar","Algemesí","Durango","San Vicente dels Horts","Almuñécar","Riveira","Martorell","Éibar","Campello","Catarroja",
"Lepe","San Andrés de la Barca","Lebrija","Novelda","Villaviciosa de Odón","Benicarló","Villarrobledo","Caravaca de la Cruz",
"Camas","Salou","Cangas de Morrazo","Villanueva de la Serena","Pineda de Mar","Candelaria","Almazora","Jumilla","Marín","Onda",
"Cuart de Poblet","Almansa","Santa Perpetua de Moguda","Valls","Calafell","Calahorra","Martos","Navalcarnero","Molins de Rey",
"Adra","Paiporta","Gáldar","Erandio","Icod de los Vinos","San Pedro del Pinatar","Altea","Olesa de Montserrat","Montilla",
"Alhaurín el Grande","Tacoronte","San José","Ibi","Piélagos","Tomares","Vícar","Cambre","Illescas","Puenteareas",
"Priego de Córdoba","Muchamiel","Mogán","Liria","Ciempozuelos","Cullera","Castellar del Vallés","Pilar de la Horadada",
"La Oliva","Barbate","Castrillón","Cártama","Los Barrios","Palafrugell","Alcalá la Real","Zarauz","Mejorada del Campo",
"Alboraya","San Juan de Alicante","Almonte","El Masnou","Torrelodones","Laguna de Duero","San Antonio Abad","Nerja","Armilla",
"Coín","Baza","Esparraguera","Mondragón","Isla Cristina","Moncada","Vilaseca","San Felíu de Guixols","La Estrada",
"Paracuellos de Jarama","Puebla de Vallbona","Alfaz del Pi","Conil de la Frontera","Loja","Medina del Campo","Rojales",
"Mairena del Alcor","Barañáin","Palma del Río","Bétera","Amposta","Las Torres de Cotillas","San Juan de Aznalfarache","Requena",
"Maracena","Cabra","Los Llanos de Aridane","Lalín","Ribarroja del Turia","Baena","Calatayud","Teguise","Ayamonte","Alfafar",
"Alhama de Murcia","Algete","Carcagente","Pájara","Manlleu","Moguer","Guía de Isora","Guadix","Aspe","Tías","Picassent"]

provincias=["Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Barcelona", "Burgos", "Cáceres", "Cádiz", 
"Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca", "Gerona", "Granada", "Guadalajara", "Guipúzcoa", "Huelva", "Huesca", 
"Islas Baleares", "Jaén", "La Coruña", "La Rioja", "Las Palmas", "León", "Lérida", "Lugo", "Madrid", "Málaga", "Murcia", "Navarra",
"Orense", "Palencia", "Pontevedra", "Salamanca", "Santa Cruz de Tenerife", "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", 
"Toledo", "Valencia", "Valladolid", "Vizcaya", "Zamora", "Zaragoza"]
