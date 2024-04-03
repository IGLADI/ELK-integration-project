import os
import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch

import dotenv
import pika


def main():
    dotenv.load_dotenv()
    username = os.getenv("RABBITMQ_USERNAME")
    password = os.getenv("RABBITMQ_PASSWORD")
    host = os.getenv("RABBITMQ_HOST")
    virtual_host = os.getenv("RABBITMQ_VIRTUAL_HOST")
    queue = os.getenv("RABBITMQ_QUEUE")
    routing_key = os.getenv("RABBITMQ_ROUTING_KEY")
    print("Connecting to RabbitMQ with the following credentials:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Host: {host}")
    print(f"Virtual Host: {virtual_host}")
    print(f"Queue: {queue}")
    print(f"Routing Key: {routing_key}")

    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, virtual_host=virtual_host, credentials=credentials))
    channel = connection.channel()

    # not sure if it will have CAPS or not
    channel.queue_declare(queue=queue)

    # pylance lies, callbacks call 4 args
    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print("=====================================")
        print("Received message:")
        print(message)
        try:
            root = ET.fromstring(message)
            for child in root:
                print(child.tag, child.text)
            Elasticsearch(["http://elasticsearch:9200"]).index(index="heartbeat", body=message)
        except ET.ParseError:
            print("\33[31mError parsing XML\33[0m")

    # this queue = routing key from publisher
    channel.basic_consume(queue=routing_key, on_message_callback=callback, auto_ack=True)
    print("Waiting for msgs.")
    channel.start_consuming()


if __name__ == "__main__":
    main()
