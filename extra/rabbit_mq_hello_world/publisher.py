import pika
import time


# note that this creates a one time connection for each msg sent
def send_message(message):
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

    channel.basic_publish(exchange="", routing_key="Heartbeat", body=message)
    print("msg sent")
    connection.close()


def main():
    while True:
        service = "Service1"
        timestamp = int(time.time())
        status = "up"
        error = 200
        extra = ""
        message = f"""<heartbeat>
            <service>{service}</service>
            <timestamp>{timestamp}</timestamp>
            <error>{error}</error>
            <status>{status}</status>
            <extra>{extra}</extra>
        </heartbeat>"""
        send_message(message)
        time.sleep(1)


if __name__ == "__main__":
    main()
