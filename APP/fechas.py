from datetime import datetime

# Para formatear fechas con un formato de entrada y formato salida
def formatear_fecha(str_fecha, formatoEntrada, formatoSalida):
    date_obj = datetime.strptime(str_fecha, formatoEntrada)
    return datetime.strftime(date_obj, formatoSalida)

def date_to_timestamp(date, time):
    date_aux = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M')
    return datetime.timestamp(date_aux)

def timestamp_to_date(stamp):
    date_aux = datetime.fromtimestamp(stamp)
    date = datetime.strftime(date_aux, '%Y-%m-%d')
    time = datetime.strftime(date_aux, '%H:%M')
    return date, time