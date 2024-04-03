import os

import dotenv
import pika


def main():
    dotenv.load_dotenv()
    username = os.getenv("RABBITMQ_USERNAME")
    password = os.getenv("RABBITMQ_PASSWORD")
    host = os.getenv("RABBITMQ_HOST")
    virtual_host = os.getenv("RABBITMQ_VIRTUAL_HOST")

    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, virtual_host=virtual_host, credentials=credentials))
    channel = connection.channel()

    # not sure if it will have CAPS or not
    channel.queue_declare(queue="Heartbeat")

    # pylance lies, callbacks call 4 args
    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print(f"Received: {message}")

    # this queue = routing key from publisher
    channel.basic_consume(queue="Heartbeat", on_message_callback=callback, auto_ack=True)
    print("Waiting for msgs.")
    channel.start_consuming()


if __name__ == "__main__":
    main()
