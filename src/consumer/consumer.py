import json
import os
import threading
import time
import xml.etree.ElementTree as ET
import xmlschema
from datetime import datetime
import re

import dotenv
import pika
from elasticsearch import Elasticsearch


def is_timestamp(input_str):
    try:
        datetime.fromtimestamp(float(input_str))
        return True
    except ValueError:
        return False


def convert_to_iso_timestamp(input_str):
    if is_timestamp(input_str):
        timestamp = float(input_str)
        dt_object = datetime.utcfromtimestamp(timestamp)
        return dt_object.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        return "Not a valid timestamp"


def validate_xml(xml_string, xsd_file):
    schema = xmlschema.XMLSchema(xsd_file)
    xml = ET.fromstring(xml_string)

    # for debugging other ppls heartbeats
    errors = schema.iter_errors(xml)
    for error in errors:
        print(f"sourceline: {error.sourceline}; path: {error.path} | reason: {error.reason} | message: {error.message}")

    if not schema.is_valid(xml):
        raise ValueError("xml invalid")

    # try:
    #     # Convert Unicode strings to byte strings
    #     xml_bytes = xml_file.encode()
    #     xsd_bytes = xsd_file.encode()

    #     # Parse XML document from byte string
    #     xml_doc = etree.fromstring(xml_bytes)

    #     # Parse XSD document from byte string
    #     xsd_doc = etree.fromstring(xsd_bytes)

    #     # Create XML schema object
    #     xml_schema = etree.XMLSchema(etree.XML(xsd_doc))

    #     # Validate XML document against XML schema
    #     is_valid = xml_schema.validate(xml_doc)

    #     return is_valid
    # except Exception as e:
    #     print(f"Error occurred during XML validation: {e}")
    #     return False


def main():
    dotenv.load_dotenv()

    username = os.getenv("RABBITMQ_USERNAME")
    password = os.getenv("RABBITMQ_PASSWORD")
    host = os.getenv("RABBITMQ_HOST")
    virtual_host = os.getenv("RABBITMQ_VIRTUAL_HOST")
    queue = os.getenv("RABBITMQ_QUEUE")
    log_queue = os.getenv("LOGGING_QUEUE")
    print("Connecting to RabbitMQ with the following credentials:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Host: {host}")
    print(f"Virtual Host: {virtual_host}")
    print(f"Queue: {queue}")
    print(f"Log queue: {log_queue}")
    print("=====================================")

    elastic_username = os.getenv("ELASTIC_USERNAME")
    elastic_password = os.getenv("ELASTIC_PASSWORD")
    print("Connecting to Elasticsearch with the following credentials:")
    print(f"Username: {elastic_username}")
    print(f"Password: {elastic_password}")
    print("=====================================")

    thread_kill = False

    # services to monitor
    services = []
    global services_last_timestamp
    services_last_timestamp = {}

    global error_sent
    error_sent = {}

    global email_timestamps
    email_timestamps = {}

    EMAIL_INTERVAL = 60

    def parse_element(element, json_data, index=None):
        if len(element) == 0:
            # if no more child
            if element.text is not None:
                tag = element.tag
                # when multiple tags with the same name, add numbers to differenciete them
                og_tag = tag
                while tag in json_data:
                    if index is None:
                        index = 2
                    else:
                        index += 1
                    tag = f"{og_tag}-{index}"
                json_data[tag] = element.text
            else:
                json_data[element.tag] = "None"
        else:
            # recursively parse each child
            for child in element:
                index = parse_element(child, json_data)
        return index

    def parse_xml_json(body):
        message = body.decode("utf-8")
        #print(f"=====================================\nReceived message:{message}")

        # remove " xmlns="http://ehb.local"" from the xml if present in it or ('<?xml version="1.0" encoding="UTF-8"?>', '') or similar (using re)
        message = re.sub(r'<\?xml[^>]*>|xmlns="http://ehb\.local"', "", message)
        # usefull for debugging re (i hate re, wish I was a 10x dev 😔)
        # print(f"cleaned message: {message}")
        # parse xml
        root = ET.fromstring(message)

        # parse it to json
        #print("Parsed XML:")
        json_data = {}

        parse_element(root, json_data)

        # add a timestamp if missing
        if "timestamp" not in json_data:
            timestamp = int(time.time())
            json_data["timestamp"] = timestamp

        json_message = json.dumps(json_data)
        #print(f"JSON message:\n{json_message}")

        return json_message, json_data

    def log_callback(ch, method, properties, body):
        try:
            json_message, _ = parse_xml_json(body)
        except Exception as e:
            print(f"\33[31mError parsing xml to json: {e}\33[0m")

        # send to elasticsearch
        try:
            es.index(index="logs", body=json_message)
        except Exception as e:
            print(f"\33[31mError indexing to Elasticsearch: {e}\33[0m")

    # pylance lies, callbacks call 4 args
    def heartbeat_callback(ch, method, properties, body):
        message = body.decode("utf-8")
 
        # this is mainly to debug invalid xml of other people, uncomment when needed
        # try:
        #     validate_xml(message, "/app/template.xsd")
        # except ValueError as e:
        #     print(f"ERROR: received an invalid XML: {message}")
        #     return
        try:
            json_message, json_data = parse_xml_json(body)
        except Exception as e:
            print(f"\33[31mError parsion xml to json: {e}\33[0m")

        # Send "Back online" email when service is back 
        service = json_data["service"]
        global error_sent
        if service in error_sent:
            error_sent.pop(service, None)
            print("Service back online: ", service)
            #send_error_email(ch, service, int(time.time()), "up", "")

        # send to elasticsearch
        try:
            es.index(index="heartbeat-rabbitmq", body=json_message)
            services_last_timestamp[service] = json_data["timestamp"]
        except Exception as e:
            print(f"\33[31mError indexing to Elasticsearch: {e}\33[0m")
            
    def send_error_email(channel, service, timestamp, status, error):
        global error_sent
        global email_timestamps

        current_time = time.time()
        last_email_time = email_timestamps.get(service, 0)

        if current_time - last_email_time < EMAIL_INTERVAL:
            print(f"Rate limit active for service {service}. Email not sent.")
            return
            
        if service in error_sent:
            print(f"Error email already sent for service {service}")
            return
        email_content = f"""
                        <heartbeat xmlns="http://ehb.local">
                        <service>{service}</service>
                        <timestamp>{timestamp}</timestamp>
                        <status>{status}</status>
                        <error>no heartbeat received</error>
                        </heartbeat>"""
        try:
            email_timestamps[service] = current_time
            error_sent[service] = True
            publish_to_rabbitmq(channel, email_content)
            print("Email content published to RabbitMQ successfully.")
        except Exception as e:
            print(f"Error publishing email content to RabbitMQ: {e}")

 
    def check_service_down(service):
        global services_last_timestamp
        global thread_kill
        username = os.getenv("RABBITMQ_USERNAME")
        password = os.getenv("RABBITMQ_PASSWORD")
        host = os.getenv("RABBITMQ_HOST")
        virtual_host = os.getenv("RABBITMQ_VIRTUAL_HOST")
        credentials = pika.PlainCredentials(username, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, virtual_host=virtual_host, credentials=credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange='amq.topic', exchange_type='topic', durable=True)

        while True:
            if thread_kill:
                break

            current_timestamp = int(time.time())
            # this means we haven't received a heartbeat in 10s since the last one was sent
            # -10s so afterwards it will be every 5s like they send us ups (for accumulative uptime) but still give them 3s room
            if current_timestamp - int(services_last_timestamp[service]) >= 10:
                es.index(index="heartbeat-rabbitmq", body={
                    'service': service,
                    'timestamp': current_timestamp - 5,
                    'status': 'down',
                    'error': 'no heartbeat received'
                })
                print(f"Didn't received heartbeat in 5s from {service}")
                send_error_email(channel, service, current_timestamp, "unavailable", "no heartbeat received")
                time.sleep(5)
            else:
                time.sleep(1)

    def publish_to_rabbitmq(channel, email_content):
        channel.basic_publish(exchange="amq.topic", routing_key="service", body=email_content)

    def stop_callback_check_services_down():
        global thread_kill
        thread_kill = True

        for thread in threading.enumerate():
            if thread.name == "check_service_down":
                thread.join()

        thread_kill = False

    def create_callback_check_services_down(services):
        for service in services:
            threading.Thread(
                target=check_service_down,
                name="check_service_down",
                args=(service[0],),
                daemon=True,
            ).start()

    def update_services():
        while True:
            global services_last_timestamp
            global services

            print("Updating services...")
            services = []
            with open(file="./heartbeat_rabbitmq.csv", mode="r") as csv:
                for line in csv:
                    service_line = line.strip().split(",")
                    for service in service_line:
                        services.append((service, int(time.time())))

            print(f"Services updated\nServices found: {services}")

            stop_callback_check_services_down()

            current_timestamp = int(time.time())
            services_last_timestamp = {service[0]: current_timestamp for service in services}

            create_callback_check_services_down(services)

            # update every minute
            time.sleep(60)

    print("Connecting to RabbitMQ with the following credentials:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Host: {host}")
    print(f"Virtual Host: {virtual_host}")
    print(f"Queue: {queue}")
    print(f"Log queue: {log_queue}")
    print("=====================================")
    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, virtual_host=virtual_host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.queue_declare(queue=log_queue)

    print("Connecting to Elasticsearch")
    es = Elasticsearch(["http://elasticsearch:9200"], basic_auth=(elastic_username, elastic_password))
    print("Waiting for Elasticsearch API to be up")
    while not es.ping():
        time.sleep(2)
    print("Connected to Elasticsearch")

    index_settings = {
        "properties": {
            "timestamp": {"type": "date", "format": "epoch_second"},
        }
    }

    # # delete the index, needed when an old indice is existing with other settings
    # try:
    #     es.indices.delete(index="heartbeat-rabbitmq")
    #     es.indices.delete(index="logs")
    #     print("Index deleted")
    # except Exception as e:
    #     print(f"Error deleting index: {e}")

    # create index if it doesn't exist
    try:
        es.indices.create(index="heartbeat-rabbitmq", ignore=400)
        es.indices.create(index="logs", ignore=400)
        print("Indexes created")
        # edit the index so that the timestamp value is a real timestamp
        try:
            es.indices.put_mapping(index="heartbeat-rabbitmq", body=index_settings, ignore=400)
            es.indices.put_mapping(index="logs", body=index_settings, ignore=400)
            print("Index settings updated")
        except Exception as e:
            print(f"Error updating index settings: {e}")
    except Exception as e:
        print(f"Error creating index: {e}")

    # consume all messages to clear the queue (avoid to get false stat when we are down/starting/...)
    channel.queue_purge(queue)

    print("Starting services update thread")
    threading.Thread(target=update_services, daemon=True).start()

    channel.basic_consume(queue=queue, on_message_callback=heartbeat_callback, auto_ack=True)
    channel.basic_consume(queue=log_queue, on_message_callback=log_callback, auto_ack=True)
    print("Waiting for msgs.")
    channel.start_consuming()


if __name__ == "__main__":
    main()
