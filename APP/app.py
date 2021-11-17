from flask import Flask
from flask_pymongo import PyMongo
import pymongo
import sys

app = Flask(__name__)	
client = pymongo.MongoClient("mongodb+srv://Gestionpymongo:Gestionpymongo@cluster0.iixvr.mongodb.net/iweb?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
                              
# mongo = PyMongo(app)
db = client.get_default_database()
test = db["Usuario"]

@app.route('/')
def hello_world():
    findtest = test.find()
    
    for x in findtest:
        print(x)

    return "insertado"

app.run()