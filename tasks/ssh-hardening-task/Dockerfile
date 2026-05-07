FROM ubuntu:22.04

# Устанавливаем переменные окружения
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    nano \
    vim \
    curl \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя student (не root)
RUN useradd -m -s /bin/bash student && \
    echo "student:student123" | chpasswd && \
    usermod -aG sudo student && \
    echo "student ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Создаем SSH директорию
RUN mkdir -p /var/run/sshd && \
    mkdir -p /home/student/.ssh && \
    chown -R student:student /home/student/.ssh && \
    chmod 700 /home/student/.ssh

# Копируем НЕБЕЗОПАСНУЮ конфигурацию SSH (задание - сделать безопасной)
# Это исходное состояние, которое студент должен исправить
COPY files/sshd_config /etc/ssh/sshd_config

# Копируем скрипт проверки
COPY check.sh /usr/local/bin/check.sh
RUN chmod +x /usr/local/bin/check.sh

# Копируем entrypoint скрипт
COPY files/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Создаем лог директорию
RUN mkdir -p /var/log/ssh

# Экспонируем SSH порт
EXPOSE 22 2222

# Запускаем SSH сервер
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D"]
