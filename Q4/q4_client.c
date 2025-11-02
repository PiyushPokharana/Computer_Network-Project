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
    struct sockaddr_in servaddr;
    char buffer[BUFFER_SIZE];
    const char *message = "Hello from UDP Client!";

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

    memset(&servaddr, 0, sizeof(servaddr));

    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(PORT);
    servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");

    // Send message to server
    sendto(sockfd, message, (int)strlen(message), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
    printf("Message sent to server.\n");

    // Wait for reply
#ifdef _WIN32
    int n = recvfrom(sockfd, buffer, BUFFER_SIZE - 1, 0, NULL, NULL);
#else
    ssize_t n = recvfrom(sockfd, buffer, BUFFER_SIZE - 1, 0, NULL, NULL);
#endif
    if (n < 0)
    {
#ifdef _WIN32
        fprintf(stderr, "recvfrom failed: %d\n", WSAGetLastError());
        closesocket(sockfd);
        WSACleanup();
#else
        perror("recvfrom failed");
        close(sockfd);
#endif
        return 1;
    }
    buffer[n] = '\0';
    printf("Server reply: %s\n", buffer);

#ifdef _WIN32
    closesocket(sockfd);
    WSACleanup();
#else
    close(sockfd);
#endif
    return 0;
}