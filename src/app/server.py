import socket
import threading
import re
from constants import *

HOST = "localhost"
PORT = 6667

threads = {}  # client_socket -> thread
clients = {}  # client_socket -> [username, addr, channel]
usernames = ["Server"]
channels = {DEFAULT_CHANNEL: []}  # channel_name -> [sockets]


def broadcast(sender_sock, msg: str, channel: str):
    """Send msg to everyone in the channel except sender."""
    if channel not in channels:
        return
    for sock in channels[channel]:
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
    uname, _, channel = clients[sock]
    parts = cmd.split()
    if parts[0] == "/help":
        help_text = (
            "Server: Available commands:\n"
            "  /help              Show this help message.\n"
            "  /users             List users in the current channel.\n"
            "  /nick <newname>    Change your display name.\n"
            "  /create <#channel> Create a new channel.\n"
            "  /join <#channel>   Join an existing channel.\n"
            "  /leave             Return to the #general channel.\n"
            "  /close             Disconnect from the chat server.\n"
        )
        send_to(sock, help_text)
        return False

    if parts[0] == "/users":
        count = len(channels[channel])
        send_to(sock, f"Server: There are {count} user(s) in {channel}.")
        return False

    if parts[0] == "/nick" and len(parts) > 1:
        new = parts[1]
        if new in usernames:
            send_to(sock, f"Server: [red]{new}[/red] is already taken.")
        else:
            broadcast(sock, f"Server: [magenta]{uname}[/magenta] is now [magenta]{new}[/magenta]", channel)
            usernames.remove(uname)
            usernames.append(new)
            clients[sock][0] = new
            send_to(sock, f"Server: Your nick is now {new}")
        return False

    if parts[0] == "/create" and len(parts) > 1:
        new_channel = parts[1]
        if not new_channel.startswith("#"):
            send_to(sock, "Server: Channel names must start with #")
        elif new_channel in channels:
            send_to(sock, f"Server: Channel {new_channel} already exists.")
        else:
            channels[new_channel] = []
            send_to(sock, f"Server: Channel {new_channel} created.")
        return False

    if parts[0] == "/join" and len(parts) > 1:
        new_channel = parts[1]
        if new_channel not in channels:
            send_to(sock, f"Server: Channel {new_channel} does not exist.")
        elif new_channel == channel:
            send_to(sock, f"Server: You are already in {channel}.")
        else:
            # leave old
            broadcast(sock, f"Server: [magenta]{uname}[/magenta] Left the channel", channel)
            channels[channel].remove(sock)
            # join new
            clients[sock][2] = new_channel
            channels[new_channel].append(sock)
            user_list = [clients[s][0] for s in channels[new_channel]]
            send_to(sock, f"Server: You joined {new_channel}. Users: {user_list}")
            broadcast(sock, f"Server: [magenta]{uname}[/magenta] Joined the channel", new_channel)
        return False

    if parts[0] == "/leave":
        if channel == DEFAULT_CHANNEL:
            send_to(sock, f"Server: You can't leave {DEFAULT_CHANNEL}.")
        else:
            broadcast(sock, f"Server: [magenta]{uname}[/magenta] Left the channel", channel)
            channels[channel].remove(sock)
            clients[sock][2] = DEFAULT_CHANNEL
            channels[DEFAULT_CHANNEL].append(sock)
            broadcast(sock, f"Server: [magenta]{uname}[/magenta] Joined the channel", DEFAULT_CHANNEL)
        return False

    if parts[0] == "/close":
        send_to(sock, MESSAGE_CLOSE)
        broadcast(sock, f"Server: [magenta]{uname}[/magenta] Left the server", channel)
        usernames.remove(uname)
        channels[channel].remove(sock)
        del clients[sock]
        sock.close()
        return True

    # unknown
    if parts[0] in COMMANDS:
        send_to(sock, f"Server: {parts[0]} requires an argument.")

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
    clients[sock] = [name, addr, DEFAULT_CHANNEL]
    channels[DEFAULT_CHANNEL].append(sock)
    send_to(sock, f"Server: Welcome {name}, you have joined {DEFAULT_CHANNEL}")
    broadcast(sock, f"Server: [magenta]{name}[/magenta] Joined the channel", DEFAULT_CHANNEL)

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
            uname, _, channel = clients[sock]
            broadcast(sock, f"{uname}: {data}", channel)

    # cleanup if fell out
    if sock in clients:
        uname, _, channel = clients[sock]
        usernames.remove(uname)
        channels[channel].remove(sock)
        del clients[sock]
        broadcast(sock, f"Server: [magenta]{uname}[/magenta] Left the server", channel)
        try:
            sock.close()
        except:
            pass

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
