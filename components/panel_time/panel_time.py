import datetime
from database.db_connection import db_connection


def get_zones():
    try:
        with db_connection() as conn:
            with conn.cursor() as db_cursor:
                db_cursor.execute("SELECT * FROM zonas")
                zones = db_cursor.fetchall()

                return [zone[1] for zone in zones]  # Return a list of zone names
    except Exception as e:
        print(f"Error getting zones from the database: {str(e)}")
        return []
    
def get_monthly_average_data(start_datetime, end_datetime, selected_zone_id, selected_rack):
    data = {
        'time': [],
        'temperature': {},
        'humidity': {}
    }

    try:
        with db_connection() as conn:
            with conn.cursor() as db_cursor:
                select_query = """
                SELECT fecha, hora, rack_id, temperatura, humedad
                FROM datos
                WHERE (fecha, hora) >= (%s, %s) AND (fecha, hora) <= (%s, %s)
                AND zona_id = %s AND rack_id = %s
                ORDER BY fecha, hora
                """
                db_cursor.execute(
                    select_query, (start_datetime.date(), start_datetime.time(), end_datetime.date(), end_datetime.time(), selected_zone_id, selected_rack))
                rows = db_cursor.fetchall()

                # Seleccionar un dato cada 4 minutos (15 datos por hora)
                intervalo = 30  # en minutos
                ultimo_punto = None

                for row in rows:
                    fecha, hora, rack_id, temperatura, humedad = row
                    tiempo = datetime.datetime.combine(fecha, hora)

                    # Si el punto actual es el primero o han pasado 4 minutos desde el último punto
                    if ultimo_punto is None or (tiempo - ultimo_punto).seconds >= intervalo * 60:
                        data['time'].append(f"{fecha} {hora}")

                        if rack_id not in data['temperature']:
                            data['temperature'][rack_id] = []
                            data['humidity'][rack_id] = []

                        data['temperature'][rack_id].append(float(temperatura))
                        data['humidity'][rack_id].append(float(humedad))

                        ultimo_punto = tiempo

    except Exception as e:
        print(f"Error al obtener datos de la base de datos: {str(e)}")

    return data
    

def get_data(start_datetime, end_datetime, selected_zone_id, selected_rack, time_unit):
    data = {
        'time': [],
        'temperature': {},
        'humidity': {}
    }
    try:
        with db_connection() as conn:
            with conn.cursor() as db_cursor:
                select_query = """
                SELECT fecha, hora, rack_id, temperatura, humedad
                FROM datos
                WHERE (fecha, hora) >= (%s, %s) AND (fecha, hora) <= (%s, %s)
                AND zona_id = %s AND rack_id = %s
                ORDER BY fecha, hora
                """
                db_cursor.execute(
                    select_query, (start_datetime.date(), start_datetime.time(), end_datetime.date(), end_datetime.time(), selected_zone_id, selected_rack))
                rows = db_cursor.fetchall()

                for row in rows:
                    fecha, hora, rack_id, temperatura, humedad = row
                    tiempo = datetime.datetime.combine(fecha, hora)

                    data['time'].append(f"{fecha} {hora}")

                    if rack_id not in data['temperature']:
                        data['temperature'][rack_id] = []
                        data['humidity'][rack_id] = []

                    data['temperature'][rack_id].append(float(temperatura))
                    data['humidity'][rack_id].append(float(humedad))

    except Exception as e:
        print(f"Error al obtener datos de la base de datos: {str(e)}")
    return data
