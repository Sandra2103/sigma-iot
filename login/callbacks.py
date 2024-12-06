from dash import Input, Output, State, ctx
from flask import session

# Credenciales de usuarios
USERS = {
    "admin": "admin",  # Contraseña en texto plano para pruebas
    "user": "user",
}

def register_login_callbacks(app):
    @app.callback(
        [
            Output("url", "pathname"),          # Redirige al usuario al Home o mantiene en Login
            Output("login-message", "children"), # Muestra mensaje de error en caso de fallo
            Output("username", "value"),       # Limpia el campo de usuario si falla
            Output("password", "value"),       # Limpia el campo de contraseña si falla
        ],
        Input("login-button", "n_clicks"),      # Botón de inicio de sesión
        [State("username", "value"), State("password", "value")],  # Inputs
        prevent_initial_call=True,  # No llamar el callback al cargar la página
    )
    def authenticate(n_clicks, username, password):
        if n_clicks:
            if username in USERS and password == USERS[username]:
                session["user"] = username  # Guardar el usuario en sesión
                return "/home", "", "", ""  # Redirigir al Home sin mensajes de error
            else:
                # Mostrar mensaje de error y limpiar inputs
                return (
                    "/login", 
                    "⚠️ Usuario o contraseña incorrectos. Intente nuevamente.", 
                    "",  # Limpiar campo de usuario
                    "",  # Limpiar campo de contraseña
                )

        # Si no hay clics, mantener en login
        return "/login", "", "", ""
