from dash import html

def logout_layout():
    return html.Div(
        [
            html.H1("Has cerrado sesión", className="text-center mt-5"),
            html.A("Ir al login", href="/login", className="d-block text-center mt-3"),
        ]
    )
