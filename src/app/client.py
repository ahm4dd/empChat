import socket
import threading
import time
import re
from constants import *

HOST = "localhost"
PORT = 6667

username = ""

my_socket = None
stop_event = threading.Event() # An event to indicate that the client has disconnected

def data_read():
    global username
    while not stop_event.is_set():
        data = my_socket.recv(1024)
        data = data.decode("utf-8")
        if data == "":
            continue
        if username == "" and len(re.findall("^Server: Welcome (.*?)$", data)) == 2:
            username = re.findall("^(Server: Welcome )(.*?)$", data)[1]
        print(f"\n{data}\n")
        if (data == MESSAGE_CLOSE):
            stop_event.set()
            return
        
def data_send():
    global username
    while not stop_event.is_set():
        data_to_send = input(f"{username}:")
        if data_to_send != f"{username}:":
            my_socket.sendall(data_to_send.encode("utf-8"))

def main():
    global my_socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            my_socket = s
            read_thread = threading.Thread(target=data_read)
            write_thread = threading.Thread(target=data_send)
            write_thread.daemon = True
            stop_event.clear()
            read_thread.start()
            write_thread.start()
            while True:
                if stop_event.is_set():
                    write_thread.join()
                    my_socket.close()
                    return

    except KeyboardInterrupt:
        my_socket.sendall(b"/close")
        stop_event.set()
        if stop_event.is_set():
            read_thread.join()
            write_thread.join()
            my_socket.close()

main()