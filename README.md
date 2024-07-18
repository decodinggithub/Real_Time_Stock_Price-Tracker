# Real_Time_Stock_Price-Tracker
This project tracks real-time stock prices using Alpha Vantage API, Kafka, and Zookeeper. Data is stored in PostgreSQL and visualized with Metabase. It ensures high availability and low-latency processing, providing actionable insights into stock market trends.
Steps Involved
1. Set Up the Environment
Install Kafka and Zookeeper:
Download and extract Kafka, which includes Zookeeper : tar -xzf kafka_2.13-2.8.0.tgz  cd kafka_2.13-2.8.0
Start Zookeeper and Kafka Servers: # Start Zookeeper : bin/zookeeper-server-start.sh config/zookeeper.properties
# Start Kafka
bin/kafka-server-start.sh config/server.properties

# Create Kafka Topic
Create a Kafka topic named stock_price: bin/kafka-topics.sh --create --topic stock_price --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Develop the Producer
producer.py: This script fetches stock prices from Alpha Vantage API and sends them to the Kafka topic.
from kafka import KafkaProducer
import requests
import json
import time
producer = KafkaProducer(bootstrap_servers='localhost:9092')
api_key = 'Your_API_Key'
symbol = 'AAPL'
while True:
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    for timestamp, values in data['Time Series (1min)'].items():
        message = {
            'symbol': symbol,
            'price': values['1. open'],
            'timestamp': timestamp
        }
        producer.send('stock_price', json.dumps(message).encode('utf-8'))
    time.sleep(60)

# Develop the Consumer
consumer.py: This script reads data from the Kafka topic and stores it in PostgreSQL. 
from kafka import KafkaConsumer
import psycopg2
import json

consumer = KafkaConsumer('stock_price', bootstrap_servers='localhost:9092')
conn = psycopg2.connect(database="your_database", user="your_user", password="your_password", host="localhost", port="5432")
cursor = conn.cursor()

for message in consumer:
    data = json.loads(message.value)
    cursor.execute("INSERT INTO stock_prices (symbol, price, timestamp) VALUES (%s, %s, %s)", (data['symbol'], data['price'], data['timestamp']))
    conn.commit()

# Set Up PostgreSQL Database
Create Table in PostgreSQL:
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    price DECIMAL,
    timestamp TIMESTAMP
);

# Visualize Data with Metabase
Connect Metabase to PostgreSQL: Configure a new database connection in Metabase to your PostgreSQL instance.
Create Dashboards and Visualizations: Use Metabase’s GUI to create dashboards that visualize stock price trends and patterns.

# Running the System
Start the Producer: python producer.py
Start the Consumer: python consumer.py
This setup will enable real-time tracking of stock prices, storing the data in PostgreSQL, and visualizing it with Metabase.
