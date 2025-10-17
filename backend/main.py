"""
Receptor principal de datos AWS IoT con TimescaleDB
"""
import logging
from config import LOG_LEVEL, LOG_FORMAT
from database import DatabaseManager
from mqtt_handler import MQTTHandler

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

def main():
    """Función principal"""
    db_manager = None
    mqtt_handler = None
    
    try:
        logger.info("Iniciando receptor AWS IoT...")
        
        # Inicializar base de datos
        db_manager = DatabaseManager()
        db_manager.connect()
        db_manager.initialize_schema()
        db_manager.get_stats()
        
        # Inicializar MQTT
        mqtt_handler = MQTTHandler(db_manager)
        
        if not mqtt_handler.connect():
            return
        
        if not mqtt_handler.subscribe():
            return
        
        # Mantener corriendo
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Deteniendo receptor...")
        
        # Estadísticas finales
        db_manager.get_stats()
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    finally:
        if mqtt_handler:
            mqtt_handler.disconnect()
        if db_manager:
            db_manager.close()

if __name__ == "__main__":
    main()
