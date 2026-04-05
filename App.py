from flask import Flask, render_template, request, redirect, url_for, flash
import redis
import atexit
import uuid
import secrets

from rabbitMQ import RabbitMQClient


app = Flask(__name__, template_folder='templates')
app.secret_key = secrets.token_hex(16)

rabbit_client = RabbitMQClient()

r = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

users = {}

# основная страница
@app.route('/')
def main():
    message = request.args.get('message')
    if not message:
        message = ""
    
    user = request.args.get('user')
    if not user:
        user = "guest"
    
    return render_template('main_page.html', message=message, user=user)

# страница регистрации
@app.route('/request-invite', methods=['GET'])
def request_invite():
    message = request.args.get('message')
    if not message:
        message = ""

    return render_template('request_invite.html', message=message)

# отправка письма с токеном для регистрации
@app.route('/send-invite', methods=['POST'])
def send_invite():
    email = request.form.get('email')
    if not email:
        return render_template('request_invite.html', message="Введите email!")

    token = str(uuid.uuid4())
    r.setex(f"invite_token:{token}", 180, email)
    rabbit_client.send_message({"email": email, "token": token, "idempotency_key": str(uuid.uuid4())})

    return redirect(url_for('main', message = "Ссылка для регистрации отправлена на Ваш email."))


# страница для установки пароля
@app.route('/request-password', methods=['GET'])
def request_password():
    token = request.args.get('token')
    if not token:
        return redirect(url_for('main', message="Неверная или устаревшая ссылка."))

    email = r.get(f"invite_token:{token}")
    if not email:
        return redirect(url_for('main', message="Неверная или устаревшая ссылка."))

    return render_template('set_password.html', token=token, message="")

# страница для установки пароля
@app.route('/set-password', methods=['POST'])
def set_password():
    token = request.args.get('token')
    if not token:
        return redirect(url_for('main', message="Неверная или устаревшая ссылка."))

    email = r.get(f"invite_token:{token}")
    if not email:
        return redirect(url_for('main', message="Неверная или устаревшая ссылка."))

    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        return render_template('set_password.html', message="Пароли не совпадают.", token=token)

    users[email] = password

    r.delete(f"invite_token:{token}")

    return redirect(url_for('main', message="Пароль установлен! Теперь Вы можете войти."))


# страница авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return render_template('login.html', message="Все поля обязательны!")

        password_right = users.get(email)
        if password_right != password:
            return render_template('login.html', message="Неверный email или пароль.")

        return redirect(url_for('main', user=email))

    return render_template('login.html', message="")

# страница восстановления пароля
@app.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('forgot_password.html')

# отправка письма с токеном для регистрации
@app.route('/send-token-for-reset-password', methods=['POST'])
def send_token_for_reset_password():
    email = request.form.get('email')
    if not email:
        return render_template('forgot_password.html', message="Введите email!")

    token = str(uuid.uuid4())
    r.setex(f"invite_token:{token}", 180, email)
    rabbit_client.send_message({"email": email, "token": token, "idempotency_key": str(uuid.uuid4())})

    return redirect(url_for('main', message = "Ссылка для регистрации отправлена на Ваш email. Проверьте почту"))

@atexit.register
def close_rabbitmq():
    rabbit_client.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)