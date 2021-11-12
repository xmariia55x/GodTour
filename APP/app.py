from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)	

app.config["MONGO_URI"] = "mongodb+srv://Gestionpymongo:Gestionpymongo@cluster0.iixvr.mongodb.net/iweb?retryWrites=true&w=majority"
mongo = PyMongo(app)
db = mongo.db
@app.route('/')
def hello_world():
    
    
    doc = {'paco'}
    t = db['test']
    a = t.insert_one(doc)

    return "insertado"

  

if __name__ == '__main__':
   		app.run()