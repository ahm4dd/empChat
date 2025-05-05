import socket
import threading
import time
import re
import rich
from constants import *
from rich import print
from rich.prompt import Prompt

HOST = "localhost"
PORT = 6667

username = None

my_socket = None
stop_event = threading.Event() # An event to indicate that the client has disconnected




def data_read():
    global username
    while not stop_event.is_set():
        data = my_socket.recv(1024)
        data = data.decode("utf-8")
        if data == "":
            continue
        if username == None and len(re.findall("^(Server: Welcome) (.*?)$", data)) == 1:
            username = re.findall("^(Server: Welcome) (.*?)$", data)[0][1]
        if len(re.findall("^(Server:) (.*)$", data)) == 1:
            rich.print(f"\n[bold red]{re.findall("^(Server:) (.*)$", data)[0][0]}[/bold red]: [blue]{re.findall("^(Server:) (.*)$", data)[0][1]}[/blue]\n")
        else:
            rich.print(f"\n-------------\n[bold yellow]{re.findall("^(.*?): (.*)$", data)[0][0]}[/bold yellow]: [orange4]{re.findall("^(.*?): (.*)$", data)[0][1]}[/orange4]\n-------------\n")
        if (data == MESSAGE_CLOSE):
            stop_event.set()
            return
        
def data_send():
    global username
    while not stop_event.is_set():
        try:
            if username == None:
                data_to_send = input()
            else:
                data_to_send = Prompt.ask(f"[bold magenta]{username}[/bold magenta]")
            if data_to_send != f"{username}:" and data_to_send != "":
                my_socket.sendall(data_to_send.encode("utf-8"))
        except KeyboardInterrupt:
            print("Test")


def main():
    global my_socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        my_socket = s
        read_thread = threading.Thread(target=data_read)
        write_thread = threading.Thread(target=data_send)
        write_thread.daemon = True
        stop_event.clear()
        try:
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
                write_thread.join()
                my_socket.close()

main()