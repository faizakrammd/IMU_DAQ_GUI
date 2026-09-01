import serial
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QOpenGLWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import csv
import os

class OpenGLBox(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.roll = 0.0
        self.pitch = 0.0

    def set_angles(self, roll, pitch):
        self.roll = -pitch  # Corrected roll direction
        self.pitch = roll  # Corrected pitch direction
        self.update()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)  # Set background color to white

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 1, 100)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)

        # Apply rotations
        glRotatef(self.roll, 1.0, 0.0, 0.0)
        glRotatef(self.pitch, 0.0, 1.0, 0.0)

        # Draw a drone-like structure
        self.draw_drone()

    def draw_drone(self):
        # Central body
        glBegin(GL_QUADS)
        glColor3f(0.5, 0.5, 0.5)  # Grey color
        glVertex3f(-0.5, -0.1, 0.5)
        glVertex3f(0.5, -0.1, 0.5)
        glVertex3f(0.5, 0.1, 0.5)
        glVertex3f(-0.5, 0.1, 0.5)
        glVertex3f(-0.5, -0.1, -0.5)
        glVertex3f(0.5, -0.1, -0.5)
        glVertex3f(0.5, 0.1, -0.5)
        glVertex3f(-0.5, 0.1, -0.5)
        glEnd()

        # Arms
        glBegin(GL_LINES)
        glColor3f(0.0, 0.0, 0.0)  # Black for arms
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(1.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-1.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(1.0, 0.0, -1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-1.0, 0.0, -1.0)
        glEnd()

        # Propellers
        self.draw_propeller(1.0, 0.0, 1.0)
        self.draw_propeller(-1.0, 0.0, 1.0)
        self.draw_propeller(1.0, 0.0, -1.0)
        self.draw_propeller(-1.0, 0.0, -1.0)

    def draw_propeller(self, x, y, z):
        glPushMatrix()
        glTranslatef(x, y + 0.1, z)
        glColor3f(0.0, 0.0, 1.0)  # Blue for propellers
        glBegin(GL_TRIANGLES)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-0.3, 0.0, 0.1)
        glVertex3f(0.3, 0.0, 0.1)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-0.3, 0.0, -0.1)
        glVertex3f(0.3, 0.0, -0.1)
        glEnd()
        glPopMatrix()

class SerialMonitor(QWidget):
    def __init__(self):
        super().__init__()

        # Serial setup
        self.ser = serial.Serial('COM18', 9600, timeout=0)  # Set timeout to 0 for non-blocking reads

        # GUI setup
        self.setWindowTitle("Roll and Pitch Viewer")
        self.setGeometry(100, 100, 1200, 800)

        self.layout = QGridLayout()
        self.roll_label = QLabel("Roll: N/A", self)
        self.pitch_label = QLabel("Pitch: N/A", self)
        self.opengl_widget = OpenGLBox()

        # Set OpenGL widget sizes explicitly
        self.opengl_widget.setMinimumHeight(380)
        self.opengl_widget.setMaximumHeight(380)

        # Graph setup
        self.roll_series = QLineSeries()
        self.pitch_series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.roll_series)
        self.chart.addSeries(self.pitch_series)

        # Configure axes
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        self.axisX.setTitleText("Time (points)")
        self.axisY.setTitleText("Value")
        self.chart.setAxisX(self.axisX, self.roll_series)
        self.chart.setAxisX(self.axisX, self.pitch_series)
        self.chart.setAxisY(self.axisY, self.roll_series)
        self.chart.setAxisY(self.axisY, self.pitch_series)

        self.chart.setTitle("Roll and Pitch over Time")
        self.chart_view = QChartView(self.chart)
        self.chart_view.setMinimumSize(600, 300)

        # CSV save button
        self.save_button = QPushButton("Save Data to CSV", self)
        self.save_button.clicked.connect(self.save_to_csv)

        # Add widgets to layout
        self.layout.addWidget(self.roll_label, 0, 0)
        self.layout.addWidget(self.pitch_label, 0, 1)
        self.layout.addWidget(self.opengl_widget, 1, 0, 1, 2)
        self.layout.addWidget(self.chart_view, 2, 0, 1, 2)
        self.layout.addWidget(self.save_button, 3, 0, 1, 2)

        self.setLayout(self.layout)

        # Timer for updating data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(10)  # Reduce the timer interval to 10 ms for faster updates

        # Data storage
        self.data = []
        self.max_points = 50  # Keep only the most recent 50 points in the graph

    def update_data(self):
        while self.ser.in_waiting > 0:  # Read all available data
            data = self.ser.readline().decode('utf-8').strip()
            if "," in data:  # Expecting data in "roll,pitch" format
                try:
                    roll, pitch = map(float, data.split(","))
                    self.roll_label.setText(f"Roll: {roll:.2f}")
                    self.pitch_label.setText(f"Pitch: {pitch:.2f}")
                    self.opengl_widget.set_angles(roll, pitch)

                    # Add data to chart
                    self.roll_series.append(len(self.data), roll)
                    self.pitch_series.append(len(self.data), pitch)

                    # Keep graph data within the last max_points
                    if self.roll_series.count() > self.max_points:
                        self.roll_series.remove(0)
                        self.pitch_series.remove(0)

                    # Update axes range dynamically
                    self.axisX.setRange(max(0, len(self.data) - self.max_points), len(self.data))
                    self.axisY.setRange(-180, 180)  # Assuming typical IMU ranges

                    # Store data
                    timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
                    self.data.append((timestamp, roll, pitch))
                except ValueError:
                    print(f"Invalid data format: {data}")

    def save_to_csv(self):
        filename = QDateTime.currentDateTime().toString("ddMMMYYHHmm'.csv'")
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Time", "Roll", "Pitch"])
            csvwriter.writerows(self.data)
        print(f"Data saved to {filepath}")

    def closeEvent(self, event):
        if self.ser.is_open:
            self.ser.close()
        event.accept()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SerialMonitor()
    window.show()
    sys.exit(app.exec_())
