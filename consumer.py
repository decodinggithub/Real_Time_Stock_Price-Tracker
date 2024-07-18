# consumer.py

from kafka import KafkaConsumer
import psycopg2
import json
import logging

KAFKA_TOPIC = 'stock_price'
DATABASE_NAME = 'Kafka_Stock_price'
USER = 'postgres'
PASSWORD = '@Postgre001'
HOST = 'localhost'
PORT = '5432'

logging.basicConfig(level=logging.INFO, filename='consumer.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

connection = psycopg2.connect(
    dbname=DATABASE_NAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)
cursor = connection.cursor()

create_table_query = '''
CREATE TABLE IF NOT EXISTS stock_prices (
    timestamp TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT
)
'''
cursor.execute(create_table_query)
connection.commit()

for message in consumer:
    data = message.value
    insert_query = '''
    INSERT INTO stock_prices (timestamp, open, high, low, close, volume)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''
    try:
        cursor.execute(insert_query, (
            data['timestamp'],
            data['open'],
            data['high'],
            data['low'],
            data['close'],
            data['volume']
        ))
        connection.commit()
        logger.info(f"Inserted data into PostgreSQL: {data}")
    except Exception as e:
        logger.error(f"Error inserting data into PostgreSQL: {e}")
