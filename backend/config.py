"""
Configuración centralizada usando variables de entorno
"""
import os
from dotenv import load_dotenv

load_dotenv()

# AWS IoT Core
AWS_IOT_ENDPOINT = os.getenv('AWS_IOT_ENDPOINT')
AWS_IOT_PORT = int(os.getenv('AWS_IOT_PORT', 8883))
AWS_IOT_CLIENT_ID = os.getenv('AWS_IOT_CLIENT_ID', 'Python_Receiver')
AWS_IOT_TOPIC = os.getenv('AWS_IOT_TOPIC', 'esp32/mpu6050/data')

# Certificados (desarrollo local)
AWS_ROOT_CA = os.getenv('AWS_ROOT_CA', 'backend/certs/root-CA.pem')
AWS_CERTIFICATE = os.getenv('AWS_CERTIFICATE', 'backend/certs/certificate.pem.crt')
AWS_PRIVATE_KEY = os.getenv('AWS_PRIVATE_KEY', 'backend/certs/private.pem.key')

# Certificados (producción - contenido completo)
AWS_ROOT_CA_CONTENT = os.getenv('AWS_ROOT_CA_CONTENT')
AWS_CERTIFICATE_CONTENT = os.getenv('AWS_CERTIFICATE_CONTENT')
AWS_PRIVATE_KEY_CONTENT = os.getenv('AWS_PRIVATE_KEY_CONTENT')

# TimescaleDB Cloud
TIMESCALE_HOST = os.getenv('TIMESCALE_HOST')
TIMESCALE_PORT = int(os.getenv('TIMESCALE_PORT', 5432))
TIMESCALE_DB = os.getenv('TIMESCALE_DB', 'tsdb')
TIMESCALE_USER = os.getenv('TIMESCALE_USER')
TIMESCALE_PASSWORD = os.getenv('TIMESCALE_PASSWORD')

# Aplicación
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DASH_DEBUG = os.getenv('DASH_DEBUG', 'False').lower() == 'true'
DASH_HOST = os.getenv('DASH_HOST', '0.0.0.0')
DASH_PORT = int(os.getenv('DASH_PORT', 8050))

def validate_config():
    """Validar variables críticas"""
    required = {
        'TIMESCALE_HOST': TIMESCALE_HOST,
        'TIMESCALE_PASSWORD': TIMESCALE_PASSWORD,
        'TIMESCALE_USER': TIMESCALE_USER,
        'AWS_IOT_ENDPOINT': AWS_IOT_ENDPOINT,
    }
    
    missing = [k for k, v in required.items() if not v]
    
    if missing:
        raise ValueError(
            f"Faltan variables de entorno: {', '.join(missing)}\n"
            f"Verifica tu archivo .env o las variables del servidor"
        )
    
    return True

# Validar al importar
if __name__ != '__main__':
    validate_config()