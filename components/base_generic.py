from dash import html
from components.navbar import navbar

def base_generic(content, logged_in=False):
    """
    Plantilla base genérica que incluye el navbar y el contenido dinámico.
    """
    return html.Div(
        [
            navbar(logged_in=logged_in),  # Siempre muestra el navbar adecuado
            html.Div(content, className="container mt-4"),  # Contenido dinámico debajo del navbar
        ]
    )
