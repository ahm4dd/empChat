import socket, threading, re
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer, Input, Static
from textual.reactive import reactive
from rich.text import Text

HOST = "localhost"
PORT = 6667
MESSAGE_CLOSE = "/close"

class ChatClient(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    Header { dock: top; }
    Footer { dock: bottom; }
    #chat_display {
        border: round green;
        height: 1fr; overflow: auto;
    }
    #users_display {
        border: round magenta;
        width: 24; height: 1fr; overflow: auto;
    }
    #input_widget { border: round blue; height: 3; }
    """

    chat_log: reactive[list[Text]] = reactive([])
    users: reactive[list[str]]    = reactive([])
    username: str | None          = None

    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()
        self.sock: socket.socket | None = None
        self.user_colors: dict[str,str] = {}
        self.palette = ["cyan","green","yellow","blue","magenta","red","white"]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            self.chat_display = Static(id="chat_display")
            self.users_display = Static(id="users_display")
            yield self.chat_display
            yield self.users_display
        self.input_box = Input(placeholder="Type /help for commands", id="input_widget")
        yield self.input_box
        yield Footer()

    def on_mount(self):
        self.chat_log.append(Text("Connecting to server…", style="bold green"))
        self.update_displays()
        threading.Thread(target=self._connect, daemon=True).start()

    def _connect(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((HOST, PORT))
            threading.Thread(target=self._recv_loop, daemon=True).start()
        except Exception as e:
            self.chat_log.append(Text(f"Connect error: {e}", style="bold red"))
            self.update_displays()

    def _recv_loop(self):
        sock = self.sock
        while sock and not self.stop_event.is_set():
            try:
                raw = sock.recv(1024)
            except:
                break
            if not raw:
                break
            text = raw.decode("utf-8")
            # handle system
            if text.startswith("Server:"):
                # parse markup and show a subtle border
                try:
                    msg = Text.from_markup(text.replace("Server:", "[bold white]Server:[/bold white] "))
                except:
                    msg = Text(text)
                self.chat_log.append(msg)
                # update users list on join/leave
                if "Joined the server" in text or "Left the server" in text:
                    names = re.findall(r"\[magenta\](.*?)\[/magenta\]", text)
                    for n in names:
                        if "Joined" in text and n not in self.users:
                            self.users.append(n)
                        if "Left"   in text and n in self.users:
                            self.users.remove(n)
                # Welcome
                m = re.match(r"Server: Welcome (.+)", text)
                if m and not self.username:
                    self.username = m.group(1)
                    self.users.append(self.username)
            else:
                # normal user message
                m = re.match(r"^(.*?): (.*)$", text)
                if m:
                    sender, body = m.groups()
                    color = self._color_for(sender)
                    self.chat_log.append(
                        Text.assemble((f"{sender}: ", f"bold {color}"), (body, "white"))
                    )
                else:
                    self.chat_log.append(Text(text, style="white"))

            self.update_displays()

        self.stop_event.set()
        if sock:
            sock.close()

    def _color_for(self, name: str) -> str:
        if name not in self.user_colors:
            self.user_colors[name] = self.palette[len(self.user_colors) % len(self.palette)]
        return self.user_colors[name]

    async def on_input_submitted(self, event: Input.Submitted):
        text = event.value.strip()
        event.input.value = ""
        if not text or not self.sock:
            return
        # locally echo your own message
        if self.username and not text.startswith("/"):
            col = self._color_for(self.username)
            self.chat_log.append(
                Text.assemble((f"{self.username}: ", f"bold {col}"), (text, "white"))
            )
            self.update_displays()
        try:
            self.sock.sendall(text.encode("utf-8"))
        except:
            self.chat_log.append(Text("Send failed.", style="bold red"))
            self.update_displays()
        if text == MESSAGE_CLOSE:
            self.stop_event.set()
            self.exit()

    def update_displays(self):
        # chat
        t = Text()
        for line in self.chat_log[-200:]:
            t.append(line)
            t.append("\n")
        self.chat_display.update(t)
        # users
        self.users_display.update(Text("\n".join(self.users), style="bold magenta"))

    def on_unmount(self):
        self.stop_event.set()
        if self.sock:
            try: self.sock.sendall(MESSAGE_CLOSE.encode("utf-8"))
            except: pass
            self.sock.close()

if __name__ == "__main__":
    ChatClient().run()
