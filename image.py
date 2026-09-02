from graphviz import Digraph

def create_block_diagram():
    dot = Digraph(format='png')
    
    # Nodes
    dot.node('A', 'Summation (Σ)\nError Detector', shape='parallelogram')
    dot.node('B', 'PID Controller\n(P + I + D)', shape='box')
    dot.node('C', 'BLDC Motor\n(Actuator)', shape='box')
    dot.node('D', 'Roll Plate\n(System Output)', shape='box')
    dot.node('E', 'MPU6050 IMU\n(Feedback Sensor)', shape='box')
    
    # Edges (Connections)
    dot.edge('A', 'B', label='Error Signal')
    dot.edge('B', 'C', label='Actuating Signal')
    dot.edge('C', 'D', label='Torque Output')
    dot.edge('D', 'E', label='Measured Roll Angle')
    dot.edge('E', 'A', label='Feedback Signal')
    
    return dot

# Generate the diagram
block_diagram = create_block_diagram()
block_diagram.render('self_stabilizing_pid')
