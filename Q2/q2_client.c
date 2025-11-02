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

    int sock = -1;
    struct sockaddr_in serv_addr;
    const char *message = "Hello, world!";

    // Create socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
#ifdef _WIN32
    if (sock == INVALID_SOCKET)
    {
        fprintf(stderr, "Socket creation failed: %d\n", WSAGetLastError());
        WSACleanup();
        return -1;
    }
#else
    if (sock < 0)
    {
        perror("Socket creation failed");
        return -1;
    }
#endif

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    // Convert IPv4 address from text to binary form
#ifdef _WIN32
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    if (serv_addr.sin_addr.s_addr == INADDR_NONE)
    {
        fprintf(stderr, "Invalid address or not supported\n");
#ifdef _WIN32
        closesocket(sock);
        WSACleanup();
#else
        close(sock);
#endif
        return -1;
    }
#else
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0)
    {
        perror("Invalid address or not supported");
        close(sock);
        return -1;
    }
#endif

    // Connect to server
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {
#ifdef _WIN32
        fprintf(stderr, "Connection failed: %d\n", WSAGetLastError());
        closesocket(sock);
        WSACleanup();
#else
        perror("Connection failed");
        close(sock);
#endif
        return -1;
    }

    // Send the message
    int sent = send(sock, message, (int)strlen(message), 0);
    if (sent
#ifdef _WIN32
        == SOCKET_ERROR
#else
        < 0
#endif
    )
    {
#ifdef _WIN32
        fprintf(stderr, "send failed: %d\n", WSAGetLastError());
        closesocket(sock);
        WSACleanup();
#else
        perror("send failed");
        close(sock);
#endif
        return -1;
    }

    printf("Sent message: %s\n", message);

    // Close connection
#ifdef _WIN32
    closesocket(sock);
    WSACleanup();
#else
    close(sock);
#endif
    return 0;
}