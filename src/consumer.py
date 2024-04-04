import os
import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch
import time
import json

import dotenv
import pika


def main():
    dotenv.load_dotenv()
    username = os.getenv("RABBITMQ_USERNAME")
    password = os.getenv("RABBITMQ_PASSWORD")
    host = os.getenv("RABBITMQ_HOST")
    virtual_host = os.getenv("RABBITMQ_VIRTUAL_HOST")
    queue = os.getenv("RABBITMQ_QUEUE")
    elastic_username = os.getenv("ELASTIC_USERNAME")
    elastic_password = os.getenv("ELASTIC_PASSWORD")
    print("Connecting to RabbitMQ with the following credentials:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Host: {host}")
    print(f"Virtual Host: {virtual_host}")
    print(f"Queue: {queue}")
    print("Connecting to Elasticsearch with the following credentials:")
    print(f"Username: {elastic_username}")
    print(f"Password: {elastic_password}")

    # connect to rabbitmq
    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, virtual_host=virtual_host, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    # connect to elasticsearch
    es = Elasticsearch(["http://elasticsearch:9200"], basic_auth=(elastic_username, elastic_password))
    # wait for elasticsearch api to be up
    while not es.ping():
        time.sleep(1)
    print("Connected to Elasticsearch")

    es.indices.create(index="heartbeat-rabbitmq", ignore=400)
    print("Index created")

    # pylance lies, callbacks call 4 args
    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print("=====================================")
        print("Received message:")
        print(message)

        # parse xml
        try:
            root = ET.fromstring(message)
        except ET.ParseError:
            print("\33[31mError parsing XML\33[0m")

        # parse it to json
        try:
            print("Parsed XML:")
            json_data = {}
            for child in root:
                print(child.tag, child.text)
                # can't parse None into elasticsearch
                if child.text is not None:
                    json_data[child.tag] = child.text
                else:
                    json_data[child.tag] = "None"

            json_message = json.dumps(json_data)
            print("JSON message:")
            print(json_message)
        except Exception as e:
            print(f"\33[31mError parsing  JSON: {e}\33[0m")

        # send to elasticsearch
        try:
            es.index(index="heartbeat-rabbitmq", body=json_message)
        except Exception as e:
            print(f"\33[31mError indexing to Elasticsearch: {e}\33[0m")

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
    print("Waiting for msgs.")
    channel.start_consuming()


if __name__ == "__main__":
    main()
