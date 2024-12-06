from dash import html, dcc


def login_layout():
    return html.Div(
        [
            html.H1("Iniciar Sesión", className="text-center mt-5"),
            html.Div(
                [
                    html.Div(
                        html.Img(
                            src="/assets/logo-sigma.png",  # Ruta del logo
                            style={"maxWidth": "100%", "maxHeight": "80%"},
                        ),
                        className="logo-container",
                    ),
                    html.Div(
                        [
                            dcc.Input(
                                id="username",
                                type="text",
                                placeholder="Usuario",
                                className="form-control mb-3",
                            ),
                            dcc.Input(
                                id="password",
                                type="password",
                                placeholder="Contraseña",
                                className="form-control mb-3",
                            ),
                            html.Button(
                                "Ingresar",
                                id="login-button",
                                className="login",
                            ),
                            html.Div(
                                id="login-message",
                                className="text-danger mt-3",
                            ),
                        ],
                        className="container mt-4 selector",
                    ),
                ],
                className="container",
                id="loginid"
            ),
        ]
    )
