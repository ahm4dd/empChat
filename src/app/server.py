import socket
import threading
import time
from constants import *

HOST = "localhost"
PORT = 6667

threads = {} # client_socket : thread
clients = {} # client_socket : [username, addr]
usernames = []

def check_username(client_socket, username):
    while username in usernames and username != "exit":
        client_socket.sendall(b"-------------\nServer: Username Exists!\n-------------\n-------------\nEnter a new username or 'exit' to exit the program:\n-------------")
        username = client_socket.recv(1024).decode("utf-8").strip()
    if username != "exit" and username != "/close":
        client_socket.sendall(b"Server: Welcome "+ username.encode("utf-8"))
        return username
    else:
        print(f"Client {client_socket}:\n-------------\n{"Left the server".encode('utf-8')}\n-------------")
        client_socket.sendall(MESSAGE_CLOSE.encode("utf-8"))
        client_socket.close()
        return "invalid"


def handle_server_commands(command: str, client_socket: socket):
    match command:
        case "/close":
            client_socket.sendall(MESSAGE_CLOSE.encode("utf-8"))
            send_to_users(client_socket, "Left the server")
            usernames.remove(clients[client_socket][0])
            del clients[client_socket]
            client_socket.close()
            return MESSAGE_CLOSE
        case _:
            return "Unknown"

def handle_client(client_socket: socket):
    while True:
        data = client_socket.recv(1024)
        data = data.decode("utf-8")

        if data.startswith("/"):
            result = handle_server_commands(data, client_socket)
            if result == MESSAGE_CLOSE:
                del threads[client_socket]
                break  # Exit the loop BEFORE trying to recv again
            elif result == "Unknown":
                pass
        else:
            send_to_users(client_socket, data)
            

def send_to_users(client_socket, data):
    for client in clients.copy().keys():
        if client == client_socket:
            continue
        client.sendall(f"-------------\n{clients[client_socket][0]}: {data}\n-------------".encode("utf-8"))
    print(f"Client {clients[client_socket]}:\n-------------\n{data.encode('utf-8')}\n-------------")

def server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            while True:
                server_socket.listen()
                (client_socket, addr) = server_socket.accept()
                print(f"New connection: {addr}")
                client_socket.sendall(b"Server: Enter your username:\n")
                username = client_socket.recv(1024).decode("utf-8").strip()
                if check_username(client_socket, username) != "invalid":
                    usernames.append(username)
                    print(f"Accepted connection: {username}:{addr}")
                    clients[client_socket] = [username, addr]
                    thread = threading.Thread(target=handle_client, args=(client_socket,))
                    threads[client_socket] = thread
                    send_to_users(client_socket, "Joined the server")
                    thread.start()

    except Exception as ex:
        print(f"Error: {ex}")

server()