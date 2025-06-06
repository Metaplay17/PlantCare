import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
app_password = os.getenv("APP_PASSWORD")


def send_activation_email(email, code):
    # Данные
    recipient_email = email
    subject = "Подтверждение почты PlantCare"
    body = f"Для активации аккаунта перейдите по ссылке: https://localhost/confirm_email?email={recipient_email}&code={code}"

    # Создаем сообщение
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Добавляем тело письма
    msg.attach(MIMEText(body, 'plain'))

    # Подключаемся к SMTP-серверу Яндекса
    server = smtplib.SMTP('smtp.yandex.ru', 587)
    server.starttls()  # Включаем шифрование
    server.login(sender_email, app_password)

    # Отправляем письмо
    server.sendmail(sender_email, recipient_email, msg.as_string())
    print("✅ Письмо успешно отправлено!")
    return True
