import paramiko
import os

# Настройки подключения
linux_server = "ip"  # IP-адрес Linux-компьютера
ssh_port = port
ssh_username = "linux_user"
ssh_password = "your_password"

# Локальный файл и удалённая директория
local_file = r"C:\path\to\your\file.txt"  # Файл на Windows
remote_path = "/home/linux_user/remote_directory/file.txt"  # Путь на Linux

# Подключение к Linux через SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(linux_server, port=ssh_port, username=ssh_username, password=ssh_password)

# Передача файла
with ssh.open_sftp() as sftp:
    sftp.put(local_file, remote_path)
    print(f"Файл {local_file} успешно передан в {remote_path}.")

# Закрытие соединения
ssh.close()
print("Соединение закрыто.")
