import socket
import threading

HOST = "localhost"
PORT = 6667

threads = []

def handle_server_commands(command: str, client_socket: socket):
    match command:
        case "/close":
            client_socket.sendall(b"Closed")
            client_socket.close()

def handle_client(client_socket: socket) -> None:
    while True:
        data = client_socket.recv(1024)
        data = data.decode("utf-8")

        if data.startswith("/"):
            handle_server_commands(data, client_socket)
            break
        else:
            print("cool")

        


def server():
    # soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # soc.bind((HOST, PORT))
    # soc.close()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        while True:
            server_socket.listen()
            (client_socket, addr) = server_socket.accept()
            handle_client(client_socket)
            thread = threading.Thread(handle_client, (client_socket,))
            threads.append(thread)
            thread.start()
            # with client_socket:
            #     print(f"Connected to {addr}")
            #     while True:
            #         data = client_socket.recv(1024)
            #         data = data.decode("utf-8")
            #         if not data:
            #             pass
            #         if data == "close":
            #             print("Why?")

server()