import serial
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# === Serial Port Settings ===
SERIAL_PORT = 'COM18'  # Change if needed
BAUD_RATE = 9600
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)

# === Figure Setup ===
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 1.5])
ax.set_zlim([-1.5, 1.5])
ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])
ax.set_box_aspect([1, 1, 1])

# === Cube Vertices ===
vertices = np.array([
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Bottom
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Top
])

# === Cube Faces & Colors ===
faces = [
    [vertices[j] for j in [0, 1, 2, 3]],  # Bottom (Z-) - Blue
    [vertices[j] for j in [4, 5, 6, 7]],  # Top (Z+) - Blue
    [vertices[j] for j in [0, 1, 5, 4]],  # Side (Y-) - Green
    [vertices[j] for j in [2, 3, 7, 6]],  # Side (Y+) - Green
    [vertices[j] for j in [0, 3, 7, 4]],  # Side (X-) - Red
    [vertices[j] for j in [1, 2, 6, 5]]   # Side (X+) - Red
]
colors = ['blue', 'blue', 'green', 'green', 'red', 'red']

cube = Poly3DCollection(faces, facecolors=colors, edgecolor='black', alpha=0.6)
ax.add_collection3d(cube)

# === Axes Arrows & Labels ===
arrow_length = 1.5
X_arrow = ax.quiver(0, 0, 0, arrow_length, 0, 0, color='r', linewidth=2)
Y_arrow = ax.quiver(0, 0, 0, 0, arrow_length, 0, color='g', linewidth=2)
Z_arrow = ax.quiver(0, 0, 0, 0, 0, arrow_length, color='b', linewidth=2)

label_positions = np.array([
    [1.8, 0, 0],  # X Label
    [0, 1.8, 0],  # Y Label
    [0, 0, 1.8]   # Z Label
])
labels = [
    ax.text(*label_positions[0], 'X', color='red', fontsize=12, fontweight='bold'),
    ax.text(*label_positions[1], 'Y', color='green', fontsize=12, fontweight='bold'),
    ax.text(*label_positions[2], 'Z', color='blue', fontsize=12, fontweight='bold')
]

# === Roll & Pitch Display ===
roll_text = ax.text2D(0.05, 0.95, "", transform=ax.transAxes, fontsize=12)
pitch_text = ax.text2D(0.05, 0.90, "", transform=ax.transAxes, fontsize=12)

# === Rotation Function ===
def rotate(vertices, roll, pitch):
    roll, pitch = np.radians(roll), np.radians(pitch)

    Rx = np.array([[1, 0, 0], [0, np.cos(roll), -np.sin(roll)], [0, np.sin(roll), np.cos(roll)]])
    Ry = np.array([[np.cos(pitch), 0, np.sin(pitch)], [0, 1, 0], [-np.sin(pitch), 0, np.cos(pitch)]])
    return np.dot(vertices, Ry @ Rx.T)

# === Update Loop ===
plt.ion()
plt.show()

while True:
    try:
        line = ser.readline().decode().strip()
        if line:
            roll, pitch = map(float, line.split(','))

            # Rotate Cube
            rotated_vertices = rotate(vertices, roll, pitch)
            rotated_faces = [[rotated_vertices[j] for j in face] for face in [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [0, 3, 7, 4], [1, 2, 6, 5]]]
            cube.set_verts(rotated_faces)

            # Rotate Arrows
            rotated_axes = rotate(np.array([[arrow_length, 0, 0], [0, arrow_length, 0], [0, 0, arrow_length]]), roll, pitch)
            X_arrow.remove()
            Y_arrow.remove()
            Z_arrow.remove()
            X_arrow = ax.quiver(0, 0, 0, *rotated_axes[0], color='r', linewidth=2)
            Y_arrow = ax.quiver(0, 0, 0, *rotated_axes[1], color='g', linewidth=2)
            Z_arrow = ax.quiver(0, 0, 0, *rotated_axes[2], color='b', linewidth=2)

            # Rotate Labels
            rotated_labels = rotate(label_positions, roll, pitch)
            for i, label in enumerate(labels):
                label.set_position((rotated_labels[i][0], rotated_labels[i][1]))
                label.set_3d_properties(rotated_labels[i][2])

            # Update Roll & Pitch Text
            roll_text.set_text(f"Roll: {roll:.2f}°")
            pitch_text.set_text(f"Pitch: {pitch:.2f}°")

            # Faster Rendering
            fig.canvas.draw_idle()
            fig.canvas.flush_events()

    except KeyboardInterrupt:
        print("Closing serial connection...")
        ser.close()
        break
