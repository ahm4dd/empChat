import socket
import threading
import time
HOST = "localhost"
PORT = 6667

threads = {} # client_socket : thread
clients = {} # client_socket : addr

def handle_server_commands(command: str, client_socket: socket):
    match command:
        case "/close":
            client_socket.sendall(b"Closed")
            client_socket.close()
            del clients[client_socket]

def handle_client(client_socket: socket) -> None:
    while True:
        data = client_socket.recv(1024)
        data = data.decode("utf-8")

        if data.startswith("/"):
            handle_server_commands(data, client_socket)
            break
        else:
            for client in clients.copy().keys():
                client.sendall(data.encode('utf-8') + b'\n')
                time.sleep(1)
            print(f"Client {clients[client_socket]} sent:\n-------------\n{data.encode('utf-8')}\n------------\n")


def server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            while True:
                server_socket.listen()
                (client_socket, addr) = server_socket.accept()
                print(f"Accepted connection: {addr}")
                clients[client_socket] = addr
                thread = threading.Thread(target=handle_client, args=(client_socket,))
                threads[client_socket] = thread
                thread.start()
    except Exception as ex:
        print(f"Error: {ex}")

server()