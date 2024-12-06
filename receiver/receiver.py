import socket
import threading
import json
import datetime
from database.db_connection import db_connection

#from alerting.alerts import send_email_alert, send_telegram_alert, send_email_alert2, send_telegram_alert2



class Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(('', 7713))

    def run(self):
        while True:
            rec = self._sock.recvfrom(1024)
            data = rec[0].decode('ascii')
            print("Datos recibidos:", data)  # Imprimir los datos recibidos
            self.save_data_to_database(data)

    def save_data_to_database(self, data):
        try:
            data_dict = json.loads(data)
            zone_name = data_dict['zoneName']
            rack_id = str(data_dict['Rack'])
            temperature = data_dict['Data'][0]
            humidity = data_dict['Data'][1]

            if temperature >= 179:
                print("Temperatura muy alta. No se guardará en la base de datos.")
                return

            allowed_zones = ["POD A", "POD B", "POD C", "CARRIERS", "TELCO"]
            if not zone_name or zone_name not in allowed_zones:
                print("El nombre de la zona no es válido. No se guardará en la base de datos.")
                return

            with db_connection() as conn:
                with conn.cursor() as db_cursor:
                    db_cursor.execute("SELECT idZona FROM zonas WHERE nombre = %s", (zone_name,))
                    zone_result = db_cursor.fetchone()

                    if zone_result:
                        zone_id = zone_result[0]
                    else:
                        db_cursor.execute("INSERT INTO zonas (nombre) VALUES (%s) RETURNING idZona", (zone_name,))
                        zone_id = db_cursor.fetchone()[0]

                    db_cursor.execute("SELECT idRack FROM racks WHERE nombre = %s AND zona_id = %s", (rack_id, zone_id))
                    rack_result = db_cursor.fetchone()

                    if not rack_result:
                        db_cursor.execute("INSERT INTO racks (nombre, zona_id) VALUES (%s, %s)", (rack_id, zone_id))

                    insert_query = """
                        INSERT INTO datos (fecha, hora, zona_id, rack_id, sensor_id, temperatura, humedad)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    current_datetime = datetime.datetime.now()
                    db_cursor.execute(insert_query, (current_datetime.date(), current_datetime.time(), zone_id, rack_id, 1, temperature, humidity))
                    conn.commit()


                            # Verificar si la temperatura requiere alerta
                    #if temperature >= TEMPMAX:
                        
                    #    send_email_alert(zone_name, rack_id, temperature, f"{current_datetime.date()} {current_datetime.time()}")
                    #    send_telegram_alert(zone_name, rack_id, temperature , f"{current_datetime.date()} {current_datetime.time()}")

                    #if temperature <= TEMPMIN:
                        
                    #    send_email_alert2(zone_name, rack_id, temperature, f"{current_datetime.date()} {current_datetime.time()}")
                    #    send_telegram_alert2(zone_name, rack_id, temperature , f"{current_datetime.date()} {current_datetime.time()}")


        except Exception as e:
            print(f"Error al guardar datos en la base de datos: {str(e)}")


from dash import callback, Input, Output, State


