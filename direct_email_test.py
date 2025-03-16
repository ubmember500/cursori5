import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

def send_test_email(password=None):
    """
    Отправляет тестовое письмо напрямую через SMTP
    """
    try:
        print("Начинаю тестирование отправки email напрямую через SMTP...")
        
        # Настройки SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "defensivelox@gmail.com"
        
        # Используем пароль из аргументов или запрашиваем его
        if password is None:
            if len(sys.argv) > 1:
                password = sys.argv[1]
                print(f"Получен пароль из аргументов командной строки")
            else:
                password = input("Введите пароль для Gmail (defensivelox@gmail.com): ")
        
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = smtp_username
        msg['Subject'] = "Тестовое сообщение от Cursor Shop"
        
        body = "Это тестовое сообщение для проверки работы отправки email."
        msg.attach(MIMEText(body, 'plain'))
        
        # Подключаемся к серверу
        print(f"Подключение к {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)  # Включаем подробное логирование
        server.ehlo()
        
        # Включаем шифрование
        print("Включение TLS...")
        server.starttls()
        server.ehlo()
        
        # Авторизуемся
        print(f"Авторизация с логином {smtp_username}...")
        server.login(smtp_username, password)
        
        # Отправляем сообщение
        print("Отправка сообщения...")
        server.sendmail(smtp_username, smtp_username, msg.as_string())
        
        # Закрываем соединение
        server.quit()
        
        print("Сообщение успешно отправлено!")
        return True
        
    except Exception as e:
        print(f"Ошибка при отправке тестового сообщения: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    send_test_email() 