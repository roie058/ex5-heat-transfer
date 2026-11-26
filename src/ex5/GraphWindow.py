
import os
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QComboBox,
    QPushButton,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class GraphWindow(QWidget):

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setupUI()

    def setupUI(self):
        self.setObjectName("GraphWindow")
        self.setWindowTitle("Graph Window")
        self.setGeometry(820, 120, 680, 440)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # ----- Left side: Matplotlib graph inside a card -----
        graph_card = QFrame()
        graph_card.setObjectName("stage_card")
        graph_layout = QVBoxLayout()
        graph_layout.setContentsMargins(12, 12, 12, 12)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor("#ffffff")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.configure_axes()

        graph_layout.addWidget(self.canvas)
        graph_card.setLayout(graph_layout)

        # ----- Right side: Controls panel -----
        controls_card = QFrame()
        controls_card.setObjectName("controls_card")
        controls_card.setFixedWidth(180)
        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(14, 16, 14, 16)
        controls_layout.setSpacing(12)

        self.body_selector = QComboBox()
        self.body_selector.addItems(["Body 1", "Body 2"])

        self.draw_button = QPushButton("Draw")
        self.draw_button.setObjectName("graphs_button")
        self.draw_button.clicked.connect(self.draw_graph)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_graph)

        self.export_csv_button = QPushButton("Export to CSV")
        self.export_csv_button.clicked.connect(self.export_to_csv)

        controls_layout.addWidget(self.body_selector)
        controls_layout.addWidget(self.draw_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addWidget(self.export_csv_button)
        controls_layout.addStretch()
        controls_card.setLayout(controls_layout)

        main_layout.addWidget(graph_card, 1)
        main_layout.addWidget(controls_card)
        self.setLayout(main_layout)

    def draw_graph(self):
        if self.main_window is None or len(self.main_window.time_history) == 0:
            return
        selected = self.body_selector.currentText()
        if selected == 'Body 1':
            self.ax.plot(self.main_window.time_history, self.main_window.body1_temp_history,color='#dc2626', label="Body 1", linewidth=2)

        else:
            self.ax.plot(self.main_window.time_history, self.main_window.body2_temp_history,color='#2563eb', label="Body 2", linewidth=2)
        self.ax.legend(fontsize=10)
        self.figure.tight_layout()
        self.canvas.draw()
        
    def clear_graph(self):
        self.ax.clear()
        self.configure_axes()
        self.canvas.draw()
    
    def export_to_csv(self):
        if self.main_window is None or len(self.main_window.time_history) == 0:
            return
        with open("heat_transfer_data.csv", "w") as f:
            f.write("Time (s),Body 1 Temperature (C),Body 2 Temperature (C)\n")
            for i in range(len(self.main_window.time_history)):
                f.write(f"{self.main_window.time_history[i]},{self.main_window.body1_temp_history[i]},{self.main_window.body2_temp_history[i]}\n")
        os.startfile("heat_transfer_data.csv")
    def configure_axes(self):
        self.ax.set_xlabel("Time (s)", fontsize=12)
        self.ax.set_ylabel("Temperature (°C)", fontsize=12)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.grid(True, linestyle="--", alpha=0.35)
        self.figure.tight_layout()


if __name__ == "__main__":
    app = QApplication()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(current_dir, "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())

    window = GraphWindow()
    window.show()
    app.exec()
