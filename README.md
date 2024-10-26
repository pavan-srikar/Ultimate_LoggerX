# Keylogger with Clipboard and Telegram Bot Integration

This project is a **cross-platform keylogger** that tracks keystrokes, clipboard content, and logs events in a hidden JSON file. The JSON file can be retrieved or reset via a Telegram bot. This tool is intended for **educational purposes only**, allowing cybersecurity professionals to test keylogging detection capabilities on antivirus software.

## Features

- **Keystroke Logging**: Tracks keystrokes with real-time logging and timestamps.
- **Clipboard Monitoring**: Logs clipboard content when it changes.
- **Caps Lock Detection**: Detects Caps Lock status for accurate character capture.
- **Telegram Bot Control**: Interact with the tool using a Telegram bot to:
  - `/get` - Download the JSON file with logs.
  - `/clear` - Reset the JSON log file (a new file is created automatically).

> ⚠ **Warning**: This tool is designed strictly for testing and educational purposes. Unauthorized use of this tool may violate privacy and legal policies in various regions. Use only with permission on devices you own or are authorized to test on.

---

## Setup Instructions

### Prerequisites

Install Python (3.7+) and ensure `pip` is available for package installations.

### Required Packages

Install necessary packages via `pip`:
```bash
pip install os json pyperclip pynput platform python-telegram-bot