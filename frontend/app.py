"""
Dashboard en tiempo real para visualización de datos del sensor MPU6050
"""
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from datetime import datetime
import psycopg2
import numpy as np
import logging
import os
from dotenv import load_dotenv

# Importar estilos
from frontend.styles import (
    COLORS, MAIN_CONTAINER_STYLE, HEADER_CONTAINER_STYLE, HEADER_TITLE_STYLE,
    HEADER_SUBTITLE_STYLE, TIME_SELECTOR_CONTAINER_STYLE, TIME_SELECTOR_LABEL_STYLE,
    TIME_SELECTOR_DROPDOWN_STYLE, CARD_STYLE, CARD_TITLE_STYLE, LAST_UPDATE_STYLE,
    INDICATORS_CONTAINER_STYLE, ACCEL_SECTION_STYLE, GYRO_SECTION_STYLE,
    INDICATOR_TITLE_ACCEL_STYLE, INDICATOR_TITLE_GYRO_STYLE, INDICATOR_VALUES_CONTAINER_STYLE,
    INDICATOR_ITEM_STYLE, GRAPH_CONTAINER_STYLE, INDICATOR_BOX_STYLE, INDICATOR_LABEL_STYLE,
    get_indicator_value_style, GRAPH_CONFIG, get_graph_layout, ACCEL_LINE_CONFIG,
    GYRO_LINE_CONFIG, ACCEL_FILL_COLOR, GYRO_FILL_COLOR, TIME_RANGE_OPTIONS, UPDATE_INTERVAL
)

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====
# CONFIGURACIÓN TIMESCALE CLOUD
# ====
TIMESCALE_HOST = os.getenv('TIMESCALE_HOST')
TIMESCALE_PORT = int(os.getenv('TIMESCALE_PORT', 5432))
TIMESCALE_DB = os.getenv('TIMESCALE_DB', 'tsdb')
TIMESCALE_USER = os.getenv('TIMESCALE_USER')
TIMESCALE_PASSWORD = os.getenv('TIMESCALE_PASSWORD')

# ====
# FUNCIONES DE BASE DE DATOS
# ====
def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        conn = psycopg2.connect(
            host=TIMESCALE_HOST,
            port=TIMESCALE_PORT,
            database=TIMESCALE_DB,
            user=TIMESCALE_USER,
            password=TIMESCALE_PASSWORD,
            sslmode='require'
        )
        return conn
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        return None

def get_data_by_days(days=1):
    """Obtener datos de los últimos N días"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        ms_range = days * 24 * 60 * 60 * 1000
        
        cursor.execute("""
            SELECT 
                timestamp,
                ax, ay, az,
                gx, gy, gz,
                received_at
            FROM sensor_data
            WHERE timestamp > (
                SELECT MAX(timestamp) - %s 
                FROM sensor_data
            )
            ORDER BY timestamp ASC
        """, (ms_range,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error obteniendo datos: {e}")
        if conn:
            conn.close()
        return []

def get_latest_values():
    """Obtener los últimos valores registrados"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                timestamp,
                ax, ay, az,
                gx, gy, gz,
                received_at
            FROM sensor_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error obteniendo últimos valores: {e}")
        if conn:
            conn.close()
        return None

# ====
# INICIALIZAR DASH APP
# ====
app = dash.Dash(__name__)
app.title = "Monitor MPU6050 - Tiempo Real"

# ====
# LAYOUT DEL DASHBOARD
# ====
app.layout = html.Div([
    # Encabezado
    html.Div([
        html.H1("📊 Monitor de Sensor MPU6050", style=HEADER_TITLE_STYLE),
        html.P("Visualización en tiempo real de acelerómetro y giroscopio", 
               style=HEADER_SUBTITLE_STYLE)
    ], style=HEADER_CONTAINER_STYLE),
    
    # Selector de rango de tiempo
    html.Div([
        html.Label("Rango de tiempo histórico:", style=TIME_SELECTOR_LABEL_STYLE),
        dcc.Dropdown(
            id='time-range-selector',
            options=TIME_RANGE_OPTIONS,
            value=1,
            clearable=False,
            style=TIME_SELECTOR_DROPDOWN_STYLE
        )
    ], style=TIME_SELECTOR_CONTAINER_STYLE),
    
    # Sección de últimos valores
    html.Div([
        html.H3("📍 Últimos Valores Registrados", style=CARD_TITLE_STYLE),
        html.Div(id='last-update-time', style=LAST_UPDATE_STYLE),
        
        # Indicadores numéricos
        html.Div([
            # Acelerómetro
            html.Div([
                html.H4("Acelerómetro (m/s²)", style=INDICATOR_TITLE_ACCEL_STYLE),
                html.Div([
                    html.Div(id='indicator-ax', style=INDICATOR_ITEM_STYLE),
                    html.Div(id='indicator-ay', style=INDICATOR_ITEM_STYLE),
                    html.Div(id='indicator-az', style=INDICATOR_ITEM_STYLE)
                ], style=INDICATOR_VALUES_CONTAINER_STYLE)
            ], style=ACCEL_SECTION_STYLE),
            
            # Giroscopio
            html.Div([
                html.H4("Giroscopio (°/s)", style=INDICATOR_TITLE_GYRO_STYLE),
                html.Div([
                    html.Div(id='indicator-gx', style=INDICATOR_ITEM_STYLE),
                    html.Div(id='indicator-gy', style=INDICATOR_ITEM_STYLE),
                    html.Div(id='indicator-gz', style=INDICATOR_ITEM_STYLE)
                ], style=INDICATOR_VALUES_CONTAINER_STYLE)
            ], style=GYRO_SECTION_STYLE)
        ], style=INDICATORS_CONTAINER_STYLE)
    ], style=CARD_STYLE),
    
    # Gráficos en tiempo real
    html.Div([
        html.H3("📈 Magnitud Absoluta en Tiempo Real", style=CARD_TITLE_STYLE),
        
        # Gráfico de aceleración absoluta
        html.Div([
            dcc.Graph(id='accel-magnitude-graph', config=GRAPH_CONFIG)
        ], style=GRAPH_CONTAINER_STYLE),
        
        # Gráfico de giroscopio absoluto
        html.Div([
            dcc.Graph(id='gyro-magnitude-graph', config=GRAPH_CONFIG)
        ])
    ], style=CARD_STYLE),
    
    # Intervalo de actualización
    dcc.Interval(
        id='interval-component',
        interval=UPDATE_INTERVAL,
        n_intervals=0
    )
], style=MAIN_CONTAINER_STYLE)

# ====
# CALLBACKS
# ====
@app.callback(
    [Output('accel-magnitude-graph', 'figure'),
     Output('gyro-magnitude-graph', 'figure'),
     Output('indicator-ax', 'children'),
     Output('indicator-ay', 'children'),
     Output('indicator-az', 'children'),
     Output('indicator-gx', 'children'),
     Output('indicator-gy', 'children'),
     Output('indicator-gz', 'children'),
     Output('last-update-time', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('time-range-selector', 'value')]
)
def update_dashboard(n, days):
    """Actualizar todos los componentes del dashboard"""
    
    # Obtener datos históricos
    data = get_data_by_days(days)
    
    # Obtener últimos valores
    latest = get_latest_values()
    
    # Preparar datos para gráficos
    if data:
        timestamps = [datetime.fromtimestamp(row[0]/1000) for row in data]
        ax_vals = [row[1] for row in data]
        ay_vals = [row[2] for row in data]
        az_vals = [row[3] for row in data]
        gx_vals = [row[4] for row in data]
        gy_vals = [row[5] for row in data]
        gz_vals = [row[6] for row in data]
        
        # Calcular magnitudes absolutas
        accel_magnitude = [np.sqrt(ax**2 + ay**2 + az**2) 
                          for ax, ay, az in zip(ax_vals, ay_vals, az_vals)]
        gyro_magnitude = [np.sqrt(gx**2 + gy**2 + gz**2) 
                         for gx, gy, gz in zip(gx_vals, gy_vals, gz_vals)]
    else:
        timestamps = []
        accel_magnitude = []
        gyro_magnitude = []
    
    # Gráfico de aceleración absoluta
    accel_fig = go.Figure()
    accel_fig.add_trace(go.Scatter(
        x=timestamps,
        y=accel_magnitude,
        mode='lines',
        name='|Aceleración|',
        line=ACCEL_LINE_CONFIG,
        fill='tozeroy',
        fillcolor=ACCEL_FILL_COLOR
    ))
    accel_fig.update_layout(**get_graph_layout(
        f'Magnitud Absoluta de Aceleración (últimos {days} día(s))',
        'Magnitud (m/s²)'
    ))
    
    # Gráfico de giroscopio absoluto
    gyro_fig = go.Figure()
    gyro_fig.add_trace(go.Scatter(
        x=timestamps,
        y=gyro_magnitude,
        mode='lines',
        name='|Giroscopio|',
        line=GYRO_LINE_CONFIG,
        fill='tozeroy',
        fillcolor=GYRO_FILL_COLOR
    ))
    gyro_fig.update_layout(**get_graph_layout(
        f'Magnitud Absoluta de Giroscopio (últimos {days} día(s))',
        'Magnitud (°/s)'
    ))
    
    # Indicadores numéricos
    if latest:
        timestamp, ax, ay, az, gx, gy, gz, received_at = latest
        dt = datetime.fromtimestamp(timestamp/1000)
        time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        
        indicator_ax = create_indicator('AX', ax, COLORS['accel_color'])
        indicator_ay = create_indicator('AY', ay, COLORS['accel_color'])
        indicator_az = create_indicator('AZ', az, COLORS['accel_color'])
        indicator_gx = create_indicator('GX', gx, COLORS['gyro_color'])
        indicator_gy = create_indicator('GY', gy, COLORS['gyro_color'])
        indicator_gz = create_indicator('GZ', gz, COLORS['gyro_color'])
        
        last_update = f"🕐 Última actualización: {time_str}"
    else:
        indicator_ax = create_indicator('AX', 0, COLORS['accel_color'])
        indicator_ay = create_indicator('AY', 0, COLORS['accel_color'])
        indicator_az = create_indicator('AZ', 0, COLORS['accel_color'])
        indicator_gx = create_indicator('GX', 0, COLORS['gyro_color'])
        indicator_gy = create_indicator('GY', 0, COLORS['gyro_color'])
        indicator_gz = create_indicator('GZ', 0, COLORS['gyro_color'])
        last_update = "🕐 Sin datos disponibles"
    
    return (accel_fig, gyro_fig, 
            indicator_ax, indicator_ay, indicator_az,
            indicator_gx, indicator_gy, indicator_gz,
            last_update)

def create_indicator(label, value, color):
    """Crear un indicador numérico estilizado"""
    return html.Div([
        html.Div(label, style=INDICATOR_LABEL_STYLE),
        html.Div(f"{value:.2f}", style=get_indicator_value_style(color))
    ], style=INDICATOR_BOX_STYLE)

# ====
# EJECUTAR SERVIDOR
# ====
server = app.server

if __name__ == '__main__':
    logger.info("🚀 Iniciando dashboard...")
    logger.info("📊 Dashboard disponible en: http://127.0.0.1:8050")
    app.run(debug=os.getenv('DASH_DEBUG', 'False').lower() == 'true', 
            host=os.getenv('DASH_HOST', '0.0.0.0'), 
            port=int(os.getenv('DASH_PORT', 8050)))