![managment](https://github.com/user-attachments/assets/424808a6-3c2f-4209-973e-e0f6d268d3a8)

# PS: всё делалось, собиралось и выкладывалось при помощи ChatGPT 4o, сам я хз как это всё делать с нуля, но получилось то что хотел, делюсь со всеми, может пригодится

# Управление серверами

Это проект для управления серверами и виртуальными машинами (VM), а также отслеживания выделенных и используемых ресурсов, таких как CPU, RAM, SSD и HDD.

## Используемые технологии

- **Python**: Основной язык программирования
- **Flask**: Веб-фреймворк для создания интерфейсов
- **Gunicorn**: WSGI сервер для продакшн запуска
- **MariaDB**: Для хранения данных
- **HTML/CSS**: Для фронтенда

## Зависимости

- Python 3.11+
- Flask
- Gunicorn
- pymysql
- MariaDB или MySQL
- pipx
- python3-venv

## Установка

### Установка через `.deb` пакет

Используйте команду для установки пакета:

```bash
sudo apt install ./servers_managment.deb
```


## Ручная установка

Если вы хотите установить проект вручную, выполните следующие шаги:

### Шаг 1: Клонирование репозитория

Сначала клонируйте репозиторий проекта и перейдите в каталог проекта:

```bash
git clone https://github.com/ваш-репозиторий/servers-management.git
cd servers-management
```

### Шаг 2: Настройка базы данных

Для работы приложения необходимо создать базу данных и пользователя в MariaDB или MySQL:

1. Запустите MariaDB:
   ```bash
   sudo service mariadb start
   ```

2. Откройте MariaDB:
   ```bash
   sudo mysql -u root -p
   ```

3. Создайте базу данных и пользователя:
   ```sql
   CREATE DATABASE SERVERMANAGER;
   CREATE USER 'SERVERMANAGER'@'localhost' IDENTIFIED BY 'SUPERPASSWORD';
   GRANT ALL PRIVILEGES ON SERVERMANAGER.* TO 'SERVERMANAGER'@'localhost';
   FLUSH PRIVILEGES;
   ```

4. Создайте необходимые таблицы:
   ```sql
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
     pending_delete BOOLEAN DEFAULT FALSE,
     FOREIGN KEY (server_id) REFERENCES servers(id)
   );
   ```

### Шаг 3: Настройка автозапуска (systemd)

Чтобы приложение запускалось автоматически при загрузке системы, создайте файл службы:

1. Создайте файл службы:

   ```bash
   sudo nano /etc/systemd/system/servers-managment.service
   ```

2. Вставьте в него следующее содержимое:

   ```ini
   [Unit]
   Description=Flask Application for Server Management
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/opt/servers-managment
   ExecStart=/opt/servers-managment/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:80 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Перезагрузите systemctl, активируйте службу и запустите её:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable servers-managment.service
   sudo systemctl start servers-managment.service
   ```

Теперь ваше приложение будет автоматически запускаться при загрузке системы.

## Зависимости

- Flask
- PyMySQL
- Gunicorn
- MariaDB

## Использование deb-пакета

В релизе проекта представлен deb-пакет для автоматической установки приложения и его зависимостей.

### Установка deb-пакета:

1. Установите пакет:
   ```bash
   sudo apt install ./servers-managment.deb
   ```

2. Во время установки автоматически:
   - Установится MariaDB и создадутся необходимые таблицы.
   - Будет настроена служба для автозапуска приложения.
   - Установятся зависимости через pipx и будет создано виртуальное окружение.

Если потребуется установить что-то вручную, воспользуйтесь инструкциями выше.
