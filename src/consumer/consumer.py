import json
import os
import threading
import time
import xml.etree.ElementTree as ET

import dotenv
import pika
from elasticsearch import Elasticsearch


def main():
    dotenv.load_dotenv()

    username = os.getenv("RABBITMQ_USERNAME")
    password = os.getenv("RABBITMQ_PASSWORD")
    host = os.getenv("RABBITMQ_HOST")
    virtual_host = os.getenv("RABBITMQ_VIRTUAL_HOST")
    queue = os.getenv("RABBITMQ_QUEUE")
    print("Connecting to RabbitMQ with the following credentials:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Host: {host}")
    print(f"Virtual Host: {virtual_host}")
    print(f"Queue: {queue}")
    print("=====================================")

    elastic_username = os.getenv("ELASTIC_USERNAME")
    elastic_password = os.getenv("ELASTIC_PASSWORD")
    print("Connecting to Elasticsearch with the following credentials:")
    print(f"Username: {elastic_username}")
    print(f"Password: {elastic_password}")
    print("=====================================")

    # services to monitor
    services = []
    global services_last_timestamp
    services_last_timestamp = {}

    # pylance lies, callbacks call 4 args
    def heartbeat_callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print(f"=====================================\nReceived message:{message}")

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
            services_last_timestamp[json_data["service"]] = json_data["timestamp"]
        except Exception as e:
            print(f"\33[31mError indexing to Elasticsearch: {e}\33[0m")

    def check_service_down(service):
        global services_last_timestamp

        while True:
            current_timestamp = int(time.time())
            # this means we haven't received a heartbeat in 2s since the last one was sent
            if current_timestamp - int(services_last_timestamp[service]) >= 2:
                heartbeat_callback(
                    None,
                    None,
                    None,
                    f"""<heartbeat>
                    <service>{service}</service>
                    <timestamp>{current_timestamp}</timestamp>
                    <error>503</error>
                    <status>down</status>
                    <extra><message>Didn't received heartbeat in 2s</message></extra>
                </heartbeat>""".encode(
                        "utf-8"
                    ),
                )
                print(f"Didn't received heartbeat in 2s from {service}")
                time.sleep(1)

    def stop_callback_check_services_down():
        for thread in threading.enumerate():
            if thread.name == "check_service_down":
                thread.raise_exception()
                thread.join()

    def create_callback_check_services_down(services):
        for service in services:
            threading.Thread(target=check_service_down, name="check_service_down", args=(service[0],), daemon=True).start()

    def update_services():
        while True:
            global services_last_timestamp
            global services

            print("Updating services...")
            services = []
            with open(file="/heartbeat_rabbitmq.csv", mode="r") as csv:
                for line in csv:
                    service_line = line.strip().split(",")
                    for service in service_line:
                        services.append((service, int(time.time())))

            print(f"Services updated\nServices found: {services}")

            stop_callback_check_services_down()

            current_timestamp = int(time.time())
            services_last_timestamp = {service[0]: current_timestamp for service in services}

            create_callback_check_services_down(services)

            # update every 5s
            time.sleep(5)

    print("Connecting to RabbitMQ")
    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, virtual_host=virtual_host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue)

    print("Connecting to Elasticsearch")
    es = Elasticsearch(["http://elasticsearch:9200"], basic_auth=(elastic_username, elastic_password))
    print("Waiting for Elasticsearch API to be up")
    while not es.ping():
        time.sleep(1)
    print("Connected to Elasticsearch")

    # create index if it doesn't exist
    try:
        es.indices.create(index="heartbeat-rabbitmq", ignore=400)
        print("Index created")
    except Exception as e:
        print(f"Error creating index: {e}")

    print("Starting services update thread")
    threading.Thread(target=update_services, daemon=True).start()

    channel.basic_consume(queue=queue, on_message_callback=heartbeat_callback, auto_ack=True)
    print("Waiting for msgs.")
    channel.start_consuming()


if __name__ == "__main__":
    main()
