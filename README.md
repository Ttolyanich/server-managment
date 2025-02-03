![managment](https://github.com/user-attachments/assets/424808a6-3c2f-4209-973e-e0f6d268d3a8)

# PS: всё делалось, собиралось и выкладывалось при помощи ChatGPT 4o, сам я хз как это всё делать с нуля, но получилось то что хотел, делюсь со всеми, может пригодится
## админка по пути /admin

# Управление серверами

Это проект для управления серверами и виртуальными машинами (VM), а также отслеживания выделенных и используемых ресурсов, таких как CPU, RAM, SSD и HDD.

## Используемые технологии

- **Python**: Основной язык программирования
- **Flask**: Веб-фреймворк для создания интерфейсов
- **Gunicorn**: WSGI сервер для продакшн запуска
- **HTML/CSS**: Для фронтенда

## Зависимости

- Python 3.11+
- Flask
- Gunicorn
- pipx
- python3-venv

## Установка

### Шаг 1: Клонирование репозитория

Сначала клонируйте репозиторий проекта и перейдите в каталог проекта:

```bash
cd /opt
git clone https://github.com/Ttolyanich/servers-managment.git
cd /opt/servers-managment/
```

### Шаг 2: Установка пакетов и настройка

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip gunicorn nginx -y
```
Создание и активация виртуального окружения:
```bash
python3 -m venv /opt/servers-managment/venv
source /opt/servers-managment/venv/bin/activate
pip install --break-system-packages flask gunicorn
```
Установка Flask и Gunicorn:
```bash
pip install flask gunicorn
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
Description=Server Managment
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/servers-managment
ExecStart=/opt/servers-managment/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

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

Настройка Nginx для проксирования:
```bash
sudo nano /etc/nginx/sites-enabled/servers-managment
```

```bash
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
Перезапустить NGINX
```bash
systemctl restart nginx
```

## Зависимости

- Python3
- Flask
- Gunicorn
