import time
import json

# Load the keylog file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Simulate typing with delays and handling special keys
def simulate_typing(data):
    for entry in data:
        if 'key' in entry:
            key = entry['key']
            if key == 'Key.space':
                print(' ', end='', flush=True)
            elif key == 'Key.enter':
                print('\n', end='', flush=True)
            elif key == 'Key.backspace':
                print('\b \b', end='', flush=True)  # Simulate backspace
            elif key.startswith('Key'):
                # Handle other special keys, like tab, shift, etc.
                if key == 'Key.tab':
                    print('\t', end='', flush=True)
                else:
                    continue
            else:
                print(key, end='', flush=True)
        time.sleep(0.1)  # Adjust delay for a more human-like typing speed

# Example usage
log_file = '/home/pavan/.hidden_dir/keylog.json'  # Set the correct path to your JSON log file
keylog_data = load_json_data(log_file)
simulate_typing(keylog_data)
