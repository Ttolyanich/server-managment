Название проекта: Управление серверами
Этот проект представляет собой простое веб-приложение для управления серверами и виртуальными машинами (VM), а также отслеживания выделенных и используемых ресурсов, таких как CPU, RAM, SSD и HDD.

Используемые технологии
Python: Основной код приложения написан на Python с использованием фреймворка Flask.
Gunicorn: Для запуска Flask-приложения в продакшене.
MariaDB: В качестве базы данных для хранения информации о серверах и виртуальных машинах.
HTML/CSS: Для структуры и стилизации интерфейса.
Debian Packaging: В релизе доступен .deb установщик для систем на основе Debian.
Зависимости
Python 3.11+
Flask
Gunicorn
pymysql
MariaDB (или MySQL)
pipx (для установки Gunicorn)
python3-venv (для создания виртуального окружения)
Функционал
Управление серверами и виртуальными машинами: Добавление, редактирование и удаление серверов и виртуальных машин.
Отслеживание использования ресурсов: Поддержка отображения и анализа использования CPU, RAM, SSD и HDD как на уровне серверов, так и на уровне виртуальных машин.
Отмена удаления: Возможность отменить удаление серверов и виртуальных машин до их окончательного удаления.
Как установить
1. Установка через .deb пакет
Релиз включает готовый .deb пакет для установки на системы на основе Debian. Для установки выполните команду:

bash
Копировать код
sudo apt install ./servers_managment.deb
Это установит приложение, настроит необходимые зависимости и создаст систему для автозапуска сервиса через systemd.

2. Ручная установка
Шаг 1: Клонирование проекта
Сначала клонируйте репозиторий:

bash
Копировать код
git clone https://github.com/ваш-репозиторий/servers-management.git
cd servers-management
Шаг 2: Создание виртуального окружения и установка зависимостей
Создайте виртуальное окружение и установите все зависимости:

bash
Копировать код
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Шаг 3: Настройка базы данных
Для работы приложения необходимо настроить базу данных в MariaDB или MySQL.

Запустите MariaDB и создайте базу данных:
bash
Копировать код
sudo service mariadb start
mysql -u root -p
Создайте базу данных и пользователя:
sql
Копировать код
CREATE DATABASE SERVERMANAGER;
CREATE USER 'SERVERMANAGER'@'localhost' IDENTIFIED BY 'SUPERPASSWORD';
GRANT ALL PRIVILEGES ON SERVERMANAGER.* TO 'SERVERMANAGER'@'localhost';
FLUSH PRIVILEGES;
Создайте таблицы для серверов и виртуальных машин:
sql
Копировать код
USE SERVERMANAGER;

CREATE TABLE servers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    cpu INT,
    ram INT,
    ssd INT,
    hdd INT,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE virtual_machines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    cpu INT,
    ram INT,
    ssd INT,
    hdd INT,
    server_id INT,
    deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (server_id) REFERENCES servers(id)
);
Шаг 4: Настройка авторизации
Откройте файл app.py и замените данные для подключения к базе данных в функции connect_db:

python
Копировать код
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='SERVERMANAGER',
        password='SUPERPASSWORD',
        db='SERVERMANAGER',
        cursorclass=pymysql.cursors.DictCursor
    )
Шаг 5: Запуск приложения
Чтобы запустить приложение, выполните команду:

bash
Копировать код
gunicorn --workers 3 --bind 0.0.0.0:80 app:app
Теперь приложение доступно на порту 80.

Ручной запуск сервиса
Приложение поддерживает автоматический запуск с помощью systemd. Если вы не хотите использовать Nginx, приложение можно запускать прямо на порту 80 через Gunicorn.

Пример systemd-сервиса:
Файл: /etc/systemd/system/servers.service:

ini
Копировать код
[Unit]
Description=Servers Management Service
After=network.target

[Service]
User=root
WorkingDirectory=/opt/servers
ExecStart=/opt/servers/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:80 app:app
Restart=always

[Install]
WantedBy=multi-user.target
После добавления конфигурации перезапустите systemd и активируйте сервис:

bash
Копировать код
sudo systemctl daemon-reload
sudo systemctl enable servers.service
sudo systemctl start servers.service
Особенности
Поддержка удаления серверов и виртуальных машин с возможностью отмены.
Поддержка круглых диаграмм для отображения использования ресурсов.
Легкая установка через .deb пакет.
