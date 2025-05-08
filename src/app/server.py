import socket
import threading
import re
from constants import *

HOST = "localhost"
PORT = 6667

threads = {}    # client_socket -> thread
clients = {}    # client_socket -> [username, addr]
usernames = ["Server"]

def broadcast(sender_sock, msg: str):
    """Send msg to everyone except sender."""
    for sock in list(clients):
        if sock is not sender_sock:
            try:
                sock.sendall(msg.encode("utf-8"))
            except:
                pass

def send_to(sock, msg: str):
    """Send msg only to this sock."""
    try:
        sock.sendall(msg.encode("utf-8"))
    except:
        pass

def handle_commands(cmd: str, sock: socket.socket):
    uname, _ = clients[sock]
    parts = cmd.split()
    if parts[0] == "/help":
        help_text = (
            "Server: Available commands:\n"
            "/help            Show this message\n"
            "/users           Number of connected users\n"
            "/nick <newname>  Change your nickname\n"
            "/close           Leave the chat\n"
        )
        send_to(sock, help_text)
        return False
    if parts[0] == "/users":
        count = len(clients)
        send_to(sock, f"Server: There are {count} user(s) online.")
        return False
    if parts[0] == "/nick" and len(parts) > 1:
        new = parts[1]
        if new in usernames:
            send_to(sock, f"Server: [red]{new}[/red] is already taken.")
        else:
            # broadcast leave under old name
            broadcast(sock, f"Server: [magenta]{uname}[/magenta] Left the server")
            # update lists
            usernames.remove(uname)
            usernames.append(new)
            clients[sock][0] = new
            send_to(sock, f"Server: Welcome {new}")
            broadcast(sock, f"Server: [magenta]{new}[/magenta] Joined the server")
        return False
    if parts[0] == "/close":
        # let client know to close
        send_to(sock, MESSAGE_CLOSE)
        broadcast(sock, f"Server: [magenta]{uname}[/magenta] Left the server")
        usernames.remove(uname)
        del clients[sock]
        sock.close()
        return True
    # unknown
    return False

def handle_client(sock: socket.socket):
    """Per‑connection thread."""
    addr = sock.getpeername()
    # Ask for username
    send_to(sock, "Server: Enter your username:")
    name = sock.recv(1024).decode("utf-8").strip()
    # enforce unique
    while name in usernames:
        send_to(sock, f"Server: [red]{name}[/red] already exists, choose another:")
        name = sock.recv(1024).decode("utf-8").strip()
    if not name or name == "/close":
        send_to(sock, MESSAGE_CLOSE)
        sock.close()
        return

    # register
    usernames.append(name)
    clients[sock] = [name, addr]
    send_to(sock, f"Server: Welcome {name}")
    broadcast(sock, f"Server: [magenta]{name}[/magenta] Joined the server")

    # listen
    while True:
        try:
            data = sock.recv(1024).decode("utf-8").strip()
            if not data:
                break
        except:
            break

        if data.startswith("/"):
            done = handle_commands(data, sock)
            if done:
                break
        else:
            # normal chat
            uname, _ = clients[sock]
            broadcast(sock, f"{uname}: {data}")

    # cleanup if fell out
    if sock in clients:
        uname, _ = clients[sock]
        usernames.remove(uname)
        del clients[sock]
        broadcast(sock, f"Server: [magenta]{uname}[/magenta] Left the server")
        try: sock.close()
        except: pass

def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[+] Chat server listening on {HOST}:{PORT}")
        while True:
            client_sock, _ = s.accept()
            t = threading.Thread(target=handle_client, args=(client_sock,), daemon=True)
            threads[client_sock] = t
            t.start()

if __name__ == "__main__":
    server()
