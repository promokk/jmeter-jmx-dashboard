#!/bin/bash

# Описание: Prometheus / VictoriaMetrics HTTP Service Discovery (SD) Server

# Пример выполнения скрипта:
# sudo bash install-sd-server.sh

# Добавляем пользователей
useradd --no-create-home --shell /usr/sbin/nologin sd-server
# 1. Директория SD-сервера
mkdir /opt/sd-server
chown -R sd-server:sd-server /opt/sd-server
chmod 755 /opt/sd-server
cp sd_server.py /opt/sd-server/
# 2. Директория логов
mkdir -p /var/log/sd-server
chown -R sd-server:sd-server /var/log/sd-server
chmod 755 /var/log/sd-server

# Настраиваем сервис
cat << EOF > /etc/systemd/system/sd-server.service
[Unit]
Description=Prometheus / VictoriaMetrics HTTP Service Discovery (SD) Server
After=network.target

[Service]
Type=simple
User=sd-server
Group=sd-server
WorkingDirectory=/opt/sd-server
ExecStart=/usr/bin/python3 /opt/sd-server/sd_server.py
Restart=always
RestartSec=5
# or for example - journal
StandardOutput=append:/var/log/sd-server/sd_server.log 
StandardError=append:/var/log/sd-server/sd_server.log

[Install]
WantedBy=multi-user.target
EOF

# Настраиваем логирование
cat << EOF > /etc/logrotate.d/sd-server
/var/log/sd-server/sd_server.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF

# Запускаем сервис sd-server + логирование
logrotate -f /etc/logrotate.d/sd-server
systemctl daemon-reload
systemctl enable sd-server
systemctl start sd-server
