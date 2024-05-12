import pika


def main():
    with open(".env", "r") as env:
        password = env.readline().strip()
    credentials = pika.PlainCredentials("mrgydtsi", password)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rat.rmq2.cloudamqp.com",
            virtual_host="mrgydtsi",
            credentials=credentials,
        )
    )
    channel = connection.channel()

    # not sure if it will have CAPS or not
    channel.queue_declare(queue="Heartbeat")

    # pylance lies, callbacks call 4 args
    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print(f"Received: {message}")

    # this queue = routing key from publisher
    channel.basic_consume(
        queue="Heartbeat", on_message_callback=callback, auto_ack=True
    )
    print("Waiting for msgs.")
    channel.start_consuming()


if __name__ == "__main__":
    main()
