from dash import html
import dash_bootstrap_components as dbc


def navbar(logged_in=False):
    """
    Genera un Navbar dinámico con logotipos y botones bien alineados.
    """
    # Enlaces principales del Navbar
    top_links = [
        dbc.NavItem(dbc.NavLink("Inicio", href="/home")),
    ]

    # Si el usuario está autenticado, añadir el botón de "Cerrar Sesión"
    if logged_in:
        top_links.append(dbc.NavItem(dbc.NavLink("Cerrar Sesión", href="/logout", className="text-danger")))

    # Tabs adicionales visibles solo si el usuario está autenticado
    tabs = None
    if logged_in:
        tabs = dbc.Nav(
            [
                dbc.NavLink("Temperaturas y humedades", href="/tabs/tab1", active="exact", className="tab-style flex-fill"),
                dbc.NavLink("Monitoreo", href="/tabs/tab2", active="exact", className="tab-style flex-fill"),
                dbc.NavLink("Informes", href="/tabs/tab3", active="exact", className="tab-style flex-fill"),
                dbc.NavLink("Configuración", href="/tabs/tab4", active="exact", className="tab-style flex-fill"),
            ],
            pills=True,
            className="mt-2 nav-tabs-style d-flex",
        )

    # Construcción del Navbar completo
    return html.Div(
        [
            dbc.Navbar(
                dbc.Container(
                    [
                        # Logotipos alineados a la izquierda
                        html.Div(
                            [
                                html.Img(src="/assets/infotec.png", height="90px", className="mx-2 logo"),
                                html.Img(src="/assets/sigma.png", height="90px", className="mx-2 logo"),
                                html.Img(src="/assets/conahcyt.png", height="90px", className="mx-2 logo"),
                            ],
                            className="d-flex align-items-center",
                        ),
                        # Botones de navegación alineados a la derecha
                        dbc.Nav(
                            top_links,
                            className="ms-auto d-flex align-items-center",  # Alineación y distribución
                            navbar=True,
                        ),
                    ],
                    fluid=True,  # Asegura que los elementos ocupen todo el ancho
                    className="d-flex justify-content-between",  # Distribuye contenido
                ),
                dark=True,
                sticky="top",
                className="navbar-custom",
            ),
            html.Hr(className="m-0"),  # Línea divisoria
            # Agrega las Tabs si el usuario está autenticado
            html.Div(tabs, className="bg-light") if logged_in else None,
        ],
        className="nav-custom",
    )
