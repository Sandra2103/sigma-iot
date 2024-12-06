# Configuraciones globales
import dash
from flask import Flask
from dash_bootstrap_components import themes




# Configuración de Flask y Dash
server = Flask(__name__)
server.secret_key = "clave_secreta"  # Clave secreta para sesiones

app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[themes.BOOTSTRAP]
)
