####### /home/sandramartinez/Escritorio/sigma_nuevo/routing/callbacks.py
from dash import Input, Output, html
from flask import session
from login.layout import login_layout
from login.logout_layout import logout_layout
from home.layout import home_layout
from tabs.tab1 import tab1_layout
from tabs.tab2 import tab2_layout
from tabs.tab3 import tab3_layout
#from tabs.tab4 import tab4_layout
from components.base_generic import base_generic
from app_instance import app

def register_routing_callbacks(app):
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
    )
    def display_page(pathname):
        # Verificar si el usuario está autenticado
        is_logged_in = "user" in session

        # Rutas específicas
        if pathname == "/login":
            return base_generic(login_layout(), logged_in=is_logged_in)

        elif pathname == "/logout":
            session.clear()  # Limpiar sesión
            return base_generic(logout_layout(), logged_in=False)

        elif pathname == "/" or pathname == "/home":
            return base_generic(home_layout(logged_in=is_logged_in, username=session.get("user")), logged_in=is_logged_in)

        elif pathname == "/tabs/tab1" and is_logged_in:
            return base_generic(tab1_layout(), logged_in=True)
        elif pathname == "/tabs/tab2" and is_logged_in:
            return base_generic(tab2_layout(), logged_in=True)
        elif pathname == "/tabs/tab3" and is_logged_in:
            return base_generic(tab3_layout(), logged_in=True)
        elif pathname == "/tabs/tab4" and is_logged_in:
            return base_generic(tab4_layout(), logged_in=True)

        # Ruta no encontrada
        return base_generic(html.H1("404: Página no encontrada", className="text-center mt-5"), logged_in=is_logged_in)
