import datetime
from database.db_connection import db_connection
from components.panel_time.panel_time import get_zones, get_monthly_average_data, get_data
from dash import html, dcc, Input, Output, callback, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
####################### Para gráficas Monitoreo ########################
# Define la función para crear el gráfico de pastel combinado
def create_combined_pie_figure(temperature, humidity):
    temperature_data = [temperature] if isinstance(temperature, (int, float)) else temperature
    humidity_data = [humidity] if isinstance(humidity, (int, float)) else humidity

    temperature_average = sum(temperature_data) / len(temperature_data) if temperature_data else 0
    humidity_average = sum(humidity_data) / len(humidity_data) if humidity_data else 0

    labels = ['Temperatura (°C)', 'Humedad (%)']
    values = [temperature_average, humidity_average]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_traces(hole=0.4, hoverinfo="label+percent", textinfo="value", textfont_size=20)
    fig.update_layout(title_text="Temperatura(°C) y Humedad(%) Promedio")
    
    return fig

def create_combined_bar_figures(x_data, temperature_data, humidity_data, rack_id):
    # Crea el gráfico de barras para la temperatura
    temperature_trace = go.Bar(
        x=x_data,
        y=temperature_data,
        name='Temperatura (°C)',
        #marker=dict(color='rgb(99, 110, 250)')
        marker=dict(color='rgb(99, 110, 250)')  # Líneas más gruesas
    )

    # Crea el gráfico de barras para la humedad
    humidity_trace = go.Bar(
        x=x_data,
        y=humidity_data,
        name='Humedad (%)',
        marker=dict(color='rgb(239, 85, 59)')
    )

    # Crea una figura para la temperatura
    temperature_figure = go.Figure(data=[temperature_trace])
    temperature_figure.update_layout(
        xaxis_title='Fecha y Hora',
        yaxis_title='Temperatura (°C)',
        barmode='group',
    )

    # Crea una figura para la humedad
    humidity_figure = go.Figure(data=[humidity_trace])
    humidity_figure.update_layout(
        xaxis_title='Fecha y Hora',
        yaxis_title='Humedad (%)',
        barmode='group',
    )

    return temperature_figure, humidity_figure

def create_empty_figure():
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {'l': 200, 'r': 200, 'b': 30, 't': 10}
    fig['layout']['legend'] = {'x': 0, 'y': 1.2, 'xanchor': 'left'}
    fig.append_trace({'x': [], 'y': [], 'mode': 'lines+markers', 'type': 'scatter'}, 1, 1)
    fig.append_trace({'x': [], 'y': [], 'mode': 'lines+markers', 'type': 'scatter'}, 2, 1)
    return fig



####################################CALLBACK PARA GRÁFICAS PRINCIPALES ##################################################################
# Almacena el estado actual de las selecciones de los dropdown
current_zone_value = 'all'
current_rack_value = 'all'

@callback( # selecionar la zona 
    Output('zone-dropdown2', 'options'),
    [Input('interval-component2', 'n_intervals')]
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
    [Output('rack-dropdown2', 'options'),
     Output('rack-dropdown2', 'value')],
    [Input('zone-dropdown2', 'value')],
    [State('rack-dropdown2', 'value')]
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



# Mantén la selección actual del dropdown 'zone-dropdown2'
@callback(
    Output('zone-dropdown2', 'value'),
    [Input('interval-component2', 'n_intervals')],
    [State('zone-dropdown2', 'value')]
)
def set_zone_value(n, current_value):
    global current_zone_value
    if current_value is None:
        current_zone_value = 'all'  # Establecer 'Todas las zonas' como predeterminado la primera vez
        return 'all'
    return current_value


@callback(
    Output('temperature-humidity-graphs2', 'children'),
    [Input('interval-component2', 'n_intervals')],
    [State('date-picker-range2', 'start_date'),
     State('date-picker-range2', 'end_date'),
     State('zone-dropdown2', 'value'),
     State('rack-dropdown2', 'value')]
)
def update_combined_graphs(n, start_date, end_date, selected_zone, selected_rack):

    # Usar la fecha actual si no hay selección
    today = datetime.date.today()
    start_date = start_date or today.isoformat()
    end_date = end_date or today.isoformat()
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

    graph_children = []

    # Obtén la lista de zonas seleccionadas
    selected_zones = [selected_zone] if selected_zone != 'all' else get_zones()

    for zone in selected_zones:
        # Obtén la ID de la zona actual
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
                    if selected_zone_id == 0:
                        continue
                    humidity_data = data['humidity'].get(rack_id, [])
                    x_data = data['time']

                    # Inicializar variables para evitar UnboundLocalError
                    last_temperature = None
                    last_humidity = None

                    # Obtener los valores de última temperatura y humedad si están disponibles
                    if temperature_data:
                        last_temperature = temperature_data[-1]
                    if humidity_data:
                        last_humidity = humidity_data[-1]

                    # Genera las gráficas
                    temperature_figure, humidity_figure = create_combined_bar_figures(x_data, temperature_data, humidity_data, rack_id)
                    pie_figure = create_combined_pie_figure(last_temperature, last_humidity)

                    # Añade las gráficas al layout
                    graph_children.append(
                        html.Div([
                            html.H3(f"Zona: {zone}, Rack {rack_id}"),
                            dcc.Graph(figure=temperature_figure),
                            dcc.Graph(figure=humidity_figure),
                            dcc.Graph(figure=pie_figure)
                        ])
                    )
        else:
            # Para un rack específico
            data = get_data(start_datetime, end_datetime, selected_zone_id, selected_rack, "custom")

            for rack_id, temperature_data in data['temperature'].items():
                if selected_zone_id == 0:
                    continue
                humidity_data = data['humidity'].get(rack_id, [])
                x_data = data['time']

                # Inicializar variables para evitar UnboundLocalError
                last_temperature = None
                last_humidity = None

                # Obtener los valores de última temperatura y humedad si están disponibles
                if temperature_data:
                    last_temperature = temperature_data[-1]
                if humidity_data:
                    last_humidity = humidity_data[-1]

                # Obtén las figuras separadas
                temperature_figure, humidity_figure = create_combined_bar_figures(x_data, temperature_data, humidity_data, rack_id)
                pie_figure = create_combined_pie_figure(last_temperature, last_humidity)

                # Añade ambas figuras al layout
                graph_children.append(
                    html.Div([
                        html.H3(f"Zona: {zone}, Rack {rack_id}"),
                        dcc.Graph(figure=temperature_figure),
                        dcc.Graph(figure=humidity_figure),
                        dcc.Graph(figure=pie_figure)
                    ])
                )

    return graph_children




def tab2_layout():
    return html.Div(
        [
       
            html.Div(
                id="main3",
                className="contenedor",
                children=[
                    html.Div(
                        id="temp",
                        className="selector",
                        children=[
                            html.H3("Temperatura Promedio", ),
                            html.Div(id="specific-temperature",) 
                        ]
                    ),
                    html.Div(
                        id="hum",
                        className="selector",
                        children=[
                            html.H3("Humedad Promedio", ),
                            html.Div(id="specific-humidity",) 
                        ]
                    ),
                    html.Div(
                        id="racks",
                        className="selector",
                        children=[
                            html.H3("Total de Racks",),
                        ]
                    ),

                ]
            ),
            html.Div(
                id="main2",
                className="contenedor",
                children=[
                    html.Div(
                        id="selector",
                        className="selector",
                        children=[
                            html.H3("Período a mostrar:", style={'marginBottom': '10px'}),
                            dcc.DatePickerRange(
                                id='date-picker-range2',
                                start_date=datetime.date.today().isoformat(),  # Fecha de inicio predeterminada
                                end_date=datetime.date.today().isoformat(),    # Fecha de fin predeterminada
                                start_date_placeholder_text="Fecha inicio",
                                end_date_placeholder_text="Fecha fin",
                                calendar_orientation='horizontal',
                                display_format='YYYY-MM-DD',
                                style={'marginBottom': '10px'}
                            ),
                           
                            dcc.Dropdown(
                                id='zone-dropdown2',
                                className="dropdown-selector",
                                options=[{'label': zone, 'value': zone} for zone in get_zones()],
                                placeholder='Select Zone'
                            ),
                            dcc.Dropdown(
                                id='rack-dropdown2',
                                placeholder='Select Rack',
                                className="dropdown-selector",
                            ),
                           
                            dcc.Interval(#
                                id='interval-temavg',
                                interval=3000,
                                n_intervals=0
                            ),#
                            
                        ]
                    ),
                    html.Div(
                        id="line-charts2",
                        children=[
                            html.Div(id='last-temp-hum-{rack_id}2', className='last-temp-hum'),
                            html.Div(id='temperature-humidity-graphs2'),
                        ]
                    ),
                ]
            ),
            dcc.Interval(
                id='interval-component2',
                interval=2 * 4000,
                n_intervals=0
            )
        
        ]
    )


@callback(
    [Output('specific-temperature', 'children'),
     Output('specific-humidity', 'children'),
     Output('racks', 'children')],
    [Input('interval-temavg', 'n_intervals')],
    [State('date-picker-range2', 'start_date'),
     State('date-picker-range2', 'end_date'),
     State('zone-dropdown2', 'value'),
     State('rack-dropdown2', 'value')]
)
def update_combined_graphs(n, start_date, end_date, selected_zone, selected_rack):
    # Verifica si no se seleccionó ninguna zona
    if selected_zone is None:
        return [], [], []

    # Usar la fecha actual si no hay selección
    today = datetime.date.today()
    start_date = start_date or today.isoformat()
    end_date = end_date or today.isoformat()

    # Convertir fechas a datetime
    try:
        start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1, seconds=-1)
    except ValueError as e:
        print(f"Error al convertir las fechas: {str(e)}")
        return [], [], []

    temperature_output = []
    humidity_output = []
    racks_output = []

    # Obtén la lista de zonas seleccionadas
    selected_zones = [selected_zone] if selected_zone != 'all' else get_zones()

    global global_average_data

    average_data = []

    # Llena la lista average_data con los promedios de temperatura y humedad actualizados
    for zone in selected_zones:
        try:
            with db_connection() as conn:
                with conn.cursor() as db_cursor:
                    db_cursor.execute("SELECT idZona FROM zonas WHERE nombre = %s", (zone,))
                    selected_zone_id = db_cursor.fetchone()[0]

        except Exception as e:
            print(f"Error obteniendo el ID de la zona: {str(e)}")
            return [], [], []

        if selected_rack == 'all':
            try:
                with db_connection() as conn:
                    with conn.cursor() as db_cursor:
                        db_cursor.execute("SELECT nombre FROM racks WHERE zona_id = %s", (selected_zone_id,))
                        all_racks = db_cursor.fetchall()
                        selected_racks = [rack[0] for rack in all_racks]

            except Exception as e:
                print(f"Error obteniendo racks de la zona: {str(e)}")
                return [], [], []

            for rack_id in selected_racks:
                data = get_data(start_datetime, end_datetime, selected_zone_id, rack_id, "custom")

                for rack_id, temperature_data in data['temperature'].items():
                    if selected_zone_id == 0:
                        continue
                    humidity_data = data['humidity'].get(rack_id, [])

                    # Calcula el promedio de temperatura
                    average_temperature = sum(temperature_data) / len(temperature_data) if temperature_data else 0

                    # Calcula el promedio de humedad
                    average_humidity = sum(humidity_data) / len(humidity_data) if humidity_data else 0
                    average_data.append((zone, rack_id, average_temperature, average_humidity))

        else:
            data = get_data(start_datetime, end_datetime, selected_zone_id, selected_rack, "custom")

            for rack_id, temperature_data in data['temperature'].items():
                if selected_zone_id == 0:
                    continue
                humidity_data = data['humidity'].get(rack_id, [])

                # Calcula el promedio de temperatura
                average_temperature = sum(temperature_data) / len(temperature_data) if temperature_data else 0

                # Calcula el promedio de humedad
                average_humidity = sum(humidity_data) / len(humidity_data) if humidity_data else 0
                average_data.append((zone, rack_id, average_temperature, average_humidity))

    # Actualiza la variable global_average_data
    global_average_data = average_data

    # Si global_average_data está vacío, retornar listas vacías
    if not global_average_data:
        return [], [], []

    # Calcula el índice para mostrar el próximo conjunto de promedios
    index = n % len(global_average_data)

    # Devuelve el conjunto de promedios correspondiente al índice actual
    temperature_output = [html.Div([
        html.H2(f"Zona: {global_average_data[index][0]} Rack {global_average_data[index][1]}", style={'fontSize': '20px', 'textAlign': 'center'}),
        html.H5(f"{global_average_data[index][2]:.2f} °C", style={'fontFamily': 'Montserrat', 'fontWeight': 600, 'fontSize': '50px', 'textAlign': 'center'})
    ])]

    humidity_output = [html.Div([
        html.H2(f"Zona: {global_average_data[index][0]} Rack {global_average_data[index][1]}", style={'fontSize': '20px', 'textAlign': 'center'}),
        html.H5(f"{global_average_data[index][3]:.2f} %", style={'fontFamily': 'Montserrat', 'fontWeight': 600, 'fontSize': '50px', 'textAlign': 'center'})
    ])]

    racks_output = [html.Div([
        html.H3("Total de Racks", style={'marginBottom': '10px'}),
        html.H2(f"{global_average_data[index][0]}", style={'fontSize': '20px', 'textAlign': 'center'}),
        html.H5(f"{len([rack[1] for rack in global_average_data if rack[0] == global_average_data[index][0]])}", style={'fontFamily': 'Montserrat', 'fontWeight': 600, 'fontSize': '50px', 'textAlign': 'center'})
    ])]

    return temperature_output, humidity_output, racks_output






