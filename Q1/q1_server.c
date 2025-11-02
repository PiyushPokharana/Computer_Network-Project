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
    char buffer[1024] = {0};

    // Create socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
#ifdef _WIN32
    if (server_fd == INVALID_SOCKET)
    {
        fprintf(stderr, "socket failed: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }
#else
    if (server_fd < 0)
    {
        perror("socket failed");
        return 1;
    }
#endif

    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; // listen on any local IP
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0)
    {
#ifdef _WIN32
        fprintf(stderr, "bind failed: %d\n", WSAGetLastError());
        closesocket(server_fd);
        WSACleanup();
#else
        perror("bind failed");
        close(server_fd);
#endif
        return 1;
    }

    // Listen for one connection
    if (listen(server_fd, 1) < 0)
    {
#ifdef _WIN32
        fprintf(stderr, "listen failed: %d\n", WSAGetLastError());
        closesocket(server_fd);
        WSACleanup();
#else
        perror("listen failed");
        close(server_fd);
#endif
        return 1;
    }

    printf("Server listening on port %d...\n", PORT);

    // Accept connection
    new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen);
#ifdef _WIN32
    if (new_socket == INVALID_SOCKET)
    {
        fprintf(stderr, "accept failed: %d\n", WSAGetLastError());
        closesocket(server_fd);
        WSACleanup();
        return 1;
    }
#else
    if (new_socket < 0)
    {
        perror("accept failed");
        close(server_fd);
        return 1;
    }
#endif

    // Read data from client (use recv to be portable)
    int received = recv(new_socket, buffer, (int)sizeof(buffer) - 1, 0);
    if (received <= 0)
    {
        fprintf(stderr, "recv failed or connection closed\n");
    }
    else
    {
        buffer[received] = '\0';
        printf("Received from client: %s\n", buffer);
    }

#ifdef _WIN32
    closesocket(new_socket);
    closesocket(server_fd);
    WSACleanup();
#else
    close(new_socket);
    close(server_fd);
#endif
    printf("Connection closed.\n");
    return 0;
}