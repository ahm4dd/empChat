[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Textual](https://img.shields.io/badge/UI-Textual-9cf?logo=python)](https://github.com/Textualize/textual)

A terminal-based real-time chat application built using Python's `socket`, `threading`, and [Textual](https://github.com/Textualize/textual). Think of it as your own IRC-style chat system (Not exactly an IRC client), running locally.

## Video on how to use:


https://github.com/user-attachments/assets/48d22a11-26b6-467c-8e0f-cb5bd8e50859



---

## ✅ Features

- Live chat between multiple clients
- User-specific color-coded messages
- Real-time join/leave detection
- TUI interface with Rich + Textual
- Command support: `/help`, `/users`, `/nick`, `/close`

---

## 🐍 Requirements

### Python version:

```bash
Python 3.10 or higher
```

### Dependencies:
> Install using pip:
```bash
pip install textual rich
```

## 🚀 Running the App
1. Start the server:
```bash
python server.py
```

2. In another terminal, start the client:
```bash
python client.py
```
Open more client terminals to simulate multiple users.

## 💬 Commands

| Command            | Description                          | Example                |
|--------------------|--------------------------------------|------------------------|
| `/help`            | Show all available commands          | `/help`                |
| `/users`           | Show number of connected users       | `/users`               |
| `/nick <newname>`  | Change your username                 | `/nick coolguy123`     |
| `/close`           | Disconnect from the server gracefully| `/close`               |


## 📦 Future Plans
- Persistent chat history

- Private messaging

- Channel/room support

📜 License
> MIT License. Feel free to use, modify, and share.

