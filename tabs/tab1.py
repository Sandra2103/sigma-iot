import datetime
from database.db_connection import db_connection
import calendar
from dateutil.relativedelta import relativedelta
from matplotlib.dates import relativedelta
from receiver.receiver import Receiver
from dash import html, dcc, Input, Output, callback, State
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from components.panel_time.panel_time import get_zones, get_monthly_average_data, get_data

from app_instance import app


TEMPMAX = 1000.0
TEMPMIN = 10.0

VERDE = 30
AMARILLO = 45
ROJO = 46 
TAMANO_VERDE = 15
TAMANO_AMARILLO = 20 
TAMANO_ROJO = 25


umbrales_por_zona = {
    'POD A': (VERDE, AMARILLO, ROJO),
    'POD B': (VERDE, AMARILLO, ROJO),
    'POD C': (VERDE, AMARILLO, ROJO),
    'TELCO': (VERDE, AMARILLO, ROJO),
    'CARRIERS': (VERDE, AMARILLO, ROJO)
}

coordenadas = {
   
    ('POD A', 2): (575, 680),
    ('POD A', 3): (530, 680),
    ('POD A', 4): (490, 680),

    ('POD B', 1): (425, 680),
    ('POD B', 2): (385, 680),
    ('POD B', 3): (355, 680),
    ('POD B', 4): (320, 680),

    ('POD C', 1): (415, 550),
    ('POD C', 2): (330, 550),
    ('POD C', 3): (380, 550),
    ('POD C', 4): (305, 550),

    ('TELCO', 1): (420, 320),
    ('TELCO', 2): (380, 320),
    ('TELCO', 3): (350, 320),
    ('TELCO', 4): (320, 320),

    ('CARRIERS', 1): (175, 320),
    ('CARRIERS', 2): (150, 320),
    ('CARRIERS', 3): (125, 320),
    ('CARRIERS', 4): (75, 320),

    
}

####################### Para gráficas principales ########################
def create_combined_figure(x_data, temperature_data, humidity_data, rack_id):
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.2,
                        subplot_titles=(f"Rack {rack_id} - Temperatura (°C)", f"Rack {rack_id} - Humedad (%)"))
    fig['layout']['margin'] = {'l': 200, 'r': 200, 'b': 30, 't': 60}
    fig['layout']['legend'] = {'x': 1.1, 'y': 1.1, 'xanchor': 'left', 'yanchor': 'top'}
    fig.append_trace({'x': x_data, 'y': temperature_data, 'mode': 'lines+markers', 'type': 'scatter',
                      'name': f"Rack {rack_id} - Temp (°C)."}, 1, 1)
    fig.append_trace({'x': x_data, 'y': humidity_data, 'mode': 'lines+markers', 'type': 'scatter',
                      'name': f"Rack {rack_id} - Hum (%)."}, 2, 1)

    return fig

####################################CALLBACK PARA GRÁFICAS PRINCIPALES ##################################################################
# Almacena el estado actual de las selecciones de los dropdown
current_zone_value = 'all'
current_rack_value = 'all'

@callback( # selecionar la zona 
    Output('zone-dropdown', 'options'),
    [Input('interval-component', 'n_intervals')]
)
def update_zone_options(n):
    try:
        with db_connection() as conn:
            with conn.cursor() as db_cursor:
                db_cursor.execute("SELECT * FROM zonas")
                zones = db_cursor.fetchall()

                zone_options = [{'label': 'Todas las zonas', 'value': 'all','title': f'Selecciona la zona deseada.'}] + [{'label': zone[1], 'value': zone[1],'title': f'Selecciona la zona deseada.'} for zone in zones]
                return zone_options

    except Exception as e:
        print(f"Error getting zones from the database: {str(e)}")
        return [{'label': 'Todas las zonas', 'value': 'all','title': f'Selecciona la zona deseada.'}]  # Opción predeterminada en caso de error


@callback( #selecciona el raack 
    [Output('rack-dropdown', 'options'),
     Output('rack-dropdown', 'value')],
    [Input('zone-dropdown', 'value')],
    [State('rack-dropdown', 'value')]
)
def update_rack_options_and_value(selected_zone, current_value):
    if selected_zone is None:
        return [], None
    try:
        with db_connection() as conn:
            with conn.cursor() as db_cursor:
                db_cursor.execute("SELECT nombre FROM racks WHERE zona_id IN (SELECT idZona FROM zonas WHERE nombre = %s)",
                                  (selected_zone,))
                racks = db_cursor.fetchall()

                rack_options = [{'label': 'Todos los racks', 'value': 'all','title': f'Selecciona el rack deseado.'}] + [{'label': rack[0], 'value': rack[0],'title': f'Selecciona el rack deseado.'} for rack in racks]
                
                # Mantener el valor actual del dropdown si está definido
                if current_value:
                    return rack_options, current_value
                
                # Definir el valor predeterminado como 'all' solo si no hay un valor actual
                return rack_options, 'all'

    except Exception as e:
        print(f"Error getting racks from the database: {str(e)}")
        return [], None



# Mantén la selección actual del dropdown 'zone-dropdown'
@callback(
    Output('zone-dropdown', 'value'),
    [Input('interval-component', 'n_intervals')],
    [State('zone-dropdown', 'value')]
)
def set_zone_value(n, current_value):
    global current_zone_value
    if current_value is None:
        current_zone_value = 'all'  # Establecer 'Todas las zonas' como predeterminado la primera vez
        return 'all'
    return current_value



@callback(
    Output('temperature-humidity-graphs', 'children'),
    [Input('interval-component', 'n_intervals')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('zone-dropdown', 'value'),
     State('rack-dropdown', 'value')]
)
def update_combined_graphs(n, start_date, end_date, selected_zone, selected_rack):
    
    # Usar la fecha actual si no hay selección
    today = datetime.date.today()
    start_date = start_date or today.isoformat()
    end_date = end_date or today.isoformat()

    # Convertir las fechas seleccionadas a objetos datetime
    try:
        start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1, seconds=-1)
    except ValueError as e:
        return html.Div(f"Error en las fechas seleccionadas: {str(e)}", style={'color': 'red'})

    # El resto de la lógica sigue igual, usando start_datetime y end_datetime
    selected_zones = [selected_zone] if selected_zone != 'all' else get_zones()
    graph_children = []

    for zone in selected_zones:
        try:
            with db_connection() as conn:
                with conn.cursor() as db_cursor:
                    db_cursor.execute("SELECT idZona FROM zonas WHERE nombre = %s", (zone,))
                    selected_zone_id = db_cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting zone ID from the database: {str(e)}")
            return []

        if selected_rack == 'all':
            try:
                with db_connection() as conn:
                    with conn.cursor() as db_cursor:
                        db_cursor.execute("SELECT nombre FROM racks WHERE zona_id = %s", (selected_zone_id,))
                        all_racks = db_cursor.fetchall()
                        selected_racks = [rack[0] for rack in all_racks]
            except Exception as e:
                print(f"Error getting all racks from the database: {str(e)}")
                return []

            for rack_id in selected_racks:
                data = get_data(start_datetime, end_datetime, selected_zone_id, rack_id, "custom")

                for rack_id, temperature_data in data['temperature'].items():
                    humidity_data = data['humidity'].get(rack_id, [])
                    x_data = data['time']

                    graph = create_combined_figure(x_data, temperature_data, humidity_data, rack_id)

                    graph_children.append(
                        html.Div([
                            html.H3(f"Zona: {zone}, Rack {rack_id}"),
                            dcc.Graph(figure=graph),
                        ])
                    )
        else:
            data = get_data(start_datetime, end_datetime, selected_zone_id, selected_rack, "custom")

            for rack_id, temperature_data in data['temperature'].items():
                humidity_data = data['humidity'].get(rack_id, [])
                x_data = data['time']

                graph = create_combined_figure(x_data, temperature_data, humidity_data, rack_id)

                graph_children.append(
                    html.Div([
                        html.H3(f"Zona: {zone}, Rack {rack_id}"),
                        dcc.Graph(figure=graph),
                    ])
                )

    return graph_children

def tab1_layout():
    return html.Div(
        [
            
            html.Div(
                id="main-container",
                className="contenedor",
                children=[
                    html.Div(
                        id="sidebar",
                        className="selector",
                        children=[
                            html.H3("Período a mostrar:", style={'marginBottom': '10px'}),
                            dcc.DatePickerRange(
                                id='date-picker-range',
                                start_date=datetime.date.today().isoformat(),  # Fecha de inicio predeterminada
                                end_date=datetime.date.today().isoformat(),    # Fecha de fin predeterminada
                                start_date_placeholder_text="Fecha inicio",
                                end_date_placeholder_text="Fecha fin",
                                calendar_orientation='horizontal',
                                display_format='YYYY-MM-DD',
                                style={'marginBottom': '10px'}
                            ),
                            dcc.Dropdown(
                                id='zone-dropdown',
                                className="dropdown-selector",
                                options=[{'label': zone, 'value': zone} for zone in get_zones()],
                                placeholder='Select Zone'
                            ),
                            dcc.Dropdown(
                                id='rack-dropdown',
                                className="dropdown-selector",
                                placeholder='Select Rack',
                            ),
                            html.H3("Temperatura Actual:"),
                            #html.Div(id='last-temp-hum-{rack_id}3', className='last-temp-hum'),
                            html.Div(id='led-displays-container'),
                        ]
                    ),
                    #dcc.Interval(
                    #    id='interval-componentled3',
                    #    interval=3000,
                    #    n_intervals=0
                    #),
                    html.Div(
                        id="line-charts",
                        
                        children=[
                            #html.Div(id='last-temp-hum-{rack_id}', className='last-temp-hum'),
                            html.Div(id='temperature-humidity-graphs'),
                        ]
                    ),
                ]
            ),
            html.Div(
                id="main-container-centerdata",
                className="contenedor",
                title="En la pestaña de Configuraciones puede modificar esta vista.",
                children=[
                    html.Div(
                        id="center-data-titulo",
                        children=[
                            html.H3("CENTRO DE DATOS SEDE CDMX.", id="titulo-centrodata"),
                        ]
                    ),
                    html.Div(
                        id="center-data",
                        className="small-div",
                        children=[
                           #### QUIERO QUE AQUI SE VEA EL CENTRO DE DATOS
                            dcc.Graph(id='temperature-map')  # Agregar aquí el mapa
                        ]
                    ),
                ]
            ),
            dcc.Interval(
                id='interval-component',
                interval=2 * 4000,
                n_intervals=0
            )
        ]
    )


from dash_daq import LEDDisplay


@callback(
    Output('led-displays-container', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_led_displays(n):
    led_displays = []  # Lista para almacenar todos los LEDDisplays
    exceeding_led_displays = []  # Lista para almacenar solo los LEDDisplays que exceden el umbral

    try:
        with db_connection() as conn:
            with conn.cursor() as db_cursor:
                all_zones = get_zones()
                for zone in all_zones:
                    # Obtén la ID de la zona actual
                    db_cursor.execute("SELECT idZona FROM zonas WHERE nombre = %s", (zone,))
                    result = db_cursor.fetchone()
                    if result is None:
                        print(f"No se encontró la zona: {zone}")
                        continue
                    selected_zone_id = result[0]

                    # Obtén todos los racks de la zona
                    db_cursor.execute("SELECT nombre FROM racks WHERE zona_id = %s", (selected_zone_id,))
                    all_racks = db_cursor.fetchall()
                    if not all_racks:
                        print(f"No se encontraron racks para la zona ID: {selected_zone_id}")
                        continue

                    selected_racks = [rack[0] for rack in all_racks]

                    for rack_id in selected_racks:
                        data = get_datageneral(selected_zone_id, rack_id)

                        if data is None:
                            print(f"No se obtuvieron datos para la zona ID: {selected_zone_id} y el rack ID: {rack_id}")
                            continue

                        temperature = data.get('temperature')
                        if temperature is not None:
                            # Verifica si la temperatura supera o no el umbral TEMPMAX
                            if temperature < TEMPMAX:
                                color = "blue"
                            else:
                                color = "red"

                            # Crea el LEDDisplay
                            led_display = LEDDisplay(
                                id=f"led-display-{zone}-{rack_id}",
                                value=f"{temperature:.2f}",
                                color=color
                            )

                            # Estructura de la visualización
                            display = html.Div([
                                html.H2(
                                    f"Zona: {zone}  Rack: {rack_id}",
                                    style={
                                        'fontFamily': 'Montserrat',
                                        'fontSize': '20px',
                                        'textAlign': 'center',
                                        'fontWeight': '700'
                                    }
                                ),
                                html.Div([
                                    led_display,
                                    html.Span(
                                        " °C",
                                        style={
                                            'fontFamily': 'Montserrat',
                                            'fontSize': '30px',
                                            'fontWeight': '400',
                                            'marginLeft': '5px',
                                            'color': color,  # Aquí cambia el color de "°C" según la temperatura
                                            'marginTop': '-40px',
                                        }
                                    )
                                ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
                            ])

                            # Añade el display a la lista general
                            led_displays.append(display)

                            # Si la temperatura excede el umbral, añade el display a la lista de "exceeding"
                            if temperature >= TEMPMAX:
                                exceeding_led_displays.append(display)

    except Exception as e:
        print(f"Error: {str(e)}")
        return []

    # Si hay LEDDisplays que exceden el umbral, rota solo esos
    if exceeding_led_displays:
        return exceeding_led_displays[n % len(exceeding_led_displays)]
    # Si no hay LEDDisplays que excedan el umbral, rota todos
    elif led_displays:
        return led_displays[n % len(led_displays)]
    else:
        print("No hay LEDDisplays para mostrar.")
        return []
    


def get_datageneral(selected_zone_id, selected_rack):
    data = {
        'temperature': None,
        'humidity': None
    }
    try:
        with db_connection() as conn:
            with conn.cursor() as db_cursor:
                select_query = """
                SELECT temperatura, humedad
                FROM datos
                WHERE zona_id = %s AND rack_id = %s
                ORDER BY fecha DESC, hora DESC
                LIMIT 1
                """
                db_cursor.execute(select_query, (selected_zone_id, selected_rack))
                row = db_cursor.fetchone()

                if row:
                    temperatura, humedad = row
                    data['temperature'] = float(temperatura)
                    data['humidity'] = float(humedad)

    except Exception as e:
        print(f"Error al obtener datos de la base de datos: {str(e)}")
    return data






@callback(
    Output('temperature-map', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('coordinate-store', 'data')],  # Usar el Store como input
    [State('zone-dropdown', 'value'),
     State('rack-dropdown', 'value')]
)
def update_map(n, stored_coordinates, selected_zone, selected_rack):
    try:
        # Actualizar las coordenadas globales desde el Store
        if stored_coordinates:
            global coordenadas
            coordenadas.update(stored_coordinates)

        # Obtener datos de la base de datos
        with db_connection() as conn:
            with conn.cursor() as db_cursor:
                # Consultar datos de la base de datos ordenados por zona y rack
                if selected_zone == 'all':
                    if selected_rack == 'all':
                        db_cursor.execute("""
                            SELECT z.idZona, z.nombre, r.idRack, d.fecha as max_fecha, d.hora as max_hora, 
                                   d.temperatura as max_temp, d.humedad as max_hum
                            FROM datos d
                            JOIN racks r ON d.rack_id = r.idRack
                            JOIN zonas z ON d.zona_id = z.idZona
                            ORDER BY z.idZona ASC, r.idRack ASC  -- Ordenar por ID de Zona y Rack
                        """)
                    else:
                        db_cursor.execute("""
                            SELECT z.idZona, z.nombre, r.idRack, d.fecha as max_fecha, d.hora as max_hora, 
                                   d.temperatura as max_temp, d.humedad as max_hum
                            FROM datos d
                            JOIN racks r ON d.rack_id = r.idRack
                            JOIN zonas z ON d.zona_id = z.idZona
                            WHERE r.nombre = %s
                            ORDER BY z.idZona ASC, r.idRack ASC
                        """, (selected_rack,))
                else:
                    if selected_rack == 'all':
                        db_cursor.execute("""
                            SELECT z.idZona, z.nombre, r.idRack, 
                                   d.fecha as max_fecha, d.hora as max_hora, 
                                   d.temperatura as max_temp, d.humedad as max_hum
                            FROM datos d
                            JOIN racks r ON d.rack_id = r.idRack
                            JOIN zonas z ON d.zona_id = z.idZona
                            JOIN (SELECT d1.rack_id, MAX(d1.fecha || ' ' || d1.hora) as max_fecha_hora
                                  FROM datos d1
                                  JOIN zonas z1 ON d1.zona_id = z1.idZona
                                  WHERE z1.idZona = %s
                                  GROUP BY d1.rack_id) max_dates
                            ON d.rack_id = max_dates.rack_id 
                            AND (d.fecha || ' ' || d.hora) = max_dates.max_fecha_hora
                            ORDER BY z.idZona ASC, r.idRack ASC
                        """, (selected_zone,))
                    else:
                        db_cursor.execute("""
                            SELECT z.idZona, z.nombre, r.idRack, 
                                   d.fecha as max_fecha, d.hora as max_hora, 
                                   d.temperatura as max_temp, d.humedad as max_hum
                            FROM datos d
                            JOIN racks r ON d.rack_id = r.idRack
                            JOIN zonas z ON d.zona_id = z.idZona
                            JOIN (SELECT d1.rack_id, MAX(d1.fecha || ' ' || d1.hora) as max_fecha_hora
                                  FROM datos d1
                                  JOIN zonas z1 ON d1.zona_id = z1.idZona
                                  WHERE z1.idZona = %s
                                  GROUP BY d1.rack_id) max_dates
                            ON d.rack_id = max_dates.rack_id 
                            AND (d.fecha || ' ' || d.hora) = max_dates.max_fecha_hora
                            WHERE r.nombre = %s
                            ORDER BY z.idZona ASC, r.idRack ASC
                        """, (selected_zone, selected_rack))

                # Obtener resultados de la base de datos
                rack_info = db_cursor.fetchall()

        # Crear un conjunto global de zonas y racks
        combined_racks = {(zone, rack) for zone, rack in coordenadas.keys()}
        for row in rack_info:
            combined_racks.add((row[1], row[2]))  # (zone_name, rack_id)

        # Ordenar globalmente por zona y rack
        ordered_racks = sorted(combined_racks, key=lambda x: (x[0], x[1]))  # Ordenar por zona, luego por rack

        # Crear la figura del mapa
        fig_layout = dict(
            xaxis=dict(range=[0, 800]),
            yaxis=dict(range=[0, 779]),
            images=[
                dict(
                    source='/assets/croquis.png',
                    x=0,
                    y=800,
                    xref='x',
                    yref='y',
                    sizex=1900,
                    sizey=679,
                    opacity=1,
                    layer='below',
                )
            ],
            width=1200,
            height=679,
        )

        fig_data = []
        legend_names = set()

        # Iterar sobre los racks ordenados
        for zone_name, rack_id in ordered_racks:
            # Verificar si hay datos para esta combinación
            rack_data = next((row for row in rack_info if row[1] == zone_name and row[2] == rack_id), None)

            if rack_data:
                # Si hay datos disponibles
                _, _, _, max_fecha, max_hora, max_temp, max_hum = rack_data
                coordenada = coordenadas.get((zone_name, rack_id), (50, 50))  # Coordenada predeterminada si no existe
                x_position, y_position = coordenada

                if float(max_temp) < umbrales_por_zona[zone_name][0]:
                    color = 'green'
                    marker_size = TAMANO_VERDE
                elif umbrales_por_zona[zone_name][0] <= float(max_temp) < umbrales_por_zona[zone_name][1]:
                    color = 'yellow'
                    marker_size = TAMANO_AMARILLO
                else:
                    color = 'red'
                    marker_size = TAMANO_ROJO

                text_label = f"Zona: {zone_name}, Rack: {rack_id}<br>" \
                             f"Fecha: {max_fecha}<br>Hora: {max_hora}<br>" \
                             f"Temperatura: {max_temp:.2f}°C<br>Humedad: {max_hum:.2f}%"
            else:
                # Si no hay datos
                coordenada = coordenadas.get((zone_name, rack_id), (50, 50))  # Coordenada predeterminada
                x_position, y_position = coordenada
                color = 'grey'
                marker_size = TAMANO_VERDE
                text_label = f"Zona: {zone_name}, Rack: {rack_id}<br>No han llegado datos"

            trace_name = f'{zone_name} - Rack {rack_id}'
            show_legend = trace_name not in legend_names
            if show_legend:
                legend_names.add(trace_name)

            # Crear marcador
            fig_data.append(
                go.Scatter(
                    x=[x_position],
                    y=[y_position],
                    mode='markers',
                    marker=dict(size=marker_size, color=color),
                    text=[text_label],
                    name=trace_name,
                    showlegend=show_legend
                )
            )

        return {'data': fig_data, 'layout': fig_layout}

    except Exception as e:
        print(f"Error updating map: {str(e)}")
        return {'data': [], 'layout': {}}

