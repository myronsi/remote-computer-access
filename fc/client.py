import paramiko
import os


class SSHClient:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh = None
        self.sftp = None

    def connect(self):
        """Устанавливает SSH-соединение."""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
            )
            print(f"Подключено к {self.host}")
        except Exception as e:
            print(f"Ошибка подключения: {e}")

    def execute_command(self, command):
        """Выполняет команду на удалённом сервере."""
        if self.ssh:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            print(f"Результат выполнения команды:\n{stdout.read().decode()}")
            error = stderr.read().decode()
            if error:
                print(f"Ошибка:\n{error}")
        else:
            print("Сначала подключитесь к серверу.")        

    def upload_file(self, local_path, remote_path):
        """Передаёт файл на удалённый сервер."""
        try:
            if not self.sftp:
                self.sftp = self.ssh.open_sftp()
            self.sftp.put(local_path, remote_path)
            print(f"Файл {local_path} успешно передан в {remote_path}")
        except Exception as e:
            print(f"Ошибка передачи файла: {e}")

    def download_file(self, remote_path, local_path):
        """Загружает файл с удалённого сервера."""
        try:
            if not self.sftp:
                self.sftp = self.ssh.open_sftp()
            self.sftp.get(remote_path, local_path)
            print(f"Файл {remote_path} успешно загружен в {local_path}")
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")

    def upload_folder(self, local_folder, remote_folder):
        """Передаёт всю папку на удалённый сервер."""
        try:
            if not self.sftp:
                self.sftp = self.ssh.open_sftp()

            for root, dirs, files in os.walk(local_folder):
                remote_root = os.path.join(remote_folder, os.path.relpath(root, local_folder)).replace('\\', '/')
                try:
                    self.sftp.listdir(remote_root)  # Проверяем существование папки
                except FileNotFoundError:
                    self.sftp.mkdir(remote_root)

                for file in files:
                    local_file = os.path.join(root, file)
                    remote_file = os.path.join(remote_root, file).replace('\\', '/')
                    self.sftp.put(local_file, remote_file)
                    print(f"Файл {local_file} успешно передан в {remote_file}")
        except Exception as e:
            print(f"Ошибка передачи папки: {e}")

    def download_folder(self, remote_folder, local_folder):
        """Загружает всю папку с удалённого сервера."""
        try:
            if not self.sftp:
                self.sftp = self.ssh.open_sftp()

            os.makedirs(local_folder, exist_ok=True)

            for item in self.sftp.listdir_attr(remote_folder):
                remote_item = os.path.join(remote_folder, item.filename).replace('\\', '/')
                local_item = os.path.join(local_folder, item.filename)

                if item.st_mode & 0o40000:  # Проверка на директорию
                    self.download_folder(remote_item, local_item)
                else:
                    self.sftp.get(remote_item, local_item)
                    print(f"Файл {remote_item} успешно загружен в {local_item}")
        except Exception as e:
            print(f"Ошибка загрузки папки: {e}")            

    def close(self):
        """Закрывает SSH-соединение."""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        print("Соединение закрыто.")


# Пример использования
if __name__ == "__main__":
    # Настройки сервера
    host = "host"
    port = port
    username = "user"
    password = "pass"

    # Инициализация клиента
    client = SSHClient(host, port, username, password)

    # Подключение
    client.connect()

    # Выполнение команды
    client.execute_command("ls -la")

    # Передача папки
    local_folder = r"C:\Windows"
    remote_folder = "/home/user/windows"
    client.upload_folder(local_folder, remote_folder)

    # Передача файла
    local_file = r"C:\Documents\document.txt"
    remote_file = "/home/user/Documents\document.txt"
    client.upload_file(local_file, remote_file)

    # Загрузка файла и папки
    client.download_file(remote_file, local_file)
    client.download_folder(remote_folder, local_folder)

    # Закрытие соединения
    client.close()
