import json

# Load the keylog file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Apply strikethrough to a given character
def strike_through(text):
    return ''.join([char + '\u0336' for char in text])

# Convert keylog JSON data to formatted text
def convert_to_text(data):
    output_text = ""
    typed_text = ""

    for entry in data:
        if 'copied' in entry:
            # Append copied content with special notation
            output_text += f" [copied content: {entry['copied']}]"
        elif 'key' in entry:
            key = entry['key']
            if key == 'Key.space':
                typed_text += ' '
            elif key == 'Key.enter':
                typed_text += '\n'
            elif key == 'Key.backspace':
                # Apply strikethrough to the last character and add to output_text
                if typed_text:
                    struck_text = strike_through(typed_text[-1])  # Strike through last character only
                    output_text += typed_text[:-1] + struck_text  # Add the text with strikethrough applied
                    typed_text = ""  # Clear typed text after applying backspace
            elif key.startswith('Key'):
                # Handle special keys (e.g., ctrl, tab) with brackets
                special_key = key.replace('Key.', '').upper()
                output_text += f" [{special_key}]"
            else:
                typed_text += key  # Add normal character to typed text

        # Add any typed text to output, then clear it
        output_text += typed_text
        typed_text = ""

    return output_text

# Save formatted text to a file
def save_to_file(text, file_path):
    with open(file_path, 'w') as file:
        file.write(text)

# Example usage
log_file = '/home/pavan/.hidden_dir/keylog.json'  # Set the correct path to your JSON log file
output_file = '/home/pavan/output_keylog.txt'      # Set the desired output file path

keylog_data = load_json_data(log_file)
formatted_text = convert_to_text(keylog_data)
save_to_file(formatted_text, output_file)

print(f"Formatted text has been saved to {output_file}")
