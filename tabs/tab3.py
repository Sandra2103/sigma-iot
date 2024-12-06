
########## /home/sandramartinez/Escritorio/sigma_nuevo/tabs/tab3.py
import datetime
from database.db_connection import db_connection
from components.panel_time.panel_time import get_zones, get_monthly_average_data, get_data
from dash import html, dcc, Input, Output, callback, State
from dash.exceptions import PreventUpdate

from app_instance import server
from flask import send_file
import os


import xml.etree.ElementTree as ET
from dash import dash_table
import pandas as pd
from weasyprint import HTML
import tempfile



# Almacena el estado actual de las selecciones de los dropdown
current_zone_value = 'all'
current_rack_value = 'all'

@callback( # selecionar la zona 
    Output('zone-dropdown3', 'options'),
    [Input('interval-component3', 'n_intervals')]
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
    [Output('rack-dropdown3', 'options'),
     Output('rack-dropdown3', 'value')],
    [Input('zone-dropdown3', 'value')],
    [State('rack-dropdown3', 'value')]
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
    Output('zone-dropdown3', 'value'),
    [Input('interval-component3', 'n_intervals')],
    [State('zone-dropdown3', 'value')]
)
def set_zone_value(n, current_value):
    global current_zone_value
    if current_value is None:
        current_zone_value = 'all'  # Establecer 'Todas las zonas' como predeterminado la primera vez
        return 'all'
    return current_value


def generate_csv_report(combined_df):
    # Ruta completa del archivo CSV
    csv_path = os.path.join(ROOT_DIR, "report.csv")
    print(f"Generando archivo CSV en: {csv_path}")

    # Guardar el dataframe como archivo CSV
    try:
        combined_df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"Archivo CSV generado correctamente en: {csv_path}")
    except Exception as e:
        print(f"Error al generar el archivo CSV: {e}")



def generate_pdf_report(combined_df):
    # Ruta completa del archivo
    pdf_path = os.path.join(ROOT_DIR, "report.pdf")

    styles = """
    <style>
    table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 20px;
    }
    th, td {
        border: 1px solid black;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2;
    }
    .header {
        display: flex;
        margin-bottom: 20px;
        flex-direction: column;
    }
    #header-logo {
        text-align: center;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """

    # Convertir el dataframe a HTML y agregar estilos y encabezado
    table_html = combined_df.to_html(index=False)
    html_content = f"{styles}<div class='header'><div id='header-logo'>REPORTE GENERADO POR Sigma-IoT</div></div>{table_html}"

    # Utilizar WeasyPrint para generar el PDF
    try:
        HTML(string=html_content).write_pdf(pdf_path)
        print(f"PDF generado correctamente en {pdf_path}")
    except Exception as e:
        print(f"Error al generar el PDF: {e}")




def generate_xml_report(combined_df):
    # Ruta completa del archivo XML
    xml_path = os.path.join(ROOT_DIR, "report.xml")
    print(f"Generando archivo XML en: {xml_path}")

    # Crear el elemento raíz del XML
    root = ET.Element("data")

    # Iterar sobre las filas del dataframe y agregarlas como elementos al XML
    for index, row in combined_df.iterrows():
        data_element = ET.SubElement(root, "row")
        for col_name, col_value in row.items():
            ET.SubElement(data_element, col_name).text = str(col_value)

    # Crear el árbol XML y guardarlo en el archivo
    try:
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"Archivo XML generado correctamente en: {xml_path}")
    except Exception as e:
        print(f"Error al generar el archivo XML: {e}")

     # Actualizar el estado a True después de generar el XML
# Función para generar la ruta completa del archivo
def get_file_path(filename):
    return os.path.join(ROOT_DIR, filename)
# Callbacks para manejar las descargas de archivos
# Callbacks para manejar las descargas de archivos
@callback(
    Output('link-csv', 'href'),
    [Input('btn-csv', 'n_clicks')]
)
def download_csv(n_clicks):
    if n_clicks > 0:
        return '/download/report.csv'
@callback(
    Output('link-pdf', 'href'),
    [Input('btn-pdf', 'n_clicks')]
)
def download_pdf(n_clicks):
    if n_clicks > 0:
        return '/download/report.pdf'

@callback(
    Output('link-xml', 'href'),
    [Input('btn-xml', 'n_clicks')]
)
def download_xml(n_clicks):
    if n_clicks > 0:
        return '/download/report.xml'

# Rutas para manejar las descargas de archivos
@server.route('/download/<filename>')
def serve_static(filename):
    filepath = get_file_path(filename)
    return send_file(filepath, as_attachment=True)


@callback(
    Output('temperature-humidity-dataframes', 'children'),
    [Input('interval-component3', 'n_intervals')],
    [State('date-picker-range3', 'start_date'),
     State('date-picker-range3', 'end_date'),
     State('zone-dropdown3', 'value'),
     State('rack-dropdown3', 'value')]
)
def update_combined_dataframes(n, start_date, end_date, selected_zone, selected_rack):
    if not start_date or not end_date:
        raise PreventUpdate

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

    dataframes = []

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

                    df = pd.DataFrame({
                        'Zona': [zone] * len(x_data),
                        'Rack': [rack_id] * len(x_data),
                        'Tiempo': x_data,
                        'Temperatura': temperature_data,
                        'Humedad': humidity_data
                    })
                    dataframes.append(df)
        else:
            data = get_data(start_datetime, end_datetime, selected_zone_id, selected_rack, "custom")

            for rack_id, temperature_data in data['temperature'].items():
                if selected_zone_id == 0:
                    continue
                humidity_data = data['humidity'].get(rack_id, [])
                x_data = data['time']

                df = pd.DataFrame({
                    'Zona': [zone] * len(x_data),
                    'Rack': [rack_id] * len(x_data),
                    'Tiempo': x_data,
                    'Temperatura': temperature_data,
                    'Humedad': humidity_data
                })
                dataframes.append(df)

    # Concatenate all dataframes into a single dataframe
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Generate PDF and XML reports
    generate_pdf_report(combined_df)
    generate_xml_report(combined_df)
    generate_csv_report(combined_df)

    return html.Div([
        html.Div(
            style={'text-align': 'center'},
            children=[html.H5("Vista previa", style={'font-size': '25px'})]
        ),
        dash_table.DataTable(
            id='temperature-humidity-data',
            columns=[{'name': i, 'id': i} for i in combined_df.columns],
            data=combined_df.to_dict('records'),
            export_headers='display',
            style_table={'backgroundColor': '#34495E'},
            style_cell={'color': '#34495E'},
        )
    ])



# Define la ruta base donde se encuentran los archivos


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def tab3_layout():
    return  html.Div( 
        [
            html.Div(
                id="main-report",
                className="contenedor",
                children=[
                    html.Div(
                        id="selector-report",
                        className="selector",
                        children=[
                            html.H3("Generación de reportes:", style={'margin': '20px','padding':'10px'}),
                            dcc.DatePickerRange(
                                id='date-picker-range3',
                                start_date=datetime.date.today().isoformat(),  # Fecha inicial predeterminada
                                end_date=datetime.date.today().isoformat(),    # Fecha final predeterminada
                                start_date_placeholder_text="Fecha inicio",
                                end_date_placeholder_text="Fecha fin",
                                calendar_orientation='horizontal',
                                display_format='YYYY-MM-DD',
                                style={'marginBottom': '10px'}
                            ),
                            
                            dcc.Dropdown(
                                id='zone-dropdown3',
                                className="dropdown-selector",
                                options=[{'label': zone, 'value': zone} for zone in get_zones()],
                                placeholder='Select Zone'
                            ),
                            dcc.Dropdown(
                                id='rack-dropdown3',
                                placeholder='Select Rack',
                                className="dropdown-selector",
                            ),
                            html.Div([
                                html.H3("Descarga de archivos"),
                                html.Div([
                                html.A(html.Button("Reporte '.pdf'",id="btn-pdf", n_clicks=0), id="link-pdf", href=""),
                                ],id="btn-pdfe",className="buttonBox"), 
                                html.Div([
                                html.A(html.Button("Reporte '.xml'",id="btn-xml", n_clicks=0), id="link-xml", href=""),
                                ],id="btn-xmle",className="buttonBox"),
                                html.Div([
                                html.A(html.Button("Reporte '.csv'", id="btn-csv", n_clicks=0), id="link-csv", href="")
                                ],id="btn-csve",className="buttonBox"),
                            ],id="download-links-div"),  
                        ]
                    ),
                    html.Div(
                        id='temperature-humidity-dataframes',
                    ),
                ]
            ),
            dcc.Interval(
                id='interval-component3',
                interval=2 * 4000,
                n_intervals=0
            )
        ]),
