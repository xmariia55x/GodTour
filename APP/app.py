# from logging import NullHandler
from flask import Flask, Blueprint
import sys
from datetime import datetime, timedelta
# import datos.datos_abiertos as datos_abiertos
from bp.client import bpclient
from bp.server import bpserver
from mongoDB import disconnect_database

'''ultima_actualizacion_gasolineras = 0
ultima_actualizacion_trafico = 0
class FlaskApp(Flask):
  def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
    if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
      with self.app_context():
        global gasolineras_datos_abiertos, ultima_actualizacion_gasolineras 
        gasolineras_datos_abiertos = datos_abiertos.descargar_gasolineras() 
        ultima_actualizacion_gasolineras = datetime.now()
    super(FlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)
'''
app = Flask(__name__)
# app.secret_key = 'clave de cifrado lo más robusta posible'
app.register_blueprint(bpclient)
app.register_blueprint(bpserver)

app.run()

disconnect_database()

