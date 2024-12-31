#include <iostream>
#include <string>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>

#define PORT 9999
#define BUFFER_SIZE 4096

int main() {
    int server_fd, client_fd;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};

    // Создаем сокет
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("[!] Ошибка создания сокета");
        return 1;
    }

    // Настраиваем сервер
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("[!] Ошибка привязки сокета");
        return 1;
    }

    if (listen(server_fd, 1) < 0) {
        perror("[!] Ошибка прослушивания");
        return 1;
    }

    std::cout << "[+] Ожидание подключения на 0.0.0.0:" << PORT << "..." << std::endl;

    if ((client_fd = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen)) < 0) {
        perror("[!] Ошибка принятия подключения");
        return 1;
    }

    std::cout << "[+] Подключение установлено: " << inet_ntoa(address.sin_addr) << ":" << ntohs(address.sin_port) << std::endl;

    while (true) {
        std::string command;
        std::cout << "Введите команду: ";
        std::getline(std::cin, command);

        if (command.empty()) {
            std::cout << "Команда не может быть пустой!" << std::endl;
            continue;
        }

        send(client_fd, command.c_str(), command.size(), 0);
        int valread = recv(client_fd, buffer, BUFFER_SIZE, 0);
        if (valread > 0) {
            buffer[valread] = '\0';
            std::cout << "Ответ от клиента:\n" << buffer << std::endl;
        } else {
            std::cerr << "[!] Ошибка получения ответа" << std::endl;
            break;
        }
    }

    close(client_fd);
    close(server_fd);
    return 0;
}
