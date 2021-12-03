import pymongo

client = pymongo.MongoClient("mongodb+srv://Gestionpymongo:Gestionpymongo@cluster0.iixvr.mongodb.net/iweb?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = client.get_default_database()

trayecto_db = db['Trayecto']
usuario_db = db['Usuario']
vehiculo_db = db['Vehiculo']

client.close()
