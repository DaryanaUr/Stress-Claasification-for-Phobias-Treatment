import serial
import csv
import time
from datetime import datetime
from pylsl import StreamInfo, StreamOutlet
from pynput import keyboard
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# Load the deep learning model
model = load_model('stress_model.h5')

# Serial port configuration
ser = serial.Serial('COM8', 115200)

# LSL Stream Configuration
info = StreamInfo('TriggerStream', 'Markers', 1, 0, 'int32', 'myuidw43536')
outlet = StreamOutlet(info)

# Global variables
current_level = 0
game_in_progress = False
awaiting_response = False
welcome_message_sent = False

# Function to send triggers to Unity
def send_trigger(trigger):
    outlet.push_sample([trigger] if isinstance(trigger, int) else [str(trigger)])
    print(f"Trigger sent: {trigger}")

# Function to send a welcome message and open the game in Unity
def send_welcome_message():
    global welcome_message_sent
    if not welcome_message_sent:
        send_trigger("Welcome")
        time.sleep(10)
        send_trigger("Instructions")
        print("Welcome to your phobias gradual exposure therapy")
        welcome_message_sent = True

# Function to read heart rate and GSR for 10 seconds and return numpy array
def collect_sensor_data(duration=10):
    data = []
    start_time = time.time()
    while time.time() - start_time < duration:
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8').strip()
                parts = line.split(',')
                heart_rate = int(parts[0].split(':')[1])
                gsr = int(parts[1].split(':')[1])
                data.append([heart_rate, gsr])
                print(f"HR: {heart_rate}, GSR: {gsr}")
            except:
                continue
    return np.array(data)

# Function to classify stress level using deep learning model
def classify_stress_dl():
    raw_data = collect_sensor_data(duration=10)
    if len(raw_data) == 0:
        print("No data received.")
        return 2  # default to medium stress

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(raw_data)
    input_data = np.expand_dims(scaled_data, axis=0)  # shape: (1, timesteps, 2)

    prediction = model.predict(input_data)
    stress_class = np.argmax(prediction)

    label = {0: "Low", 1: "Medium", 2: "High"}[stress_class]
    print(f"Predicted stress level: {label}")
    return {0: 3, 1: 2, 2: 1}[stress_class]  # Level 3 = low stress, Level 2 = medium stress, Level 1 = high stres (Unity triggers)

# Level control
def advance_level():
    global awaiting_response
    if current_level == 1:
        print("Starting level 1...")
    elif current_level == 2:
        print("Starting level 2...")
    elif current_level == 3:
        print("Starting level 3...")

    time.sleep(120)
    print("Do you feel more comfortable with this level? (a: yes, b: no)")
    awaiting_response = True

# Keyboard handler
def on_press(key):
    global current_level, game_in_progress, awaiting_response, welcome_message_sent

    try:
        if key.char == '0' and not game_in_progress:
            if welcome_message_sent:
                send_trigger(0)  # remove welcome
                welcome_message_sent = False

            send_trigger(0)  # signal game start
            current_level = classify_stress_dl()
            send_trigger(current_level)

            game_in_progress = True
            advance_level()

        elif key.char == 'a' and game_in_progress and awaiting_response:
            awaiting_response = False
            send_trigger("LevelPassed")
            time.sleep(5)

            if current_level == 1:
                current_level = 2
                send_trigger(2)
            elif current_level == 2:
                current_level = 3
                send_trigger(3)
            elif current_level == 3:
                send_trigger("End")
                print("Congratulations, you completed all levels!")
                send_trigger(0)
                final_data = collect_sensor_data(duration=10)
                print("Final data collected. Game over.")
                game_in_progress = False
                return

            advance_level()

        elif key.char == 'b' and game_in_progress and awaiting_response:
            awaiting_response = False
            print("Level not passed. Try again.")
            send_trigger("Restart")
            advance_level()

    except AttributeError:
        pass

# Game startup
def start_game():
    send_welcome_message()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

start_game()
