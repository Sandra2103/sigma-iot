from app_instance import app, server
from dash import dcc, html
from login.callbacks import register_login_callbacks
from routing.callbacks import register_routing_callbacks
from receiver.receiver import Receiver
#from alerting.alert_receiver import AlertReceiver




# Layout principal
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),  # Manejo de rutas
        dcc.Store(id='coordinate-store'),  # Asegura que el Store esté disponible globalmente
        html.Div(id="page-content"),           # Contenido dinámico de la página
    ]
)

# Registrar callbacks
register_login_callbacks(app)         # Callbacks relacionados con autenticación
register_routing_callbacks(app)       # Callbacks para enrutamiento dinámico

if __name__ == "__main__":
    # Iniciar el receptor en un hilo separado
    thread = Receiver()
    thread.start()

    # Receiver para alertas
    #alert_receiver = AlertReceiver()
    #alert_receiver.start()

    

    # Ejecutar la aplicación
    app.run_server(debug=True)
