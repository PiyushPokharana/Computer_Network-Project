#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")
#else
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#endif

#define PORT 8080
#define BUFFER_SIZE 1024

int main()
{
#ifdef _WIN32
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
    {
        fprintf(stderr, "WSAStartup failed: %d\n", WSAGetLastError());
        return 1;
    }
#endif

    int server_fd = -1, new_socket = -1;
    struct sockaddr_in address;
    socklen_t addrlen = sizeof(address);
    char buffer[BUFFER_SIZE];
    char message[BUFFER_SIZE];

    // Create socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
#ifdef _WIN32
    if (server_fd == INVALID_SOCKET)
    {
        fprintf(stderr, "Socket failed: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }
#else
    if (server_fd < 0)
    {
        perror("Socket failed");
        return 1;
    }
#endif

    // Bind to localhost:8080
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0)
    {
#ifdef _WIN32
        fprintf(stderr, "Bind failed: %d\n", WSAGetLastError());
        closesocket(server_fd);
        WSACleanup();
        return 1;
#else
        perror("Bind failed");
        close(server_fd);
        return 1;
#endif
    }

    // Listen for one client
    if (listen(server_fd, 1) < 0)
    {
#ifdef _WIN32
        fprintf(stderr, "Listen failed: %d\n", WSAGetLastError());
        closesocket(server_fd);
        WSACleanup();
        return 1;
#else
        perror("Listen failed");
        close(server_fd);
        return 1;
#endif
    }

    printf("Server listening on port %d...\n", PORT);

    // Accept client connection
    new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen);
#ifdef _WIN32
    if (new_socket == INVALID_SOCKET)
    {
        fprintf(stderr, "Accept failed: %d\n", WSAGetLastError());
        closesocket(server_fd);
        WSACleanup();
        return 1;
    }
#else
    if (new_socket < 0)
    {
        perror("Accept failed");
        close(server_fd);
        return 1;
    }
#endif

    printf("Client connected! Type 'exit' to end chat.\n");

    // Chat loop
    while (1)
    {
        memset(buffer, 0, BUFFER_SIZE);
#ifdef _WIN32
        int valread = recv(new_socket, buffer, BUFFER_SIZE - 1, 0);
#else
        int valread = recv(new_socket, buffer, BUFFER_SIZE - 1, 0);
#endif
        if (valread <= 0)
        {
            printf("Client disconnected.\n");
            break;
        }
        buffer[valread] = '\0';

        printf("Client: %s\n", buffer);

        if (strncmp(buffer, "exit", 4) == 0)
            break;

        printf("You: ");
        fgets(message, BUFFER_SIZE, stdin);
        message[strcspn(message, "\n")] = 0; // Remove newline

        send(new_socket, message, (int)strlen(message), 0);

        if (strncmp(message, "exit", 4) == 0)
            break;
    }

#ifdef _WIN32
    closesocket(new_socket);
    closesocket(server_fd);
    WSACleanup();
#else
    close(new_socket);
    close(server_fd);
#endif
    printf("Chat ended.\n");
    return 0;
}