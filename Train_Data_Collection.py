import serial
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import os
import signal

#### Code for data collection ####

# Serial Port, in my case COM8 
ser = serial.Serial('COM8', 115200) 

# Verification
try:
    line = ser.readline().decode('utf-8').strip()
    if line:
        print("Comunicación serial correcta")
except ValueError:
    print("Invalid data received")

# Wait to continue with CSV file generating
input("Enter to start CSV file generating")

# Function to get user information and generate the CSV file name
def get_csv_filename():
    while True:
        subject_name = input("Subject name: ").strip()
        predisposition = input("Select the subject's predisposition: 1-HS 2-MS 3-LS:").strip()
        
        if predisposition == '1':
            predisposition_str = 'HS'
        elif predisposition == '2':
            predisposition_str = 'MS'
        elif predisposition == '3':
            predisposition_str = 'LS'
        else:
            print("Invalid input for predisposition. Please try again.")
            continue
        
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'{subject_name}_{predisposition_str}_{timestamp_str}.csv'
        print(f"CSV file generated: {csv_filename}")
        
        start_test = input("Start test y/n: ").strip().lower()
        if start_test == 'y':
            return csv_filename
        elif start_test == 'n':
            print("Returning to data entry...")
        else:
            print("Invalid input. Returning to data entry...")

# Generate CSV file name
csv_file = get_csv_filename()
columns = ['Timestamp', 'Heart Rate', 'Galvanic Skin Response', 'Event']
df = pd.DataFrame(columns=columns)

event_counter = 0

# Function to update the CSV
def update_csv(timestamp, heart_rate, gsr, event):
    global df
    new_data = pd.DataFrame({'Timestamp': [timestamp], 'Heart Rate': [heart_rate], 'Galvanic Skin Response': [gsr], 'Event': [event]})
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(csv_file, index=False)

# Setting up real-time graphics
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.subplots_adjust(hspace=0.2)  # Increase space between graphics

xs = []
ys1 = []
ys2 = []

# # Function to update the graphs
def animate(i, xs, ys1, ys2):
    line = ser.readline().decode('utf-8').strip()
    if line:
        try:
            heart_rate, gsr = map(float, line.split(','))
            timestamp = datetime.now()
            update_csv(timestamp.strftime('%Y-%m-%d %H:%M:%S'), heart_rate, gsr, event_counter)

            # Keep only the seconds for the graph
            xs.append(timestamp.strftime('%S'))
            ys1.append(heart_rate)
            ys2.append(gsr)

            xs = xs[-20:]
            ys1 = ys1[-20:]
            ys2 = ys2[-20:]

            ax1.clear()
            ax2.clear()

            ax1.plot(xs, ys1, label='Heart Rate')
            ax2.plot(xs, ys2, label='Galvanic Skin Response')

            ax1.set_title('Heart Rate over Time')
            ax2.set_title('Galvanic Skin Response over Time')

            plt.xticks(rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.10)

            ax1.legend(loc='upper right')
            ax2.legend(loc='upper right')
        except ValueError:
            print("Invalid data received")

# Function to close the program by pressing 'ESC'
def on_key(event):
    global event_counter
    if event.key == 'escape':
        plt.close(fig)
        ser.close()
        os.kill(os.getpid(), signal.SIGINT)
    elif event.key == ' ':
        event_counter += 1
        print("Event")

fig.canvas.mpl_connect('key_press_event', on_key)

ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys1, ys2), interval=100)
plt.show()
