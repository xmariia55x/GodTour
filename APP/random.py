from flask import Flask #, request, redirect,render_template



app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def get_post():
    ''''if request.method == 'GET':
        return render_template("/prueba.html")
    else:
        fecha = request.form.get("fecha") # formatear la fecha
        hora = request.form.get("hora")
        print(fecha)
        print(hora) 
        return redirect('/', code=302)
    '''
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()