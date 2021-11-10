from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)	

app.config["MONGO_URI"] = "mongodb+srv://Gestionpymongo:<Gestionpymongo>@cluster0.iixvr.mongodb.net/iweb?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
   		app.run()