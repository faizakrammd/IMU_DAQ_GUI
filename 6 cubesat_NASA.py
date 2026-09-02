import serial
import vedo
import numpy as np

# Load STL model
stl_file = "cubesat.stl"  # Update with your STL file path
cubesat = vedo.Mesh(stl_file).color("cyan").alpha(0.7)

# Serial Configuration
serial_port = "COM18"  # Update with your correct serial port
baud_rate = 9600

# Setup the 3D scene
plotter = vedo.Plotter(title="Real-Time CubeSat Orientation", interactive=False)
plotter.show(cubesat, axes=1, viewup="z")

def read_serial_data():
    """Reads roll and pitch data from the serial port and updates visualization"""
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        print(f"Connected to {ser.port} at {ser.baudrate} baud rate.")

        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                try:
                    roll, pitch = map(float, data.split(','))
                    print(f"Roll: {roll}, Pitch: {pitch}")
                    update_plot(roll, pitch)
                except ValueError:
                    print("Invalid data:", data)

    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

def update_plot(roll, pitch):
    """Applies roll and pitch rotations to the CubeSat"""

    # Reset transformations by applying an identity matrix
    identity_matrix = np.eye(4)  # 4x4 identity matrix
    cubesat.apply_transform(identity_matrix)

    # Apply rotations using .rotate() method
    cubesat.rotate(-roll, axis=(1, 0, 0))  # Roll (X-axis)
    cubesat.rotate(pitch, axis=(0, 1, 0))  # Pitch (Y-axis)

    plotter.show(cubesat, resetcam=False)

# Start serial data reading and visualization
read_serial_data()
