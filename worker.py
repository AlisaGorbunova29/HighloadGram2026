import pika
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import redis

r = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "адрес_почты_с_которой_будут_отправляться_письма@gmail.com" 
EMAIL_PASSWORD = "код_почты"

def send_welcome_email(to_email, token):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = "HighloadGram. Установка пароля"

    link = f"http://localhost:5000/request-password?token={token}"
    body = f"""
    Здравствуйте!

    Перейдите по ссылке, чтобы установить пароль:

    {link}

    Ссылка действует 3 минуты.
    """

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()  # Включаем шифрование
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_ADDRESS, to_email, text)
    server.quit()


def callback(ch, method, properties, body):
    try:   
        message = json.loads(body)
        email = message["email"]
        token = message["token"]
        idempotency_key = message.get("idempotency_key")

        if r.exists(f"task:{idempotency_key}"):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        send_welcome_email(email, token)

        r.setex(f"task:{idempotency_key}", 86400, "1")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    

def start_worker():
    credentials = pika.PlainCredentials('user', 'password')
    connection_params = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=credentials
    )
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue='welcome_email_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='welcome_email_queue', on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    start_worker()