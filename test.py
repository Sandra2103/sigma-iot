import smtplib

EMAIL_SENDER = "sigma.martinez@infotec.mx"
EMAIL_PASSWORD = "Ms4ndr4t.2024"
SMTP_SERVER = "mail.infotec.mx"
SMTP_PORT = 587

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        print("Conexión SMTP exitosa.")
except Exception as e:
    print(f"Error al conectarse al servidor SMTP: {e}")
