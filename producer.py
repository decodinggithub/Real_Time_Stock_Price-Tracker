# producer.py

import requests
from kafka import KafkaProducer
import json
import time
import logging

API_KEY = 'B310RUO18FN61WCX'
STOCK_SYMBOL = 'AAPL'
INTERVAL = '1min'
KAFKA_TOPIC = 'stock_price'

logging.basicConfig(level=logging.INFO, filename='producer.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_stock_price():
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={STOCK_SYMBOL}&interval={INTERVAL}&apikey={API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Fetched data: {data}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Alpha Vantage: {e}")
        return None

while True:
    stock_data = fetch_stock_price()
    if stock_data:
        for timestamp, values in stock_data.get('Time Series (1min)', {}).items():
            data = {
                'timestamp': timestamp,
                'open': values['1. open'],
                'high': values['2. high'],
                'low': values['3. low'],
                'close': values['4. close'],
                'volume': values['5. volume']
            }
            producer.send(KAFKA_TOPIC, value=data)
            logger.info(f"Sent data to Kafka: {data}")
    time.sleep(60)
