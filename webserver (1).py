from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json

# Try to import SenseHat. If it fails (not on a Pi / SenseHAT missing),
# the server will still run, but it won't update physical LEDs.
try:
    from sense_hat import SenseHat
    sense = SenseHat()
    HAS_SENSEHAT = True
except Exception:
    sense = None
    HAS_SENSEHAT = False

# Store the 8x8 LED colors as a flat list of 64 RGB triplets.
# Each entry is [R, G, B] with values 0..255.
# Start all LEDs off (black).
colors = [[0, 0, 0] for _ in range(64)]

# Create the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# Create the SocketIO wrapper (eventlet is fine if installed; otherwise it will fallback)
socketio = SocketIO(app)

# Converts a RGB color expressed in HEX to RGB list.
# Example: "#ff00aa" -> [255, 0, 170]
def hex_to_rgb_color(color: str):
    color = color.strip('#')
    rgb = [int(color[i:i+2], 16) for i in (0, 2, 4)]
    return rgb

# The webpage uses LED ids 0..63. Map that index to (x, y) coordinates (0..7, 0..7).
# With id = y*8 + x, we recover x = id % 8 and y = id // 8.
def map_index_to_xy(led_index: int):
    return int(led_index % 8), int(led_index / 8)

# Main page route: serves templates/Lab3-Colour-Picker.html
@app.route('/')
def index():
    return render_template('Lab3-Colour-Picker.html')

# When a client connects, send the current full LED grid so their webpage initializes correctly.
@socketio.on('connect')
def send_led_colors():
    packet = json.dumps(dict(colors=colors))
    print(f"sending colors.. {packet}")
    emit('current_colors', packet)

# When the user drags/clicks on a square, the webpage sends:
# socket.emit('update_led', JSON.stringify({ 'id': <0..63>, 'color': '#RRGGBB' }))
# We must:
#  1) update internal colors[]
#  2) update the physical SenseHAT pixel
#  3) broadcast the update to all connected clients
@socketio.on('update_led')
def update_led_color(data):
    try:
        data = json.loads(data)
        led_id = int(data['id'])
        hex_color = data['color']

        # Basic validation
        if led_id < 0 or led_id >= 64:
            return

        # Update internal array
        color_rgb = hex_to_rgb_color(hex_color)
        colors[led_id] = color_rgb

        # Update physical SenseHAT
        if HAS_SENSEHAT:
            x, y = map_index_to_xy(led_id)
            sense.set_pixel(x, y, color_rgb)

        # Broadcast to all clients so every browser stays in sync
        emit(
            'update_led',
            json.dumps(dict(id=str(led_id), color=hex_color)),
            broadcast=True
        )

    except Exception as e:
        print(f"update_led error: {e}")

# The Clear LEDs button on your HTML sends:
# socket.emit('clear_leds')
# We must clear the internal array AND the physical SenseHAT,
# then broadcast the full cleared grid so all browsers reset to black.
@socketio.on('clear_leds')
def clear_leds():
    global colors

    # Clear internal state
    colors = [[0, 0, 0] for _ in range(64)]

    # Clear physical SenseHAT
    if HAS_SENSEHAT:
        sense.clear()

    # Broadcast full cleared grid (clients already know how to handle 'current_colors')
    emit('current_colors', json.dumps(dict(colors=colors)), broadcast=True)

if __name__ == '__main__':
    # Run on all interfaces so laptop/phone on same network can reach it.
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)