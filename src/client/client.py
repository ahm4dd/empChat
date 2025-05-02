import socket
import threading
import time

HOST = "localhost"
PORT = 6667

my_socket = None

def data_read():
    while True:
        data = my_socket.recv(1024)
        if data.decode("utf-8") == "":
            continue

        print(f"Received:\n {data.decode("utf-8")}\n")
        if (data.decode("utf-8") == "Closed"):
            break

def data_send():
    while True:
        data_to_send = input()
        my_socket.sendall(data_to_send.encode("utf-8"))

def main():
    global my_socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        my_socket = s
        read_thread = threading.Thread(target=data_read)
        write_thread = threading.Thread(target=data_send)
        write_thread.setDaemon("True")
        read_thread.start()
        write_thread.start()
        while True:
            if not read_thread.is_alive:
                exit
                break


main()