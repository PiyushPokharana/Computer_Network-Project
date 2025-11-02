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

    int sockfd = -1;
    char buffer[BUFFER_SIZE];
    struct sockaddr_in server_addr, client_addr;
    socklen_t addr_len = sizeof(client_addr);
    int recv_len = 0;

    // Create UDP socket
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
#ifdef _WIN32
    if (sockfd == INVALID_SOCKET)
    {
        fprintf(stderr, "Socket creation failed: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }
#else
    if (sockfd < 0)
    {
        perror("Socket creation failed");
        return 1;
    }
#endif

    // Clear and set up server address
    memset(&server_addr, 0, sizeof(server_addr));
    memset(&client_addr, 0, sizeof(client_addr));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    // Bind socket to the port
    if (bind(sockfd, (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
#ifdef _WIN32
        fprintf(stderr, "Bind failed: %d\n", WSAGetLastError());
        closesocket(sockfd);
        WSACleanup();
        return 1;
#else
        perror("Bind failed");
        close(sockfd);
        return 1;
#endif
    }

    printf("UDP Server listening on port %d...\n", PORT);

    // Receive data from client
    recv_len = (int)recvfrom(sockfd, buffer, BUFFER_SIZE - 1, 0,
                             (struct sockaddr *)&client_addr, &addr_len);
    if (recv_len < 0)
    {
#ifdef _WIN32
        fprintf(stderr, "Receive failed: %d\n", WSAGetLastError());
        closesocket(sockfd);
        WSACleanup();
#else
        perror("Receive failed");
        close(sockfd);
#endif
        return 1;
    }

    buffer[recv_len] = '\0'; // Null terminate
    printf("Client says: %s\n", buffer);

    // Optionally, send a reply back
    const char *reply = "Message received by server";
    sendto(sockfd, reply, (int)strlen(reply), 0, (struct sockaddr *)&client_addr, addr_len);

    printf("Reply sent. Closing server.\n");

#ifdef _WIN32
    closesocket(sockfd);
    WSACleanup();
#else
    close(sockfd);
#endif
    return 0;
}