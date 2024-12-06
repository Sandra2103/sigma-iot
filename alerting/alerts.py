import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import json

from tabs.tab4 import  EMAIL_LIST_FILE, load_email_list, save_email_list, manage_email_list, email_list, CONFIG

#############################Mensaje de correo##########################

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests


import smtplib
import requests
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Configuración de correo
EMAIL_SENDER = "sandra.martinez@infotec.mx"
EMAIL_PASSWORD = "Ms4ndr4t.2024"  # Cambia esto por un token seguro
SMTP_SERVER = "mail.infotec.mx"
SMTP_PORT = 587

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Inicia una conexión segura
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)  # Intenta iniciar sesión
        print("Conexión SMTP exitosa.")
except smtplib.SMTPAuthenticationError:
    print("Error de autenticación: Verifica tu correo o contraseña.")
except Exception as e:
    print(f"Error al conectarse al servidor SMTP: {e}")


TELEGRAM_BOT_TOKEN = "7275549555:AAFc9kzYUvIpnw9YukvzYFmKHqA3UHEkLRA"
TELEGRAM_CHANNEL = "SigmaIoTcd"

def send_email_alert(zone, rack, temperature, date_time):
    """Envía una alerta por correo electrónico."""
    subject = f"Sigma-IoT: Alerta de Temperatura maxima- Zona: {zone}, Rack: {rack}"
    body = f"""
    <html>
      <body>
        <h1 style="color: #621132;">Sigma-IoT: Alerta de Temperatura</h1>
        <p><b>Temperatura:</b> {temperature:.2f}°C</p>
        <p><b>Zona:</b> {zone}</p>
        <p><b>Rack:</b> {rack}</p>
        <p><b>Fecha y Hora:</b> {date_time}</p>
      </body>
    </html>
    """

    try:
        # Leer lista de correos
        with open("email_list.json", "r") as f:
            recipients = json.load(f)

        if not recipients:
            print("La lista de correos está vacía. No se enviarán alertas.")
            return

        # Crear el mensaje
        message = MIMEMultipart()
        message["From"] = EMAIL_SENDER
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        # Adjuntar imagen (si existe)
        try:
            with open("assets/banerCorreo.png", "rb") as f:
                banner = MIMEImage(f.read())
                banner.add_header("Content-ID", "<banner>")
                message.attach(banner)
        except FileNotFoundError:
            print("La imagen de banner no se encontró. Continuando sin ella.")

        # Conexión SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Iniciar conexión segura
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            for recipient in recipients:
                message["To"] = recipient
                server.sendmail(EMAIL_SENDER, recipient, message.as_string())
                print(f"Correo enviado correctamente a (maxima) {recipient}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


def send_telegram_alert(zone, rack, temperature, date_time):
    """Envía una alerta por Telegram."""
    message = f"""
*Sigma-IoT: Alerta de Temperatura*
Zona: {zone}
Rack: {rack}
Temperatura: {temperature:.2f}°C
Fecha y Hora: {date_time}
"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": f"@{TELEGRAM_CHANNEL}",
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, params=params)
        response.raise_for_status()
        print("Alerta de Telegram enviada maxima.")
    except Exception as e:
        print(f"Error al enviar alerta por Telegram: {e}")




def send_email_alert2(zone, rack, temperature, date_time):
    """Envía una alerta por correo electrónico."""
    subject = f"Sigma-IoT: Alerta de Temperatura minima- Zona: {zone}, Rack: {rack}"
    body = f"""
    <html>
      <body>
        <h1 style="color: #621132;">Sigma-IoT: Alerta de Temperatura</h1>
        <p><b>Temperatura:</b> {temperature:.2f}°C</p>
        <p><b>Zona:</b> {zone}</p>
        <p><b>Rack:</b> {rack}</p>
        <p><b>Fecha y Hora:</b> {date_time}</p>
      </body>
    </html>
    """

    try:
        # Leer lista de correos
        with open("email_list.json", "r") as f:
            recipients = json.load(f)

        if not recipients:
            print("La lista de correos está vacía. No se enviarán alertas.")
            return

        # Crear el mensaje
        message = MIMEMultipart()
        message["From"] = EMAIL_SENDER
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        # Adjuntar imagen (si existe)
        try:
            with open("assets/banerCorreo.png", "rb") as f:
                banner = MIMEImage(f.read())
                banner.add_header("Content-ID", "<banner>")
                message.attach(banner)
        except FileNotFoundError:
            print("La imagen de banner no se encontró. Continuando sin ella.")

        # Conexión SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Iniciar conexión segura
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            for recipient in recipients:
                message["To"] = recipient
                server.sendmail(EMAIL_SENDER, recipient, message.as_string())
                print(f"Correo enviado correctamente a (minima){recipient}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


def send_telegram_alert2(zone, rack, temperature, date_time):
    """Envía una alerta por Telegram."""
    message = f"""
*Sigma-IoT: Alerta de Temperatura minima*
Zona: {zone}
Rack: {rack}
Temperatura: {temperature:.2f}°C
Fecha y Hora: {date_time}
"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": f"@{TELEGRAM_CHANNEL}",
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, params=params)
        response.raise_for_status()
        print("Alerta de Telegram enviada minima")
    except Exception as e:
        print(f"Error al enviar alerta por Telegram: {e}")
