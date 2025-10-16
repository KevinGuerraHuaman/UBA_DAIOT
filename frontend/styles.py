"""
Módulo de estilos para el dashboard MPU6050
Contiene todos los estilos CSS, colores y configuraciones visuales
"""

# ====
# PALETA DE COLORES
# ====
COLORS = {
    'background': '#f5f6fa',
    'card_background': '#ffffff',
    'header_bg': '#ecf0f1',
    'primary_text': '#2c3e50',
    'secondary_text': '#7f8c8d',
    'accent_text': '#34495e',
    'accel_color': '#e74c3c',
    'accel_light': '#fadbd8',
    'gyro_color': '#3498db',
    'gyro_light': '#d6eaf8',
    'white': '#ffffff'
}

# ====
# ESTILOS DE LAYOUT PRINCIPAL
# ====
MAIN_CONTAINER_STYLE = {
    'padding': '20px',
    'backgroundColor': COLORS['background'],
    'fontFamily': 'Arial, sans-serif'
}

# ====
# ESTILOS DE ENCABEZADO
# ====
HEADER_CONTAINER_STYLE = {
    'backgroundColor': COLORS['header_bg'],
    'padding': '20px',
    'borderRadius': '10px',
    'marginBottom': '20px'
}

HEADER_TITLE_STYLE = {
    'textAlign': 'center',
    'color': COLORS['primary_text'],
    'marginBottom': '10px'
}

HEADER_SUBTITLE_STYLE = {
    'textAlign': 'center',
    'color': COLORS['secondary_text'],
    'fontSize': '16px'
}

# ====
# ESTILOS DE SELECTOR DE TIEMPO
# ====
TIME_SELECTOR_CONTAINER_STYLE = {
    'textAlign': 'center',
    'marginBottom': '20px'
}

TIME_SELECTOR_LABEL_STYLE = {
    'fontWeight': 'bold',
    'marginRight': '10px'
}

TIME_SELECTOR_DROPDOWN_STYLE = {
    'width': '200px',
    'display': 'inline-block'
}

# ====
# ESTILOS DE TARJETAS
# ====
CARD_STYLE = {
    'backgroundColor': COLORS['card_background'],
    'padding': '20px',
    'borderRadius': '10px',
    'marginBottom': '20px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
}

CARD_TITLE_STYLE = {
    'textAlign': 'center',
    'color': COLORS['accent_text'],
    'marginBottom': '15px'
}

# ====
# ESTILOS DE INDICADORES
# ====
LAST_UPDATE_STYLE = {
    'textAlign': 'center',
    'fontSize': '14px',
    'color': COLORS['secondary_text'],
    'marginBottom': '15px'
}

INDICATORS_CONTAINER_STYLE = {
    'display': 'flex',
    'marginBottom': '30px'
}

ACCEL_SECTION_STYLE = {
    'flex': '1',
    'padding': '10px',
    'backgroundColor': COLORS['accel_light'],
    'borderRadius': '10px',
    'margin': '5px'
}

GYRO_SECTION_STYLE = {
    'flex': '1',
    'padding': '10px',
    'backgroundColor': COLORS['gyro_light'],
    'borderRadius': '10px',
    'margin': '5px'
}

INDICATOR_TITLE_ACCEL_STYLE = {
    'textAlign': 'center',
    'color': COLORS['accel_color']
}

INDICATOR_TITLE_GYRO_STYLE = {
    'textAlign': 'center',
    'color': COLORS['gyro_color']
}

INDICATOR_VALUES_CONTAINER_STYLE = {
    'display': 'flex',
    'justifyContent': 'space-around'
}

INDICATOR_ITEM_STYLE = {
    'flex': '1'
}

# ====
# ESTILOS DE GRÁFICOS
# ====
GRAPH_CONTAINER_STYLE = {
    'marginBottom': '20px'
}

INDICATOR_BOX_STYLE = {
    'textAlign': 'center',
    'padding': '15px',
    'backgroundColor': COLORS['white'],
    'borderRadius': '8px',
    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
    'margin': '5px'
}

INDICATOR_LABEL_STYLE = {
    'fontSize': '14px',
    'fontWeight': 'bold',
    'color': COLORS['secondary_text'],
    'marginBottom': '5px'
}

def get_indicator_value_style(color):
    """Retorna el estilo para el valor del indicador con color específico"""
    return {
        'fontSize': '28px',
        'fontWeight': 'bold',
        'color': color
    }

# ====
# CONFIGURACIÓN DE GRÁFICOS PLOTLY
# ====
GRAPH_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
}

def get_graph_layout(title, yaxis_title, height=400):
    """Retorna el layout base para gráficos"""
    return {
        'title': title,
        'xaxis_title': 'Tiempo',
        'yaxis_title': yaxis_title,
        'hovermode': 'x unified',
        'template': 'plotly_white',
        'height': height
    }

# ====
# CONFIGURACIÓN DE LÍNEAS DE GRÁFICOS
# ====
ACCEL_LINE_CONFIG = {
    'color': COLORS['accel_color'],
    'width': 2
}

GYRO_LINE_CONFIG = {
    'color': COLORS['gyro_color'],
    'width': 2
}

ACCEL_FILL_COLOR = 'rgba(231, 76, 60, 0.2)'
GYRO_FILL_COLOR = 'rgba(52, 152, 219, 0.2)'

# ====
# OPCIONES DE DROPDOWN
# ====
TIME_RANGE_OPTIONS = [
    {'label': '1 Día', 'value': 1},
    {'label': '7 Días', 'value': 7},
    {'label': '30 Días', 'value': 30}
]

# ====
# CONFIGURACIÓN DE ACTUALIZACIÓN
# ====
UPDATE_INTERVAL = 5 * 1000  # 5 segundos en milisegundos