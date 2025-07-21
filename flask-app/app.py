import pika
import os 
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq.default.svc.cluster.local')
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'test_queue')
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME', 'user')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'FoYDIoTBZc8UT6vj')


def get_channel():
    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    return channel, connection

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        data = request.get_json()
        message = data.get('message', 'Hello!')
    else:
        message = "Hello from GET request!"

    channel, connection = get_channel()
    channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=message)
    connection.close()
    return jsonify({"status": "Message sent!", "message": message})


def consume():
    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    def callback(ch, method, properties, body):
        print(f"[x] Received: {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=callback,
        auto_ack=False
    )

    print("[*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


threading.Thread(target=consume, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)