from flask import Flask
from flask_pymongo import PyMongo
import pymongo
import sys

app = Flask(__name__)	
client = PyMongo("mongodb+srv://Gestionpymongo:Gestionpymongo@cluster0.iixvr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
# mongo = PyMongo(app)
db = client.get_default_database()


@app.route('/')
def hello_world():
    return 'Hello, World!'


app.run()