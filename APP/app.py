from flask import Flask
from flask_pymongo import PyMongo
import pymongo
import sys

app = Flask(__name__)	
client = PyMongo("mongodb+srv://Gestionpymongo:Gestionpymongo@cluster0.iixvr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
# mongo = PyMongo(app)
db = client.get_default_database()

<<<<<<< HEAD

=======
app.config["MONGO_URI"] = "mongodb+srv://Gestionpymongo:Gestionpymongo@cluster0.iixvr.mongodb.net/iweb?retryWrites=true&w=majority"
mongo = PyMongo(app)
db = mongo.db
>>>>>>> a91689078e786a87fe43e43dffcec0f1ff40c660
@app.route('/')
def hello_world():
    
    
    doc = {'paco'}
    t = db['test']
    a = t.insert_one(doc)

    return "insertado"

  


app.run()