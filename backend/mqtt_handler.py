"""
Gestión de conexión MQTT con AWS IoT Core
"""
import json
import logging
import os
import tempfile
import shutil
from datetime import datetime
from awscrt import mqtt
from awsiot import mqtt_connection_builder
from config import (
    AWS_IOT_ENDPOINT, AWS_IOT_PORT, AWS_IOT_CLIENT_ID,
    AWS_IOT_TOPIC, AWS_ROOT_CA, AWS_CERTIFICATE, AWS_PRIVATE_KEY,
    AWS_ROOT_CA_CONTENT, AWS_CERTIFICATE_CONTENT, AWS_PRIVATE_KEY_CONTENT
)

logger = logging.getLogger(__name__)

class MQTTHandler:
    """Gestor de conexión MQTT con AWS IoT Core"""
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.mqtt_connection = None
        self.cert_dir = None
    
    def setup_certificates(self):
        """Configurar certificados desde archivos o variables de entorno"""
        # Producción: certificados desde variables de entorno
        if all([AWS_ROOT_CA_CONTENT, AWS_CERTIFICATE_CONTENT, AWS_PRIVATE_KEY_CONTENT]):
            logger.info("Usando certificados desde variables de entorno")
            return self._create_temp_certificates()
        
        # Desarrollo: certificados desde archivos
        elif all([os.path.exists(AWS_ROOT_CA), os.path.exists(AWS_CERTIFICATE), 
                  os.path.exists(AWS_PRIVATE_KEY)]):
            logger.info("Usando certificados desde archivos")
            return AWS_ROOT_CA, AWS_CERTIFICATE, AWS_PRIVATE_KEY
        
        else:
            raise FileNotFoundError(
                "No se encontraron certificados válidos.\n"
                "Opciones: 1) Archivos en backend/certs/ 2) Variables de entorno"
            )
    
    def _create_temp_certificates(self):
        """Crear archivos temporales de certificados"""
        self.cert_dir = tempfile.mkdtemp()
        
        root_ca_path = os.path.join(self.cert_dir, 'root-CA.pem')
        cert_path = os.path.join(self.cert_dir, 'certificate.pem.crt')
        key_path = os.path.join(self.cert_dir, 'private.pem.key')
        
        with open(root_ca_path, 'w') as f:
            f.write(AWS_ROOT_CA_CONTENT)
        with open(cert_path, 'w') as f:
            f.write(AWS_CERTIFICATE_CONTENT)
        with open(key_path, 'w') as f:
            f.write(AWS_PRIVATE_KEY_CONTENT)
        
        os.chmod(root_ca_path, 0o400)
        os.chmod(cert_path, 0o400)
        os.chmod(key_path, 0o400)
        
        logger.info("Certificados temporales creados")
        return root_ca_path, cert_path, key_path
    
    def validate_endpoint(self, endpoint):
        """Validar formato del endpoint"""
        if not endpoint:
            logger.error("Falta configurar AWS_IOT_ENDPOINT")
            return False
        
        if endpoint.startswith(("https://", "mqtts://")):
            logger.error("El endpoint no debe incluir protocolo")
            return False
        
        if ":" in endpoint:
            logger.error("El endpoint no debe incluir puerto")
            return False
        
        return True
    
    def on_connection_interrupted(self, connection, error, **kwargs):
        """Callback: conexión interrumpida"""
        logger.error(f"Conexión MQTT interrumpida: {error}")
    
    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback: conexión restablecida"""
        logger.info(f"Conexión MQTT restablecida (code: {return_code})")
    
    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """Callback: mensaje recibido"""
        try:
            message = json.loads(payload.decode('utf-8'))
            num_samples = len(message.get('samples', []))
            
            logger.info(f"Mensaje recibido - {num_samples} muestras")
            
            # Guardar en base de datos
            self.db_manager.save_samples(message.get('samples', []))
            
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON: {e}")
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {e}")
    
    def connect(self):
        """Establecer conexión con AWS IoT Core"""
        try:
            if not self.validate_endpoint(AWS_IOT_ENDPOINT):
                return False
            
            root_ca, certificate, private_key = self.setup_certificates()
            
            logger.info(f"Conectando a AWS IoT: {AWS_IOT_ENDPOINT}")
            
            self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=AWS_IOT_ENDPOINT,
                port=AWS_IOT_PORT,
                cert_filepath=certificate,
                pri_key_filepath=private_key,
                ca_filepath=root_ca,
                client_id=AWS_IOT_CLIENT_ID,
                clean_session=False,
                keep_alive_secs=30,
                on_connection_interrupted=self.on_connection_interrupted,
                on_connection_resumed=self.on_connection_resumed
            )
            
            connect_future = self.mqtt_connection.connect()
            connect_future.result()
            logger.info("Conectado a AWS IoT Core")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al conectar: {e}")
            return False
    
    def subscribe(self):
        """Suscribirse al tópico"""
        try:
            logger.info(f"Suscribiéndose a: {AWS_IOT_TOPIC}")
            
            subscribe_future, packet_id = self.mqtt_connection.subscribe(
                topic=AWS_IOT_TOPIC,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self.on_message_received
            )
            
            subscribe_result = subscribe_future.result()
            logger.info(f"Suscrito con QoS: {subscribe_result['qos']}")
            logger.info("Esperando mensajes...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al suscribirse: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de AWS IoT"""
        try:
            if self.mqtt_connection:
                logger.info("Desconectando de AWS IoT...")
                disconnect_future = self.mqtt_connection.disconnect()
                disconnect_future.result()
                logger.info("Desconectado")
            
            # Limpiar certificados temporales
            if self.cert_dir and os.path.exists(self.cert_dir):
                shutil.rmtree(self.cert_dir)
                logger.info("Certificados temporales eliminados")
                
        except Exception as e:
            logger.error(f"Error al desconectar: {e}")
