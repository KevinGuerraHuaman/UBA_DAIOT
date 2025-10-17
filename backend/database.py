"""
Gestión de base de datos TimescaleDB
"""
import psycopg2
from psycopg2.extras import execute_batch
import logging
from config import (
    TIMESCALE_HOST, TIMESCALE_PORT, TIMESCALE_DB,
    TIMESCALE_USER, TIMESCALE_PASSWORD
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexión y operaciones con TimescaleDB"""
    
    def __init__(self):
        self.conn = None
    
    def connect(self):
        """Establecer conexión con TimescaleDB"""
        try:
            logger.info("Conectando a TimescaleDB...")
            
            self.conn = psycopg2.connect(
                host=TIMESCALE_HOST,
                port=TIMESCALE_PORT,
                database=TIMESCALE_DB,
                user=TIMESCALE_USER,
                password=TIMESCALE_PASSWORD,
                sslmode='require'
            )
            
            self.conn.autocommit = False
            logger.info("Conectado a TimescaleDB")
            
        except psycopg2.OperationalError as e:
            logger.error(f"Error de conexión: {e}")
            raise
    
    def initialize_schema(self):
        """Crear tablas e índices"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar TimescaleDB
            cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';")
            version = cursor.fetchone()
            if version:
                logger.info(f"TimescaleDB versión: {version[0]}")
            
            # Crear tabla
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id SERIAL,
                    timestamp BIGINT NOT NULL,
                    ax DOUBLE PRECISION NOT NULL,
                    ay DOUBLE PRECISION NOT NULL,
                    az DOUBLE PRECISION NOT NULL,
                    gx DOUBLE PRECISION NOT NULL,
                    gy DOUBLE PRECISION NOT NULL,
                    gz DOUBLE PRECISION NOT NULL,
                    received_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            self.conn.commit()
            logger.info("Tabla sensor_data verificada")
            
            # Convertir a hypertable
            try:
                cursor.execute("""
                    SELECT create_hypertable('sensor_data', 'timestamp', 
                        chunk_time_interval => 8640000, 
                        if_not_exists => TRUE);
                """)
                self.conn.commit()
                logger.info("Hypertable creada")
            except Exception as e:
                if "already a hypertable" in str(e):
                    logger.info("Hypertable ya existe")
                else:
                    logger.warning(f"No se pudo crear hypertable: {e}")
                self.conn.rollback()
            
            # Crear índice
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sensor_timestamp 
                ON sensor_data (timestamp DESC);
            """)
            self.conn.commit()
            cursor.close()
            logger.info("Base de datos inicializada")
            
        except Exception as e:
            logger.error(f"Error al inicializar BD: {e}")
            raise
    
    def save_samples(self, samples):
        """Guardar muestras en la base de datos"""
        try:
            cursor = self.conn.cursor()
            
            data_to_insert = [
                (s['t'], s['a'][0], s['a'][1], s['a'][2], 
                 s['g'][0], s['g'][1], s['g'][2])
                for s in samples
            ]
            
            execute_batch(cursor, """
                INSERT INTO sensor_data (timestamp, ax, ay, az, gx, gy, gz)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data_to_insert)
            
            self.conn.commit()
            cursor.close()
            logger.info(f"{len(samples)} registros guardados")
            
        except Exception as e:
            logger.error(f"Error al guardar: {e}")
            self.conn.rollback()
    
    def get_stats(self):
        """Obtener estadísticas de la base de datos"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    MAX(timestamp) as latest,
                    MIN(timestamp) as earliest
                FROM sensor_data
            """)
            
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0] > 0:
                logger.info(f"Total registros: {result[0]}")
                logger.info(f"Timestamp más reciente: {result[1]} ms")
                logger.info(f"Timestamp más antiguo: {result[2]} ms")
            else:
                logger.info("No hay datos en la base de datos")
            
            return result
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return None
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
            logger.info("Conexión cerrada")
