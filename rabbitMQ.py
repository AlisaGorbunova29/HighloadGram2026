import pika
import json
import uuid

class RabbitMQClient:
    def __init__(self, host='localhost', port=5672, username='user', password='password'):
        self.credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=self.credentials,
            heartbeat=600,
            connection_attempts=5,
            retry_delay=5
        )
        self.connection = None

    def _get_connection(self):
        if self.connection is None or self.connection.is_closed:
            credentials = pika.PlainCredentials('user', 'password')
            connection_params = pika.ConnectionParameters(
                host='localhost',
                port=5672,
                heartbeat=600,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(connection_params)
        return self.connection

    def send_message(self, message):
        message["idempotency_key"] = str(uuid.uuid4())

        conn = self._get_connection()
        channel = conn.channel()
        channel.queue_declare(queue='welcome_email_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='welcome_email_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        channel.close()

    def close(self):
        """Закрывает соединение"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()