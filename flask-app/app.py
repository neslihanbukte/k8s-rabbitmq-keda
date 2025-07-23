import os
import pika
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)
QUEUE_NAME = 'test_queue'

# RabbitMQ kullanıcı bilgilerini environment variable olarak al, yoksa default kullan
RABBITMQ_USER = os.getenv('RABBITMQ_USERNAME', 'user')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASSWORD', 'FoYDIoTBZc8UT6vj')

def get_channel():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='my-rabbitmq.default.svc.cluster.local',
            credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)  # durable True yapıldı
    return channel, connection

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        data = request.get_json()
        message = data.get('message', 'Hello!')
    else:
        message = "Hello from GET request!"

    channel, connection = get_channel()
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)
    connection.close()
    return jsonify({"status": "Message sent!", "message": message})


def consume():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='my-rabbitmq.default.svc.cluster.local',
            credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)  # durable True yapıldı

    def callback(ch, method, properties, body):
        print(f"[x] Received: {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # mesaj onayı (ack)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False  # otomatik onay kapalı, manuel ack yapılıyor
    )
    print("[*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

threading.Thread(target=consume, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)