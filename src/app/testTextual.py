from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Header, Button, Digits

class TimeDisplay(Digits):
    pass
class Stopwatch(HorizontalGroup):
    def compose(self):
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")


class StopwatchApp(App):
    
    CSS_PATH = "chat_client.css"
    BINDINGS = [('d', 'toggle_dark', 'Toggle dark mode')]

    def compose(self) -> ComposeResult:
        """ Create widgets """
        yield Header(show_clock=True, name="Watch")
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())
    
if __name__ == "__main__":
    app = StopwatchApp()
    app.run()