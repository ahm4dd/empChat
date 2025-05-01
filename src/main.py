import socket

HOST = "localhost"
PORT = 6667


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

while True:
    (client_socket, address) = server_socket.accept()
    print(client_socket, address)