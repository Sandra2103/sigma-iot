from dash import html
import dash_bootstrap_components as dbc

def home_layout(logged_in=False, username=None):
    """
    Layout dinámico para Home según el estado de autenticación.
    """
    if not logged_in:
        # Layout cuando el usuario no está autenticado
        return html.Div(
            [
                html.H1("Bienvenido a Sigma IoT", className="text-center mt-5"),
                html.P(
                    "Por favor, haz clic en el botón para iniciar sesión.",
                    className="text-center",
                ),
                html.Div(
                    dbc.Button("Iniciar Sesión", href="/login", className="login"),
                    className="text-center",
                ),
            ]
        )
    else:
        # Layout cuando el usuario está autenticado
        return html.Div(
            [
                html.H1(f"Hola, {username}!", className="text-center mt-5"),
                html.P("Has iniciado sesión correctamente.", className="text-center"),
            ]
        )
