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

def get_gasolineras_gasolina95_lowcost_municipio(municipio):
    datos_gasolineras = get_datos_gasolineras_actualizadas()
    lista_gasolineras = []
    for gasolinera in datos_gasolineras["ListaEESSPrecio"]:
        if gasolinera["Municipio"].upper() == municipio.upper():
            lista_gasolineras.append(gasolinera)
    gasolineras_json_string = json.dumps(lista_gasolineras)
    gasolineras_json = json.loads(gasolineras_json_string)
    gasolineras_json_ordenadas = sorted(gasolineras_json, key=lambda k: k['Precio Gasolina 95 E5'], reverse=False)
    if gasolineras_json:
        latMin, lonMin, latMax, lonMax = calcularTamMapa(gasolineras_json)
        
        baratas = []
        medias = []
        caras = []
    
        for gasolinera in gasolineras_json_ordenadas:
            precio_string = gasolinera["Precio Gasolina 95 E5"]
            if precio_string:
                precio = float(precio_string.replace(",", ".")) 
                if precio < 1.45:    
                    baratas.append(gasolinera)
                elif precio >= 1.45 and precio < 1.50:
                    medias.append(gasolinera)
                else:
                    caras.append(gasolinera)

        return baratas, medias, caras, latMin, lonMin, latMax, lonMax
    else: 
        return "No hay gasolineras"

def get_gasolineras_gasolina95_lowcost_provincia(provincia):
    datos_gasolineras = get_datos_gasolineras_actualizadas()
    lista_gasolineras = []
    for gasolinera in datos_gasolineras["ListaEESSPrecio"]:
        if gasolinera["Provincia"].upper() == provincia.upper():
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
    if gasolineras_json:
        latMin, lonMin, latMax, lonMax = calcularTamMapa(gasolineras_json)
        
        baratas = []
        medias = []
        caras = []
    
        for gasolinera in gasolineras_json:
            precio_string = gasolinera["Precio Gasolina 95 E5"]
            if precio_string:
                precio = float(precio_string.replace(",", ".")) 
                if precio < 1.45:    
                    baratas.append(gasolinera)
                elif precio >= 1.45 and precio < 1.50:
                    medias.append(gasolinera)
                else:
                    caras.append(gasolinera)

        return baratas, medias, caras, latMin, lonMin, latMax, lonMax
    else: 
        return "No hay gasolineras"

def calcularTamMapa(gasolineras):
    gasolineras_latitud = sorted(gasolineras, key=lambda k: k['Latitud'], reverse=False)
    gasolineras_longitud = sorted(gasolineras, key=lambda k: k['Longitud (WGS84)'], reverse=False)
    latMin = gasolineras_latitud[0]["Latitud"]
    lonMin = gasolineras_longitud[0]["Longitud (WGS84)"]
    latMax = gasolineras_latitud[len(gasolineras_latitud) - 1]["Latitud"]
    lonMax = gasolineras_longitud[len(gasolineras_longitud) - 1]["Longitud (WGS84)"]
    return float(latMin.replace(",",".")), float(lonMin.replace(",",".")), float(latMax.replace(",",".")), float(lonMax.replace(",",".")) 

municipios = ["Abengibre","Alatoz","Albacete","Alcadozo","Alcalá del Júcar","Alcaraz","Almansa","Alpera","Barrax","Bonete",
"Bonillo (El)","Casas de Juan Núñez","Casas-Ibáñez","Caudete","Cenizate","Chinchilla de Monte-Aragón","Elche de la Sierra",
"Fuente-Álamo","Fuentealbilla","Gineta (La)","Golosalvo","Hellín","Higueruela","Hoya-Gonzalo","Letur","Lezuza","Madrigueras",
"Mahora","Minaya","Montealegre del Castillo","Motilleja","Munera","Navas de Jorquera","Nerpio","Ontur","Ossa de Montiel",
"Peñas de San Pedro","Pétrola","Pozo Cañada","Pozohondo","Pozo-Lorente","Pozuelo","Riópar","Robledo","Roda (La)","Socovos",
"Tarazona de la Mancha","Tobarra","Valdeganga","Villalgordo del Júcar","Villamalea","Villapalacios","Villarrobledo","Yeste",
"Agost","Albatera","Alcalalí","Alcoy/Alcoi","Alfàs del Pi (l')","Algorfa","Algueña","Alicante/Alacant","Almoradí","Altea",
"Aspe","Banyeres de Mariola","Beneixama","Benejúzar","Benidorm","Benijófar","Benilloba","Benissa",
"Benitachell/Poble Nou de Benitatxell (el)","Biar","Bigastro","Busot","Callosa de Segura","Callosa d'En Sarrià","Calpe/Calp",
"Campello (el)","Cañada","Castalla","Catral","Cocentaina","Cox","Crevillent","Dénia","Dolores","Elche/Elx","Elda","Finestrat",
"Formentera del Segura","Gata de Gorgos","Granja de Rocamora","Guardamar del Segura","Hondón de las Nieves",
"Hondón de los Frailes","Ibi","Jacarilla","Jalón/Xaló","Jávea/Xàbia","Monforte del Cid","Monóvar/Monòver","Montesinos (Los)",
"Muro de Alcoy","Mutxamel","Novelda","Nucia (la)","Ondara","Onil","Orba","Orihuela","Pedreguer","Pego","Petrer",
"Pilar de la Horadada","Pinoso","Redován","Rojales","Romana (la)","Salinas","San Fulgencio","San Isidro","San Miguel de Salinas",
"San Vicente del Raspeig/Sant Vicent del Raspeig","Sant Joan d'Alacant","Santa Pola","Sax","Teulada","Tibi","Torrevieja",
"Verger (el)","Villajoyosa/Vila Joiosa (la)","Villena","Abla","Adra","Albox","Alhama de Almería","Almería","Antas","Arboleas",
"Benahadux","Berja","Cantoria","Carboneras","Cuevas del Almanzora","Dalías","Ejido (El)","Fiñana","Fines","Gallardos (Los)",
"Gérgal","Huércal de Almería","Huércal-Overa","Láujar de Andarax","Lubrín","Macael","María","Mojácar","Mojonera (La)",
"Nacimiento","Níjar","Olula del Río","Pulpí","Purchena","Rioja","Roquetas de Mar","Sorbas","Tabernas","Taberno","Tahal","Tíjola",
"Vélez-Blanco","Vélez-Rubio","Vera","Viator","Vícar","Zurgena","Alegría-Dulantzi","Amurrio","Arraia-Maeztu","Arrazua-Ubarrundia",
"Artziniega","Asparrena","Campezo/Kanpezu","Elburgo/Burgelu","Iruña Oka/Iruña de Oca","Labastida","Laguardia","Lantarón","Llodio",
"Oyón/Oion","Ribera Alta","Ribera Baja/Erribera Beitia","Salvatierra/Agurain","San Millán/Donemiliaga","Vitoria-Gasteiz","Zuia",
"Allande","Aller","Avilés","Bimenes","Boal","Cabrales","Cangas de Onís","Cangas del Narcea","Carreño","Castrillón","Castropol",
"Coaña","Colunga","Corvera de Asturias","Cudillero","Franco (El)","Gijón","Gozón","Grado","Grandas de Salime","Ibias","Langreo",
"Laviana","Lena","Llanera","Llanes","Mieres","Morcín","Muros de Nalón","Nava","Navia","Noreña","Oviedo","Peñamellera Baja",
"Piloña","Pravia","Proaza","Ribadedeva","Ribadesella","Salas","San Martín del Rey Aurelio","San Tirso de Abres","Siero","Somiedo",
"Soto del Barco","Tapia de Casariego","Teverga","Tineo","Valdés","Vegadeo","Villanueva de Oscos","Villaviciosa","Adanero",
"Adrada (La)","Aldeaseca","Arenas de San Pedro","Arévalo","Ávila","Barco de Ávila (El)","Barraco (El)","Blascosancho","Burgohondo",
"Candeleda","Cebreros","Colilla (La)","Crespos","Espinosa de los Caballeros","Fontiveros","Hernansancho",
"Madrigal de las Altas Torres","Mingorría","Mombeltrán","Muñana","Muñico","Muñogrande","Navalperal de Pinares","Navaluenga",
"Navarredonda de Gredos","Navarredondilla","Navas del Marqués (Las)","Orbita","Palacios de Goda","Pedro Bernardo","Piedrahíta",
"San Esteban del Valle","San Pedro del Arroyo","Sanchidrián","Solosancho","Sotillo de la Adrada","Tiemblo (El)","Torre (La)",
"Velayos","Villanueva del Aceral","Acedera","Aceuchal","Alange","Albuera (La)","Alburquerque","Alconchel","Almendral",
"Almendralejo","Arroyo de San Serván","Azuaga","Badajoz","Barcarrota","Berlanga","Bienvenida","Burguillos del Cerro",
"Cabeza del Buey","Cabeza la Vaca","Calamonte","Calera de León","Calzadilla de los Barros","Campanario","Campillo de Llerena",
"Casas de Don Pedro","Castilblanco","Castuera","Codosera (La)","Cordobilla de Lácara","Coronada (La)","Corte de Peleas",
"Don Benito","Entrín Bajo","Esparragalejo","Fregenal de la Sierra","Fuenlabrada de los Montes","Fuente de Cantos",
"Fuente del Arco","Fuente del Maestre","Fuentes de León","Granja de Torrehermosa","Guareña","Haba (La)","Herrera del Duque",
"Higuera de la Serena","Higuera de Vargas","Higuera la Real","Hornachos","Jerez de los Caballeros","Llerena","Lobón","Maguilla",
"Medellín","Medina de las Torres","Mérida","Monesterio","Montemolín","Monterrubio de la Serena","Montijo","Nava de Santiago (La)",
"Navalvillar de Pela","Oliva de la Frontera","Oliva de Mérida","Olivenza","Orellana la Vieja","Peñalsordo","Puebla de Alcocer",
"Puebla de la Calzada","Puebla de Obando","Puebla de Sancho Pérez","Pueblonuevo del Guadiana","Quintana de la Serena",
"Ribera del Fresno","Roca de la Sierra (La)","Salvaleón","San Pedro de Mérida","San Vicente de Alcántara","Santa Amalia",
"Santa Marta","Santos de Maimona (Los)","Segura de León","Siruela","Solana de los Barros","Talarrubias","Talavera la Real",
"Torre de Miguel Sesmero","Torremejía","Usagre","Valdecaballeros","Valdelacalzada","Valencia de las Torres","Valencia del Mombuey",
"Valencia del Ventoso","Valle de la Serena","Valverde de Mérida","Villafranca de los Barros","Villagonzalo",
"Villalba de los Barros","Villanueva de la Serena","Villanueva del Fresno","Villar de Rena","Zafra","Zahínos",
"Zalamea de la Serena","Zarza (La)","Alaior","Alaró","Alcúdia","Algaida","Andratx","Artà","Binissalem","Bunyola","Calvià",
"Campanet","Campos","Capdepera","Castell (Es)","Ciutadella de Menorca","Eivissa","Escorca","Esporles","Felanitx","Ferreries",
"Formentera","Inca","Lloseta","Llubí","Llucmajor","Mahón","Manacor","Marratxí","Mercadal (Es)","Montuïri","Muro",
"Palma de Mallorca","Petra","Pobla (Sa)","Pollença","Porreres","Salines (Ses)","Sant Antoni de Portmany","Sant Joan",
"Sant Joan de Labritja","Sant Josep de sa Talaia","Sant Llorenç des Cardassar","Sant Lluís","Santa Eugènia",
"Santa Eulalia del Río","Santa Margalida","Santa María del Camí","Santanyí","Sencelles","Sineu","Sóller","Son Servera",
"Valldemossa","Vilafranca de Bonany","Abrera","Alella","Ametlla del Vallès (L')","Arenys de Mar","Arenys de Munt","Argentona",
"Artés","Avinyó","Badalona","Badia del Vallès","Balsareny","Barberà del Vallès","Barcelona","Begues","Berga","Bigues i Riells",
"Bruc (El)","Cabrera de Mar","Cabrils","Calaf","Calders","Caldes de Montbui","Calella","Calldetenes","Canet de Mar","Canovelles",
"Canyelles","Cardedeu","Cardona","Castellar del Vallès","Castellbell i el Vilar","Castellbisbal","Castelldefels",
"Castellet i la Gornal","Castellterçol","Centelles","Cercs","Cerdanyola del Vallès","Cervelló","Collbató","Cornellà de Llobregat",
"Cubelles","Dosrius","Esparreguera","Esplugues de Llobregat","Fogars de la Selva","Franqueses del Vallès (Les)","Garriga (La)",
"Gavà","Gelida","Gironella","Granada (La)","Granollers","Gualba","Guardiola de Berguedà","Gurb","Hospitalet de Llobregat (L')",
"Igualada","Jorba","Lliçà d'Amunt","Lliçà de Vall","Llinars del Vallès","Malgrat de Mar","Malla","Manlleu","Manresa","Martorell",
"Masies de Voltregà (Les)","Masnou (El)","Masquefa","Mataró","Moià","Molins de Rei","Mollet del Vallès","Monistrol de Montserrat"
,"Montcada i Reixac","Montgat","Montmaneu","Montmeló","Montornès del Vallès","Montseny","Navàs","Òdena","Olèrdola",
"Olesa de Montserrat","Olost","Pacs del Penedès","Palafolls","Palau-solità i Plegamans","Pallejà","Palma de Cervelló (La)",
"Papiol (El)","Parets del Vallès","Piera","Pineda de Mar","Pobla de Claramunt (La)","Pobla de Lillet (La)","Polinyà",
"Pont de Vilomara i Rocafort (El)","Prat de Llobregat (El)","Prats de Lluçanès","Premià de Mar","Puig-reig","Ripollet",
"Roca del Vallès (La)","Roda de Ter","Rubí","Sabadell","Saldes","Sallent","Sant Adrià de Besòs","Sant Andreu de la Barca",
"Sant Andreu de Llavaneres","Sant Antoni de Vilamajor","Sant Boi de Llobregat","Sant Celoni","Sant Cugat del Vallès",
"Sant Cugat Sesgarrigues","Sant Esteve Sesrovires","Sant Feliu de Llobregat","Sant Fruitós de Bages","Sant Iscle de Vallalta",
"Sant Joan de Vilatorrada","Sant Joan Despí","Sant Just Desvern","Sant Llorenç d'Hortons","Sant Martí Sarroca",
"Sant Pere de Ribes","Sant Pere de Riudebitlles","Sant Pere de Torelló","Sant Pere Sallavinera","Sant Pol de Mar",
"Sant Quirze de Besora","Sant Quirze del Vallès","Sant Sadurní d'Anoia","Sant Salvador de Guardiola","Sant Vicenç de Castellet",
"Sant Vicenç de Montalt","Sant Vicenç de Torelló","Sant Vicenç dels Horts","Santa Coloma de Gramenet","Santa Eulàlia de Ronçana",
"Santa Margarida i els Monjos","Santa Maria de Miralles","Santa Maria de Palautordera","Santa Perpètua de Mogoda","Santa Susanna",
"Santpedor","Sentmenat","Seva","Sitges","Subirats","Súria","Tagamanent","Taradell","Teià","Terrassa","Tona","Tordera","Torelló",
"Torre de Claramunt (La)","Torrelles de Llobregat","Vacarisses","Vallgorguina","Vallirana","Vallromanes","Vic","Viladecans",
"Viladecavalls","Vilafranca del Penedès","Vilanova del Vallès","Vilanova i la Geltrú","Vilassar de Dalt","Vilassar de Mar",
"Abadiño","Abanto y Ciérvana-Abanto Zierbena","Alonsotegi","Amorebieta-Etxano","Arrigorriaga","Bakio","Balmaseda","Barakaldo",
"Basauri","Berango","Bermeo","Berriz","Bilbao","Derio","Durango","Elorrio","Erandio","Etxebarri",
" Anteiglesia de San Esteban-Etxebarri Doneztebeko","Galdakao","Gernika-Lumo","Getxo","Gordexola","Gorliz","Güeñes","Iurreta",
"Izurtza","Larrabetzu","Leioa","Lekeitio","Lemoa","Loiu","Mallabia","Markina-Xemein","Mundaka","Mungia","Muxika","Orozko",
"Ortuella","Otxandio","Plentzia","Portugalete","Santurtzi","Sestao","Sopelana","Sopuerta","Ugao-Miraballes","Urduliz",
"Urduña-Orduña","Valle de Trápaga-Trapagaran","Zalla","Zamudio","Ameyugo","Aranda de Duero","Arcos","Balbases (Los)",
"Basconcillos del Tozo","Belorado","Berberana","Briviesca","Buniel","Burgos","Caleruega","Carcedo de Burgos","Cardeñajimeno",
"Castrillo de la Vega","Castrojeriz","Cilleruelo de Abajo","Condado de Treviño","Espinosa de los Monteros","Estépar","Fontioso",
"Frandovínez","Fuentecén","Fuentespina","Gumiel de Izán","Huerta de Rey","Lerma","Madrigalejo del Monte","Medina de Pomar",
"Melgar de Fernamental","Merindad de Montija","Merindad de Río Ubierna","Merindad de Sotoscueva","Milagros","Miranda de Ebro",
"Monasterio de Rodilla","Olmedillo de Roa","Oña","Oquillas","Palacios de la Sierra","Pardilla","Puebla de Arganzón (La)",
"Quintanapalla","Quintanar de la Sierra","Quintanilla Vivar","Revilla y Ahedo (La)","Roa","Rubena","Salas de los Infantes",
"Santa María del Campo","Santa María Rivarredonda","Sarracín","Sasamón","Sotresgudo","Trespaderne","Vadocondes","Valle de Losa",
"Valle de Mena","Valle de Sedano","Valle de Tobalina","Valle de Valdebezana","Valle de Valdelucio","Villadiego",
"Villagonzalo Pedernales","Villalbilla de Burgos","Villalmanzo","Villanueva de Argaño","Villaquirán de los Infantes",
"Villarcayo de Merindad de Castilla la Vieja","Villazopeque","Ahigal","Alcuéscar","Aldea del Cano","Aldeanueva del Camino",
"Aliseda","Almaraz","Almoharín","Arroyo de la Luz","Arroyomolinos","Baños de Montemayor","Barrado","Belvís de Monroy",
"Bohonal de Ibor","Brozas","Cabezuela del Valle","Cabrero","Cáceres","Caminomorisco","Campo Lugar","Cañaveral","Casar de Cáceres",
"Casas de Don Gómez","Casas del Castañar","Castañar de Ibor","Ceclavín","Cilleros","Collado","Coria","Cuacos de Yuste","Deleitosa",
"Escurial","Galisteo","Garrovillas de Alconétar","Guadalupe","Guijo de Galisteo","Guijo de Granadilla","Jaraíz de la Vera",
"Jarandilla de la Vera","Logrosán","Losar de la Vera","Madrigalejo","Madroñera","Majadas","Malpartida de Cáceres",
"Malpartida de Plasencia","Miajadas","Montánchez","Montehermoso","Moraleja","Navalmoral de la Mata","Nuñomoral","Palomero",
"Pasarón de la Vera","Peraleda de la Mata","Perales del Puerto","Pinofranqueado","Piornal","Plasencia","Pozuelo de Zarzón",
"Riolobos","Santa Cruz de la Sierra","Santiago del Campo","Talayuela","Tejeda de Tiétar","Torno (El)","Torre de Santa María",
"Torrecillas de la Tiesa","Torreorgaz","Trujillo","Valdastillas","Valdeobispo","Valencia de Alcántara","Valverde del Fresno",
"Villanueva de la Vera","Villar de Plasencia","Villar del Pedroso","Zarza de Granadilla","Zarza la Mayor","Zorita",
"Alcalá de los Gazules","Alcalá del Valle","Algar","Algeciras","Algodonales","Arcos de la Frontera","Barbate","Barrios (Los)",
"Benalup-Casas Viejas","Bornos","Bosque (El)","Cádiz","Castellar de la Frontera","Chiclana de la Frontera","Chipiona",
"Conil de la Frontera","Espera","Gastor (El)","Grazalema","Jerez de la Frontera","Jimena de la Frontera",
"Línea de la Concepción (La)","Medina-Sidonia","Olvera","Paterna de Rivera","Prado del Rey","Puerto de Santa María (El)",
"Puerto Real","Rota","San Fernando","San José del Valle","San Roque","Sanlúcar de Barrameda","Setenil de las Bodegas","Tarifa",
"Trebujena","Ubrique","Vejer de la Frontera","Villamartín","Alfoz de Lloredo","Ampuero","Arenas de Iguña","Arnuero",
"Astillero (El)","Bárcena de Cicero","Cabezón de la Sal","Camargo","Campoo de Enmedio","Cartes","Castro-Urdiales",
"Cillorigo de Liébana","Colindres","Comillas","Corrales de Buelna (Los)","Corvera de Toranzo","Entrambasaguas","Escalante",
"Hazas de Cesto","Laredo","Liendo","Marina de Cudeyo","Medio Cudeyo","Meruelo","Miengo","Molledo","Penagos","Piélagos","Polanco",
"Puente Viesgo","Ramales de la Victoria","Reinosa","Reocín","Ribamontán al Mar","Ribamontán al Monte","Rionansa","Ruente"
,"Ruiloba","San Felices de Buelna","San Vicente de la Barquera","Santa Cruz de Bezana","Santa María de Cayón","Santander",
"Santillana del Mar","Santiurde de Toranzo","Santoña","Soba","Solórzano","Suances","Torrelavega","Val de San Vicente","Valdáliga"
,"Valderredible","Vega de Pas","Villacarriedo","Villaescusa","Villafufre","Voto","Albocàsser","Alcalà de Xivert","Alcora (l')",
"Almazora/Almassora","Almenara","Alquerías del Niño Perdido","Altura","Artana","Atzeneta del Maestrat","Barracas","Benasal",
"Benicarló","Benicasim/Benicàssim","Benlloch","Betxí","Borriol","Burriana","Cabanes","Canet lo Roig",
"Castellón de la Plana/Castelló de la Plana","Chilches/Xilxes","Coves de Vinromà (les)","Forcall","Jana (la)","Jérica",
"Llosa (la)","Lucena del Cid","Moncofa","Montanejos","Morella","Nules","Onda","Oropesa del Mar/Orpesa","Peñíscola",
"Pobla Tornesa (la)","Ribesalbes","San Rafael del Río","Sant Joan de Moró","Sant Mateu","Santa Magdalena de Pulpis","Segorbe",
"Sierra Engarcerán","Soneja","Sot de Ferrer","Torreblanca","Traiguera","Vall d'Alba","Vall d'Uixó (la)","Vilafamés",
"Vilanova d'Alcolea","Villafranca del Cid","Villarreal/Vila-real","Villavieja","Vinaròs","Vistabella del Maestrazgo","Viver",
"Ceuta","Abenójar","Agudo","Alamillo","Albaladejo","Alcázar de San Juan","Alcolea de Calatrava","Alcubillas","Aldea del Rey",
"Almadén","Almagro","Almedina","Almodóvar del Campo","Almuradiel","Arenales de San Gregorio","Arenas de San Juan",
"Argamasilla de Alba","Argamasilla de Calatrava","Bolaños de Calatrava","Brazatortas","Calzada de Calatrava","Campo de Criptana",
"Carrión de Calatrava","Carrizosa","Castellar de Santiago","Chillón","Ciudad Real","Corral de Calatrava","Cortijos (Los)","Cózar",
"Daimiel","Fuencaliente","Fuente el Fresno","Granátula de Calatrava","Herencia","Horcajo de los Montes","Labores (Las)",
"Llanos del Caudillo","Malagón","Manzanares","Membrilla","Miguelturra","Montiel","Moral de Calatrava","Pedro Muñoz","Piedrabuena",
"Porzuna","Puebla de Don Rodrigo","Puerto Lápice","Puertollano","Robledo (El)","Ruidera","Saceruela","Santa Cruz de Mudela",
"Socuéllamos","Solana (La)","Terrinches","Tomelloso","Torralba de Calatrava","Torre de Juan Abad","Torrenueva","Valdepeñas",
"Villahermosa","Villamanrique","Villamayor de Calatrava","Villanueva de la Fuente","Villanueva de los Infantes",
"Villanueva de San Carlos","Villarrubia de los Ojos","Villarta de San Juan","Viso del Marqués","Adamuz","Aguilar de la Frontera",
"Alcaracejos","Almedinilla","Almodóvar del Río","Añora","Baena","Belalcázar","Belmez","Benamejí","Blázquez (Los)","Bujalance",
"Cabra","Cañete de las Torres","Carcabuey","Cardeña","Carlota (La)","Carpio (El)","Castro del Río","Córdoba","Doña Mencía",
"Encinas Reales","Espejo","Espiel","Fernán-Núñez","Fuente Obejuna","Fuente Palmera","Fuente-Tójar","Hinojosa del Duque",
"Hornachuelos","Iznájar","Lucena","Luque","Montalbán de Córdoba","Montemayor","Montilla","Montoro","Monturque","Moriles",
"Nueva Carteya","Obejo","Palenciana","Palma del Río","Pedro Abad","Pedroche","Peñarroya-Pueblonuevo","Posadas","Pozoblanco"
,"Priego de Córdoba","Puente Genil","Rambla (La)","Rute","San Sebastián de los Ballesteros","Santaella","Torrecampo",
"Victoria (La)","Villa del Río","Villafranca de Córdoba","Villaharta","Villanueva de Córdoba","Villanueva del Duque",
"Villanueva del Rey","Villaviciosa de Córdoba","Viso (El)","Abegondo","Ames","Arteixo","Arzúa","Baña (A)","Bergondo","Betanzos",
"Boimorto","Boiro","Boqueixón","Brión","Cabana de Bergantiños","Cabanas","Camariñas","Cambre","Capela (A)","Carballo","Carnota",
"Carral","Cedeira","Cee","Cerceda","Coirós","Coristanco","Coruña (A)","Culleredo","Curtis","Dodro","Dumbría","Fene","Ferrol",
"Fisterra","Frades","Irixoa","Laracha (A)","Laxe","Malpica de Bergantiños","Mazaricos","Melide","Miño","Mugardos","Muros","Muxía",
"Narón","Neda","Negreira","Noia","Oleiros","Ordes","Oroso","Outes","Oza dos Ríos","Paderne","Padrón","Pino (O)",
"Pobra do Caramiñal (A)","Ponteceso","Pontedeume","Pontes de García Rodríguez (As)","Porto do Son","Rianxo","Ribeira","Rois",
"Sada","Santa Comba","Santiago de Compostela","Sobrado","Teo","Trazo","Val do Dubra","Valdoviño","Vilasantar","Vimianzo","Zas",
"Alberca de Záncara (La)","Aliaguilla","Almarcha (La)","Almodóvar del Pinar","Almonacid del Marquesado","Atalaya del Cañavate",
"Barajas de Melo","Belinchón","Belmonte","Beteta","Buenache de Alarcón","Campillo de Altobuey","Campos del Paraíso","Cañaveras",
"Cañaveruelas","Cañete","Carboneras de Guadazaón","Casas de Benítez","Casas de Fernando Alonso","Casas de Haro",
"Casas de los Pinos","Casasimarro","Castillejo de Iniesta","Castillo de Garcimuñoz","Cervera del Llano","Chillarón de Cuenca",
"Cuenca","Fuente de Pedro Naharro","Graja de Iniesta","Herrumblar (El)","Hinojosa (La)","Hinojosos (Los)","Hito (El)","Honrubia",
"Horcajo de Santiago","Huete","Iniesta","Landete","Ledaña","Mariana","Mesas (Las)","Minglanilla","Mira","Montalbanejo","Montalbo",
"Mota del Cuervo","Motilla del Palancar","Palomares del Campo","Pedernoso (El)","Pedroñeras (Las)","Peral (El)","Pozoamargo",
"Pozorrubielos de la Mancha","Provencio (El)","Puebla de Almenara","Quintanar del Rey","Saelices","Salvacañete","San Clemente",
"San Lorenzo de la Parrilla","Santa Cruz de Moya","Santa María de los Llanos","Santa María del Campo Rus","Sisante","Talayuelas",
"Tarancón","Tébar","Torrejoncillo del Rey","Torrubia del Campo","Tragacete","Tresjuncos","Valdeolivas","Valeras (Las)",
"Valverde de Júcar","Villaconejos de Trabaque","Villaescusa de Haro","Villagarcía del Llano","Villalba del Rey","Villalpardo",
"Villamayor de Santiago","Villanueva de la Jara","Villar de Cañas","Villarejo de Fuentes","Villarejo-Periesteban",
"Villares del Saz","Villarrubio","Villarta","Villaverde y Pasaconsol","Zafra de Záncara","Aia","Andoain","Arrasate/Mondragón",
"Astigarraga","Ataun","Azkoitia","Azpeitia","Beasain","Bergara","Deba","Donostia-San Sebastián","Eibar","Elgoibar","Errenteria",
"Eskoriatza","Hernani","Hondarribia","Idiazabal","Irun","Itsasondo","Lasarte-Oria","Lazkao","Legorreta","Lezo","Mutriku",
"Oiartzun","Olaberria","Oñati","Ordizia","Tolosa","Urnieta","Usurbil","Villabona","Zarautz","Zestoa","Zumaia","Zumarraga",
"Aiguaviva","Amer","Anglès","Arbúcies","Avinyonet de Puigventós","Banyoles","Bàscara","Begur","Besalú","Bescanó",
"Bisbal d'Empordà (La)","Biure","Blanes","Borrassà","Brunyola","Cabanelles","Cadaqués","Caldes de Malavella","Calonge",
"Campelles","Camprodon","Capmany","Cassà de la Selva","Castelló d'Empúries","Castell-Platja d'Aro","Cellera de Ter (La)","Celrà",
"Cervià de Ter","Corçà","Escala (L')","Figueres","Fontanilles","Forallac","Fornells de la Selva","Fortià","Garrigàs","Girona",
"Hostalric","Jonquera (La)","Juià","Llagostera","Llançà","Llers","Llívia","Lloret de Mar","Maçanet de Cabrenys",
"Maçanet de la Selva","Mont-ras","Olot","Palafrugell","Palamós","Palol de Revardit","Pau","Pedret i Marzà","Pera (La)",
"Planes d'Hostoles (Les)","Pont de Molins","Port de la Selva (El)","Portbou","Preses (Les)","Puigcerdà","Quart","Regencós",
"Ripoll","Riudarenes","Riudellots de la Selva","Roses","Salt","Sant Feliu de Buixalleu","Sant Feliu de Guíxols","Sant Gregori",
"Sant Hilari Sacalm","Sant Jaume de Llierca","Sant Joan de les Abadesses","Sant Joan les Fonts","Sant Jordi Desvalls",
"Sant Pere Pescador","Santa Coloma de Farners","Santa Cristina d'Aro","Santa Llogaia d'Àlguema","Sarrià de Ter","Serinyà",
"Serra de Daró","Sils","Torroella de Montgrí","Tossa de Mar","Ullà","Vall de Bianya (La)","Vall d'en Bas (La)","Verges",
"Vidreres","Viladrau","Vilamalla","Vilobí d'Onyar","Albolote","Albuñán","Albuñol","Alfacar","Algarinejo","Alhama de Granada",
"Alhendín","Almuñécar","Armilla","Atarfe","Baza","Benalúa","Benalúa de las Villas","Benamaurel","Cádiar","Calahorra (La)",
"Calicasas","Campotéjar","Caniles","Castilléjar","Castril","Cenes de la Vega","Chauchina","Churriana de la Vega","Cijuela",
"Cogollos de la Vega","Colomera","Cuevas del Campo","Cúllar","Cúllar Vega","Darro","Deifontes","Diezma","Dúrcal","Freila",
"Fuente Vaqueros","Gabias (Las)","Galera","Gor","Granada","Guadahortuna","Guadix","Gualchos","Güejar Sierra","Güevéjar","Huéneja",
"Huéscar","Huétor de Santillán","Huétor Tájar","Huétor Vega","Illora","Iznalloz","Jayena","Jete","Jun","Láchar","Lanjarón",
"Lecrín","Loja","Maracena","Moclín","Molvízar","Monachil","Montefrío","Montejícar","Montillana","Moraleda de Zafayona","Morelábor",
"Motril","Nevada","Nigüelas","Ogíjares","Orce","Órgiva","Otura","Padul","Peligros","Peza (La)","Píñar","Pinos Puente",
"Puebla de Don Fadrique","Pulianas","Purullena","Salar","Salobreña","Santa Fe","Ugíjar","Vegas del Genil","Vélez de Benaudalla",
"Ventas de Huelma","Villamena","Villanueva de las Torres","Zafarraya","Zagra","Zubia (La)","Zújar","Alcolea del Pinar",
"Almadrones","Almoguera","Almonacid de Zorita","Alovera","Atienza","Azuqueca de Henares","Berninches","Brihuega",
"Cabanillas del Campo","Campillo de Dueñas","Casar (El)","Chiloeches","Cifuentes","Condemios de Arriba","Espinosa de Henares",
"Fontanar","Guadalajara","Humanes","Jadraque","Ledanca","Maranchón","Marchamalo","Mirabueno","Molina de Aragón","Mondéjar",
"Pastrana","Pioz","Poveda de la Sierra","Pozo de Guadalajara","Quer","Sacecorbo","Sacedón","Saúca","Sigüenza","Torija",
"Torrejón del Rey","Torremocha del Campo","Trijueque","Villanueva de la Torre","Viñuelas","Yebra","Yunquera de Henares",
"Aljaraque","Almonte","Alosno","Aracena","Ayamonte","Beas","Berrocal","Bollullos Par del Condado","Bonares","Cala","Calañas",
"Cartaya","Cerro de Andévalo (El)","Chucena","Cortegana","Encinasola","Escacena del Campo","Gibraleón","Granado (El)",
"Higuera de la Sierra","Hinojos","Huelva","Isla Cristina","Lepe","Lucena del Puerto","Manzanilla","Minas de Riotinto","Moguer",
"Nava (La)","Nerva","Niebla","Palma del Condado (La)","Palos de la Frontera","Paterna del Campo","Paymogo","Puebla de Guzmán",
"Punta Umbría","Rociana del Condado","Rosal de la Frontera","San Bartolomé de la Torre","San Juan del Puerto",
"Santa Bárbara de Casa","Santa Olalla del Cala","Trigueros","Valverde del Camino","Villablanca","Villalba del Alcor",
"Villanueva de los Castillejos","Villarrasa","Zalamea la Real","Albalate de Cinca","Albero Bajo","Alcampell","Alcubierre",
"Almudévar","Altorricón","Ayerbe","Ballobar","Barbastro","Benabarre","Bielsa","Biescas","Binaced","Binéfar","Boltaña","Broto",
"Campo","Candasnos","Canfranc","Capella","Castejón de Sos","Castejón del Puente","Esplús","Estadilla","Estopiñán del Castillo",
"Fonz","Fraga","Grado (El)","Grañén","Graus","Gurrea de Gállego","Huesca","Isábena","Jaca","Labuerda","Lalueza","Lanaja",
"Loporzano","Monzón","Nueno","Ontiñena","Osso de Cinca","Peñalba","Peraltilla","Puente la Reina de Jaca","Sabiñánigo",
"Sallent de Gállego","San Miguel del Cinca","Sariñena","Secastilla","Sena","Siétamo","Sotonera (La)","Tamarite de Litera",
"Tardienta","Tella-Sin","Torrente de Cinca","Valle de Hecho","Villanova","Villanúa","Villanueva de Sigena","Zaidín",
"Albanchez de Mágina","Alcalá la Real","Alcaudete","Andújar","Arjona","Arjonilla","Arquillos","Arroyo del Ojanco","Baeza",
"Bailén","Baños de la Encina","Beas de Segura","Bedmar y Garcíez","Begíjar","Bélmez de la Moraleda","Cabra del Santo Cristo",
"Cambil","Campillo de Arenas","Canena","Carboneros","Cárcheles","Carolina (La)","Castellar","Castillo de Locubín","Cazalilla",
"Cazorla","Chiclana de Segura","Chilluévar","Frailes","Fuerte del Rey","Guardia de Jaén (La)","Guarromán","Huelma","Huesa",
"Ibros","Iruela (La)","Iznatoraf","Jabalquinto","Jaén","Jamilena","Jimena","Jódar","Lahiguera","Linares","Lopera","Mancha Real",
"Marmolejo","Martos","Mengíbar","Montizón","Navas de San Juan","Noalejo","Orcera","Peal de Becerro","Pegalajar","Porcuna",
"Pozo Alcón","Puente de Génave","Puerta de Segura (La)","Quesada","Rus","Sabiote","Santa Elena","Santiago-Pontones",
"Santisteban del Puerto","Santo Tomé","Segura de la Sierra","Siles","Sorihuela del Guadalimar","Torre del Campo",
"Torreblascopedro","Torredonjimeno","Torreperogil","Torres","Úbeda","Valdepeñas de Jaén","Vilches","Villacarrillo",
"Villanueva de la Reina","Villanueva del Arzobispo","Villares (Los)","Villatorres","Antigua (La)","Ardón","Astorga",
"Bañeza (La)","Bembibre","Boñar","Brazuelo","Burgo Ranero (El)","Cabreros del Río","Cacabelos","Campo de Villavidel",
"Camponaraya","Carrizo","Carrocera","Carucedo","Castrocalbón","Castrocontrigo","Chozas de Abajo","Cistierna","Congosto",
"Cubillas de Rueda","Cubillos del Sil","Fabero","Fresno de la Vega","Hospital de Órbigo","Laguna de Negrillos","León",
"Mansilla de las Mulas","Mansilla Mayor","Onzonilla","Páramo del Sil","Pola de Gordón (La)","Ponferrada","Puebla de Lillo",
"Puente de Domingo Flórez","Riaño","Riego de la Vega","Riello","Rioseco de Tapia","Robla (La)","Roperuelos del Páramo","Sahagún",
"San Andrés del Rabanedo","San Emiliano","Santa Cristina de Valmadrigal","Santa María de la Isla","Santa María del Páramo",
"Santovenia de la Valdoncina","Sariegos","Sena de Luna","Toral de los Guzmanes","Toreno","Trabadelo","Turcia","Urdiales del Páramo",
"Valdefresno","Valdepolo","Valderas","Valderrueda","Valdevimbre","Valencia de Don Juan","Valverde de la Virgen",
"Vega de Espinareda","Vega de Valcarce","Villablino","Villadangos del Páramo","Villadecanes","Villagatón","Villamañán",
"Villamanín","Villamejil","Villanueva de las Manzanas","Villaquejida","Villaquilambre","Villarejo de Órbigo","Villaturiel",
"Agramunt","Alamús (Els)","Albatàrrec","Albesa","Alcarràs","Alcoletge","Alfarràs","Alfés","Algerri","Alguaire","Almacelles",
"Almenar","Alpicat","Anglesola","Arbeca","Artesa de Lleida","Artesa de Segre","Aspa","Balaguer","Bassella","Bausen",
"Bellcaire d'Urgell","Bell-lloc d'Urgell","Bellpuig","Bellver de Cerdanya","Bellvís","Benavent de Segrià","Borges Blanques (Les)",
"Cervera","Coll de Nargó","Corbins","Cubells","Espot","Esterri d'Àneu","Fondarella","Fuliola (La)","Gimenells i el Pla de la Font",
"Golmés","Granyanella","Guissona","Isona i Conca Dellà","Ivars d'Urgell","Juncosa","Juneda","Linyola","Llardecans","Lleida",
"Lles de Cerdanya","Maials","Miralcamp","Mollerussa","Montferrer i Castellbò","Montoliu de Lleida","Naut Aran","Oliana","Olius",
"Organyà","Palau d'Anglesola (El)","Pinós","Plans de Sió (Els)","Pobla de Segur (La)","Pont de Suert (El)","Ponts",
"Prats i Sansor","Rialp","Rosselló","Sant Guim de Freixenet","Sant Llorenç de Morunys","Sant Ramon","Seròs","Seu d'Urgell (La)",
"Sidamon","Solsona","Soriguera","Sort","Soses","Sudanell","Sunyer","Tàrrega","Térmens","Torà","Tornabous","Torrefarrera",
"Torregrossa","Torrelameu","Torres de Segre","Tremp","Vall de Boí (La)","Vallfogona de Balaguer","Verdú","Vielha e Mijaran",
"Vilagrassa","Vilaller","Vilamòs","Vilanova de la Barca","Vila-sana","Abadín","Alfoz","Antas de Ulla","Baleira","Baralla",
"Barreiros","Becerreá","Begonte","Burela","Carballedo","Castro de Rei","Castroverde","Cervo","Chantada","Corgo (O)","Cospeito",
"Fonsagrada (A)","Foz","Friol","Guitiriz","Guntín","Lourenzá","Lugo","Meira","Mondoñedo","Monforte de Lemos","Nogais (As)",
"Outeiro de Rei","Palas de Rei","Pantón","Paradela","Pastoriza (A)","Pedrafita do Cebreiro","Pobra do Brollón (A)","Pol",
"Pontenova (A)","Portomarín","Quiroga","Rábade","Ribadeo","Riotorto","Samos","Sarria","Saviñao (O)","Vilalba","Viveiro",
"Xermade","Xove","Ajalvir","Álamo (El)","Alcalá de Henares","Alcobendas","Alcorcón","Aldea del Fresno","Algete","Alpedrete",
"Aranjuez","Arganda del Rey","Becerril de la Sierra","Boadilla del Monte","Boalo (El)","Brunete","Buitrago del Lozoya",
"Bustarviejo","Cabrera (La)","Cadalso de los Vidrios","Campo Real","Casarrubuelos","Cercedilla","Chinchón","Ciempozuelos",
"Cobeña","Collado Mediano","Collado Villalba","Colmenar de Oreja","Colmenar del Arroyo","Colmenar Viejo","Coslada",
"Daganzo de Arriba","Escorial (El)","Estremera","Fuenlabrada","Fuente el Saz de Jarama","Fuentidueña de Tajo","Galapagar",
"Getafe","Griñón","Guadalix de la Sierra","Guadarrama","Hoyo de Manzanares","Humanes de Madrid","Leganés","Loeches","Lozoya",
"Lozoyuela-Navas-Sieteiglesias","Madrid","Majadahonda","Manzanares el Real","Meco","Mejorada del Campo","Miraflores de la Sierra",
"Molar (El)","Moraleja de Enmedio","Moralzarzal","Móstoles","Navacerrada","Navalcarnero","Navas del Rey","Nuevo Baztán",
"Orusco de Tajuña","Paracuellos de Jarama","Parla","Pelayos de la Presa","Perales de Tajuña","Pezuela de las Torres","Pinto",
"Pozuelo de Alarcón","Rascafría","Rivas-Vaciamadrid","Robledo de Chavela","Rozas de Madrid (Las)","San Agustín del Guadalix",
"San Fernando de Henares","San Lorenzo de El Escorial","San Martín de la Vega","San Martín de Valdeiglesias",
"San Sebastián de los Reyes","Serna del Monte (La)","Sevilla la Nueva","Somosierra","Soto del Real","Talamanca de Jarama",
"Tielmes","Torrejón de Ardoz","Torrejón de la Calzada","Torrejón de Velasco","Torrelaguna","Torrelodones","Torres de la Alameda",
"Tres Cantos","Valdemorillo","Valdemoro","Valdetorres de Jarama","Velilla de San Antonio","Venturada","Villa del Prado",
"Villaconejos","Villalbilla","Villamanta","Villanueva de la Cañada","Villanueva de Perales","Villanueva del Pardillo",
"Villarejo de Salvanés","Villaviciosa de Odón","Alameda","Alfarnate","Algarrobo","Alhaurín de la Torre","Alhaurín el Grande",
"Almargen","Álora","Alozaina","Antequera","Archidona","Ardales","Arriate","Benalmádena","Benamargosa","Benaoján","Burgo (El)",
"Campillos","Cañete la Real","Cártama","Casabermeja","Casarabonela","Casares","Coín","Colmenar","Cómpeta","Cortes de la Frontera",
"Cuevas Bajas","Cuevas de San Marcos","Cuevas del Becerro","Estepona","Frigiliana","Fuengirola","Fuente de Piedra","Gaucín",
"Guaro","Humilladero","Málaga","Manilva","Marbella","Mijas","Mollina","Monda","Nerja","Ojén","Periana","Pizarra",
"Rincón de la Victoria","Riogordo","Ronda","Sayalonga","Sierra de Yeguas","Teba","Torremolinos","Torrox","Valle de Abdalajís",
"Vélez-Málaga","Villanueva de Algaidas","Villanueva de Tapia","Villanueva del Rosario","Villanueva del Trabuco","Viñuela",
"Yunquera","Melilla","Abanilla","Abarán","Águilas","Alcantarilla","Alcázares (Los)","Aledo","Alhama de Murcia","Archena",
"Beniel","Blanca","Bullas","Calasparra","Caravaca de la Cruz","Cartagena","Cehegín","Ceutí","Cieza","Fortuna",
"Fuente Álamo de Murcia","Jumilla","Librilla","Lorca","Lorquí","Mazarrón","Molina de Segura","Moratalla","Mula","Murcia","Pliego",
"Puerto Lumbreras","San Javier","San Pedro del Pinatar","Santomera","Torre-Pacheco","Torres de Cotillas (Las)","Totana",
"Unión (La)","Yecla","Ablitas","Aibar/Oibar","Allo","Altsasu/Alsasua","Améscoa Baja","Andosilla","Ansoáin","Anue",
"Aoiz/Agoitz","Araitz","Arakil","Aranguren","Arcos (Los)","Arguedas","Aribe","Arróniz","Artajona","Azagra","Barañain",
"Barásoain","Baztan","Bera/Vera de Bidasoa","Berbinzana","Beriáin","Berrioplano","Berriozar","Bertizarana","Buñuel",
"Burlada/Burlata","Cabanillas","Cadreita","Caparroso","Cárcar","Carcastillo","Cascante","Cáseda","Castejón","Cintruénigo",
"Corella","Cortes","Doneztebe/Santesteban","Egüés","Erro","Estella/Lizarra","Esteribar","Etxalar","Etxarri-Aranatz","Ezcabarte"
"Falces","Fitero","Fontellas","Funes","Fustiñana","Galar","Huarte/Uharte","Irurtzun","Iza","Lakuntza","Lantz","Larraga","Larraun",
"Legarda","Leitza","Lerín","Lesaka","Liédena","Lodosa","Lumbier","Luzaide/Valcarlos","Marcilla","Mélida","Mendavia","Mendigorría",
"Milagro","Miranda de Arga","Morentin","Murchante","Murillo el Fruto","Noáin (Valle de Elorz)/Noain (Elortzibar)",
"Olazti/Olazagutía","Olite","Olza","Orcoyen","Oronz","Oteiza","Pamplona/Iruña","Peralta","Puente la Reina/Gares","Ribaforada",
"San Adrián","Sangüesa/Zangoza","Santacara","Sartaguda","Sesma","Tafalla","Tiebas-Muruarte de Reta","Tudela","Ujué","Ultzama",
"Urdazubi/Urdax","Urzainqui","Valtierra","Viana","Villafranca","Villatuerta","Villava/Atarrabia","Yerri","Ziordia",
"Zizur Mayor/Zizur Nagusia","Allariz","Avión","Bande","Barbadás","Barco de Valdeorras (O)","Beade","Bolo (O)","Carballiño (O)",
"Cartelle","Castrelo de Miño","Castro Caldelas","Celanova","Coles","Cortegada","Cualedro","Entrimo","Gudiña (A)","Lobeira",
"Maceda","Maside","Melón","Merca (A)","Mezquita (A)","Nogueira de Ramuín","Ourense","Padrenda","Pereiro de Aguiar (O)",
"Peroxa (A)","Piñor","Pobra de Trives (A)","Ramirás","Ribadavia","Riós","Rúa (A)","San Cibrao das Viñas","San Cristovo de Cea",
"Taboadela","Trasmiras","Verea","Verín","Viana do Bolo","Vilamarín","Vilamartín de Valdeorras","Xinzo de Limia",
"Aguilar de Campoo","Alar del Rey","Ampudia","Amusco","Astudillo","Baltanás","Barruelo de Santullán","Carrión de los Condes",
"Cervera de Pisuerga","Cevico de la Torre","Dueñas","Fresno del Río","Frómista","Fuentes de Nava","Grijota","Guardo",
"Herrera de Pisuerga","Magaz de Pisuerga","Osorno la Mayor","Palencia","Paredes de Nava","Quintana del Puente","Saldaña",
"Santibáñez de la Peña","Torquemada","Venta de Baños","Villada","Villaherreros","Villamuriel de Cerrato","Villarramiel",
"Villodrigo","Villoldo","Agaete","Agüimes","Aldea de San Nicolás (La)","Antigua","Arrecife","Artenara","Arucas","Firgas",
"Gáldar","Haría","Ingenio","Mogán","Moya","Oliva (La)","Pájara","Palmas de Gran Canaria (Las)","Puerto del Rosario",
"San Bartolomé","San Bartolomé de Tirajana","Santa Brígida","Santa Lucía de Tirajana","Santa María de Guía de Gran Canaria",
"Teguise","Tejeda","Telde","Teror","Tías","Tinajo","Tuineje","Valleseco","Valsequillo de Gran Canaria","Vega de San Mateo",
"Yaiza","Agolada","Arbo","Baiona","Barro","Bueu","Caldas de Reis","Cambados","Campo Lameiro","Cangas","Cañiza (A)","Catoira",
"Cerdedo","Cotobade","Covelo","Cuntis","Dozón","Estrada (A)","Forcarei","Gondomar","Grove (O)","Guarda (A)","Lalín","Marín",
"Meaño","Moaña","Mondariz-Balneario","Moraña","Mos","Neves (As)","Nigrán","Oia","Pazos de Borbén","Poio","Ponte Caldelas",
"Ponteareas","Pontecesures","Pontevedra","Porriño (O)","Portas","Redondela","Ribadumia","Rodeiro","Salceda de Caselas",
"Salvaterra de Miño","Sanxenxo","Silleda","Tomiño","Tui","Valga","Vigo","Vila de Cruces","Vilaboa","Vilagarcía de Arousa",
"Vilanova de Arousa","Agoncillo","Albelda de Iregua","Alberite","Alcanadre","Aldeanueva de Ebro","Alfaro","Arnedo","Autol",
"Bañares","Baños de Río Tobía","Briones","Calahorra","Cenicero","Cervera del Río Alhama","Cuzcurrita de Río Tirón","Haro",
"Hormilla","Huércanos","Lardero","Logroño","Murillo de Río Leza","Nájera","Nalda","Navarrete","Pradejón","Quel","Redal (El)",
"Rincón de Soto","San Asensio","San Vicente de la Sonsierra","Tirgo","Villamediana de Iregua","Villanueva de Cameros",
"Villar de Torre","Viniegra de Abajo","Alba de Tormes","Alberca (La)","Aldeanueva de Figueroa","Aldeatejada",
"Aldehuela de la Bóveda","Arapiles","Barruecopardo","Béjar","Buenavista","Cabrerizos","Calvarrasa de Abajo","Calvarrasa de Arriba",
"Calzada de Valdunciel","Cantalapiedra","Cantalpino","Carbajosa de la Sagrada","Castellanos de Moriscos","Ciudad Rodrigo",
"Encinas de Abajo","Espeja","Fresno Alhándiga","Fuente de San Esteban (La)","Fuentes de Oñoro","Galindo y Perahuy","Guijuelo",
"Horcajo Medianero","Ledesma","Linares de Riofrío","Lumbrales","Macotera","Martín de Yeltes","Masueco","Montejo",
"Pedrosillo el Ralo","Peñaranda de Bracamonte","Puerto de Béjar","Robleda","Robliza de Cojos","Salamanca","Sancti-Spíritus",
"Santa Marta de Tormes","Tamames","Trabanca","Valdecarros","Vecinos","Villamayor","Villar de Peralonso","Villares de la Reina",
"Villarmayor","Villoria","Vitigudino","Adeje","Alajeró","Arafo","Arico","Arona","Barlovento","Breña Alta","Buenavista del Norte",
"Candelaria","Fasnia","Frontera","Fuencaliente de la Palma","Garachico","Garafía","Granadilla de Abona","Guancha (La)",
"Guía de Isora","Güímar","Hermigua","Icod de los Vinos","Llanos de Aridane (Los)","Matanza de Acentejo (La)","Orotava (La)",
"Paso (El)","Puerto de la Cruz","Puntagorda","Puntallana","Realejos (Los)","Rosario (El)","San Andrés y Sauces",
"San Cristóbal de La Laguna","San Juan de la Rambla","San Miguel de Abona","San Sebastián de la Gomera","Santa Cruz de la Palma"
,"Santa Cruz de Tenerife","Santa Úrsula","Santiago del Teide","Sauzal (El)","Silos (Los)","Tacoronte","Tanque (El)","Tegueste",
"Valle Gran Rey","Vallehermoso","Valverde","Victoria de Acentejo (La)","Vilaflor","Villa de Mazo","Ayllón","Boceguillas",
"Cantalejo","Carbonero el Mayor","Castillejo de Mesleón","Cerezo de Abajo","Chañe","Coca","Collado Hermoso","Cuéllar",
"Espinar (El)","Fresno de Cantespino","Fuentepelayo","Fuentesaúco de Fuentidueña","Garcillán","Gomezserracín","Grajera",
"Hontalbilla","Labajos","Lastrilla (La)","Martín Muñoz de la Dehesa","Martín Muñoz de las Posadas","Mozoncillo",
"Nava de la Asunción","Navalmanzano","Navas de San Antonio","Palazuelos de Eresma","Pradales","Prádena","Riaza",
"San Cristóbal de Segovia","San Ildefonso","San Miguel de Bernuy","Sangarcía","Santa María la Real de Nieva",
"Santo Tomé del Puerto","Segovia","Sepúlveda","Tolocirio","Torrecaballeros","Turégano","Vallelado","Valseca",
"Valverde del Majano","Villacastín","Aguadulce","Alanís","Alcalá de Guadaíra","Alcalá del Río","Alcolea del Río","Algaba (La)",
"Algámitas","Almadén de la Plata","Almensilla","Arahal","Aznalcázar","Aznalcóllar","Badolatosa","Benacazón",
"Bollullos de la Mitación","Bormujos","Brenes","Burguillos","Cabezas de San Juan (Las)","Camas","Campana (La)","Cañada Rosal",
"Cantillana","Carmona","Carrión de los Céspedes","Casariche","Castilblanco de los Arroyos","Castilleja de la Cuesta",
"Castillo de las Guardas (El)","Cazalla de la Sierra","Constantina","Coria del Río","Coripe","Coronil (El)","Corrales (Los)",
"Cuervo de Sevilla (El)","Dos Hermanas","Écija","Espartinas","Estepa","Fuentes de Andalucía","Garrobo (El)","Gelves","Gerena",
"Gilena","Gines","Guadalcanal","Guillena","Herrera","Huévar del Aljarafe","Isla Mayor","Lantejuela (La)","Lebrija","Lora del Río",
"Luisiana (La)","Mairena del Alcor","Mairena del Aljarafe","Marchena","Marinaleda","Martín de la Jara","Molares (Los)",
"Montellano","Morón de la Frontera","Navas de la Concepción (Las)","Olivares","Osuna","Palacios y Villafranca (Los)",
"Palomares del Río","Paradas","Pedrera","Pedroso (El)","Peñaflor","Pilas","Pruna","Puebla de Cazalla (La)",
"Puebla de los Infantes (La)","Puebla del Río (La)","Real de la Jara (El)","Rinconada (La)","Roda de Andalucía (La)","Rubio (El)",
"Salteras","San Juan de Aznalfarache","Sanlúcar la Mayor","Santiponce","Saucejo (El)","Sevilla","Tocina","Tomares","Umbrete",
"Utrera","Valencina de la Concepción","Villamanrique de la Condesa","Villanueva de San Juan","Villanueva del Ariscal",
"Villanueva del Río y Minas","Villaverde del Río","Viso del Alcor (El)","Abejar","Ágreda","Almarza","Almazán","Arcos de Jalón",
"Berlanga de Duero","Burgo de Osma-Ciudad de Osma","Cabrejas del Pinar","Calatañazor","Golmayo","Langa de Duero","Matalebreras",
"Medinaceli","Ólvega","Rábanos (Los)","San Esteban de Gormaz","San Leonardo de Yagüe","San Pedro Manrique","Santa María de Huerta",
"Soria","Alcanar","Alcover","Aldea (L')","Alforja","Altafulla","Ametlla de Mar (L')","Ampolla (L')","Amposta","Arboç (L')",
"Batea","Bellvei","Benifallet","Benissanet","Bisbal del Penedès (La)","Bot","Bràfim","Calafell","Camarles","Cambrils",
"Catllar (El)","Constantí","Cornudella de Montsant","Cunit","Deltebre","Espluga de Francolí (L')","Falset","Fatarella (La)",
"Flix","Galera (La)","Gandesa","Horta de Sant Joan","Llorenç del Penedès","Mas de Barberans","Montblanc","Montbrió del Camp",
"Mont-roig del Camp","Móra d'Ebre","Móra la Nova","Morell (El)","Perafort","Perelló (El)","Pla de Santa Maria (El)",
"Pobla de Mafumet (La)","Prades","Rasquera","Reus","Riudoms","Roda de Barà","Roquetes","Salou","Sant Carles de la Ràpita",
"Sant Jaume dels Domenys","Sant Jaume d'Enveja","Santa Bàrbara","Santa Coloma de Queralt","Santa Oliva","Sarral",
"Selva del Camp (La)","Sénia (La)","Solivella","Tarragona","Tivissa","Torredembarra","Tortosa","Ulldecona","Valls",
"Vandellòs i l'Hospitalet de l'Infant","Vendrell (El)","Vilalba dels Arcs","Vilallonga del Camp","Vila-rodona","Vila-seca",
"Vilaverd","Vinebre","Vinyols i els Arcs","Xerta","Aguaviva","Alba","Albalate del Arzobispo","Albarracín","Albentosa",
"Alcalá de la Selva","Alcañiz","Alcorisa","Andorra","Bañón","Barrachina","Bello","Blancas","Calaceite","Calamocha","Calanda",
"Camarillas","Caminreal","Cantavieja","Castellote","Castelserás","Celadas","Cella","Codoñera (La)","Cretas","Ferreruela de Huerva",
"Fuentes Calientes","Fuentes Claras","Fuentespalda","Híjar","Jarque de la Val","Lagueruela","Mas de las Matas","Mazaleón",
"Mezquita de Jarque","Monreal del Campo","Monroyo","Mora de Rubielos","Muniesa","Odón","Ojos Negros","Orrios","Pancrudo",
"Peñarroya de Tastavins","Perales del Alfambra","Pobo (El)","Portellada (La)","Puebla de Híjar (La)","Puebla de Valverde (La)",
"Rubielos de Mora","Santa Eulalia","Sarrión","Teruel","Tornos","Torralba de los Sisones","Torrecilla de Alcañiz",
"Torrecilla del Rebollar","Torrijo del Campo","Utrillas","Valdealgorfa","Valderrobres","Valjunquera","Villafranca del Campo",
"Villarquemado","Villastar","Visiedo","Ajofrín","Alameda de la Sagra","Albarreal de Tajo","Alcabón","Alcolea de Tajo",
"Almonacid de Toledo","Almorox","Añover de Tajo","Argés","Bargas","Belvís de la Jara","Burguillos de Toledo",
"Cabañas de la Sagra","Cabezamesada","Calera y Chozas","Calzada de Oropesa","Camarena","Camuñas","Carmena","Carpio de Tajo (El)",
"Carranque","Casar de Escalona (El)","Casarrubios del Monte","Castillo de Bayuela","Cazalegas","Cebolla","Cedillo del Condado",
"Cerralbos (Los)","Chozas de Canales","Cobisa","Consuegra","Corral de Almaguer","Cuerva","Dosbarrios","Escalona","Escalonilla",
"Espinoso del Rey","Esquivias","Fuensalida","Gálvez","Gerindote","Guadamur","Guardia (La)","Herreruela de Oropesa",
"Huerta de Valdecarábanos","Illescas","Lillo","Madridejos","Malpica de Tajo","Maqueda","Mascaraque","Mazarambroz","Menasalbas",
"Méntrida","Miguel Esteban","Mocejón","Mora","Nava de Ricomalillo (La)","Navahermosa","Navalcán","Navalmorales (Los)",
"Navalucillos (Los)","Noblejas","Numancia de la Sagra","Ocaña","Olías del Rey","Ontígola","Orgaz","Oropesa","Otero","Pantoja",
"Pepino","Polán","Portillo de Toledo","Puebla de Almoradiel (La)","Puebla de Montalbán (La)","Pueblanueva (La)","Pulgar",
"Quero","Quintanar de la Orden","Real de San Vicente (El)","Recas","Romeral (El)","San Bartolomé de las Abiertas",
"San Martín de Pusa","San Pablo de los Montes","Santa Ana de Pusa","Santa Cruz de la Zarza","Santa Cruz del Retamar",
"Santa Olalla","Santo Domingo-Caudilla","Seseña","Sevilleja de la Jara","Sonseca","Talavera de la Reina","Tembleque","Toboso (El)",
"Toledo","Torre de Esteban Hambrán (La)","Torrijos","Turleque","Ugena","Urda","Valmojado","Ventas de Retamosa (Las)",
"Villa de Don Fadrique (La)","Villacañas","Villafranca de los Caballeros","Villaluenga de la Sagra","Villamiel de Toledo",
"Villamuelas","Villanueva de Alcardete","Villanueva de Bogas","Villarrubia de Santiago","Villaseca de la Sagra","Villasequilla",
"Villatobas","Viso de San Juan (El)","Yébenes (Los)","Yeles","Yepes","Yuncler","Yuncos","Ademuz","Agullent","Aielo de Malferit",
"Alaquàs","Albaida","Albal","Albalat de la Ribera","Albalat dels Sorells","Alberic","Alborache","Alboraya","Albuixech","Alcàsser",
"Alcublas","Alcúdia (l')","Alcúdia de Crespins (l')","Aldaia","Alfafar","Alfarp","Algemesí","Algimia de Alfara","Alginet",
"Almàssera","Almiserà","Almoines","Almussafes","Alpuente","Alquería de la Condesa/Alqueria de la Comtessa (l')","Alzira","Andilla",
"Anna","Ayora","Barxeta","Bellreguard","Benaguasil","Beneixida","Benetússer","Beniarjó","Benifaió","Benigánim","Benimodo",
"Beniparrell","Benisanó","Bétera","Bocairent","Bugarra","Buñol","Burjassot","Camporrobles","Canals","Canet d'En Berenguer",
"Carcaixent","Carlet","Casinos","Castelló de Rugat","Castielfabib","Catadau","Catarroja","Caudete de las Fuentes","Chella",
"Chelva","Cheste","Chiva","Chulilla","Corbera","Cortes de Pallás","Cullera","Daimús","Eliana (l')","Enguera","Estivella","Foios",
"Font de la Figuera (la)","Font d'En Carròs (la)","Fontanars dels Alforins","Fuenterrobles","Gandia","Genovés","Godella",
"Godelleta","Guadasequies","Guadassuar","Jalance","Jarafuel","Llíria","Llocnou de Sant Jeroni","Llosa de Ranes (la)","Llutxent",
"Loriguilla","Losa del Obispo","Manises","Marines","Masalavés","Massalfassar","Massamagrell","Massanassa","Meliana","Mislata",
"Mogente/Moixent","Moncada","Monserrat","Montaverner","Montesa","Montroy","Museros","Náquera","Navarrés","Novelé/Novetlè","Oliva",
"Olleria (l')","Olocau","Ontinyent","Otos","Paiporta","Palma de Gandía","Paterna","Pedralba","Picanya","Picassent",
"Pobla de Farnals (la)","Pobla de Vallbona (la)","Pobla del Duc (la)","Pobla Llarga (la)","Polinyà de Xúquer","Puçol","Puig",
"Quart de Poblet","Quartell","Quatretonda","Rafelbuñol/Rafelbunyol","Real de Gandía","Requena","Riba-roja de Túria",
"Sagunto/Sagunt","San Antonio de Benagéber","Sedaví","Siete Aguas","Silla","Sollana","Sueca","Tavernes de la Valldigna",
"Titaguas","Torrent","Turís","Utiel","Valencia","Vallada","Vilamarxant","Villalonga","Villanueva de Castellón",
"Villar del Arzobispo","Villargordo del Cabriel","Vinalesa","Xàtiva","Xeraco","Xirivella","Yátova","Alaejos","Alcazarén",
"Aldeamayor de San Martín","Arroyo de la Encomienda","Ataquines","Becilla de Valderaduey","Bobadilla del Campo","Boecillo",
"Cabezón de Pisuerga","Campaspero","Canalejas de Peñafiel","Casasola de Arión","Castrejón de Trabancos","Castroverde de Cerrato",
"Cigales","Cistérniga","Cogeces del Monte","Cubillas de Santa Marta","Esguevillas de Esgueva","Íscar","Laguna de Duero","Langayo",
"Mayorga","Medina de Rioseco","Medina del Campo","Mojados","Mota del Marqués","Mudarra (La)","Nava del Rey","Olmedo",
"Pedraja de Portillo (La)","Pedrajas de San Esteban","Pedrosa del Rey","Peñafiel","Portillo","Quintanilla de Onésimo",
"Renedo de Esgueva","Rueda","San Miguel del Arroyo","San Miguel del Pino","San Pedro de Latarce","San Vicente del Palacio",
"Santovenia de Pisuerga","Sardón de Duero","Serrada","Siete Iglesias de Trabancos","Simancas","Tordehumos","Tordesillas",
"Tudela de Duero","Valladolid","Vega de Valdetronco","Villalón de Campos","Villanubla","Villanueva de los Caballeros",
"Villardefrades","Zaratán","Alcañices","Almeida de Sayago","Benavente","Bermillo de Sayago","Bóveda de Toro (La)",
"Camarzana de Tera","Cañizal","Carbajales de Alba","Casaseca de las Chanas","Castrogonzalo","Cobreros","Corrales",
"Cubo de Tierra del Vino (El)","Fuentesaúco","Gamones","Granja de Moreruela","Lubián","Micereces de Tera","Mombuey",
"Montamarta","Moraleja del Vino","Morales de Toro","Morales del Vino","Muelas del Pan","Otero de Bodas","Pereruela",
"Quintanilla de Urz","Quiruelas de Vidriales","Rábano de Aliste","Robleda-Cervantes","San Cristóbal de Entreviñas",
"San Esteban del Molar","San Vitero","Santa María de la Vega","Santovenia","Sanzoles","Toro","Torre del Valle (La)",
"Villabrázaro","Villafáfila","Villalpando","Villanueva del Campo","Villarrín de Campos","Zamora","Agón","Aguarón",
"Ainzón","Alagón","Alberite de San Juan","Alfajarín","Alfamén","Almolda (La)","Almunia de Doña Godina (La)","Ambel","Aniñón",
"Ariza","Ateca","Azuara","Belchite","Biota","Borja","Brea de Aragón","Bujaraloz","Burgo de Ebro (El)","Buste (El)","Cadrete",
"Calatayud","Calatorao","Cariñena","Caspe","Castejón de Valdejasa","Castiliscar","Cervera de la Cañada","Cetina",
"Cuarte de Huerva","Cubel","Daroca","Ejea de los Caballeros","Épila","Erla","Fabara","Farlete","Frasno (El)","Fuendejalón",
"Fuentes de Ebro","Gallocanta","Gallur","Gelsa","Herrera de los Navarros","Illueca","Joyosa (La)","Langa del Castillo","Lécera",
"Leciñena","Luesia","Lumpiaque","Luna","Maella","Mainar","Mallén","María de Huerva","Monegrillo","Monreal de Ariza","Muel",
"Muela (La)","Munébrega","Nonaspe","Novallas","Nuévalos","Pedrola","Perdiguera","Pina de Ebro","Pinseque","Pozuelo de Aragón",
"Puebla de Alfindén (La)","Quinto","Remolinos","Ricla","Sabiñán","Sádaba","San Mateo de Gállego","Sástago","Sierra de Luna"
,"Sobradiel","Sos del Rey Católico","Tabuenca","Tarazona","Tauste","Used","Utebo","Valpalmas","Velilla de Ebro","Villadoz",
"Villamayor de Gállego","Villanueva de Gállego","Villanueva de Huerva","Villarreal de Huerva","Villarroya de la Sierra",
"Zaragoza","Zuera"]

provincias=["Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Barcelona", "Burgos", "Cáceres", "Cádiz", 
"Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca", "Gerona", "Granada", "Guadalajara", "Guipúzcoa", "Huelva", "Huesca", 
"Islas Baleares", "Jaén", "La Coruña", "La Rioja", "Las Palmas", "León", "Lérida", "Lugo", "Madrid", "Málaga", "Murcia", "Navarra",
"Orense", "Palencia", "Pontevedra", "Salamanca", "Santa Cruz de Tenerife", "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", 
"Toledo", "Valencia", "Valladolid", "Vizcaya", "Zamora", "Zaragoza"]