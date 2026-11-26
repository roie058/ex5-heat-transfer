import os
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QSlider,
    QDoubleSpinBox,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
)
from PySide6.QtCore import Qt
from About import AboutWindow


class HeatTransfer(QWidget):

    def __init__(self):
        super().__init__()
        self.about_window = AboutWindow()
        # Graph window will be added in the next step of Stage 2
        # Simulation variables and QTimer will be added in Stage 3
        self.setupUI()

    def setupUI(self):
        self.setObjectName("HeatTransferWindow")
        self.setWindowTitle("Heat Transfer")
        self.setGeometry(120, 120, 680, 440)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        # ----- Top visual stage: sliders, two thermal bodies, and conductivity bridge -----
        stage_card = QFrame()
        stage_card.setObjectName("stage_card")
        stage_layout = QHBoxLayout()
        stage_layout.setContentsMargins(20, 20, 20, 20)
        stage_layout.setSpacing(14)

        # Left slider (Body 1 temperature: 0 to 200 °C)
        self.left_temp_slider = QSlider(Qt.Orientation.Vertical)
        self.left_temp_slider.setRange(0, 200)
        self.left_temp_slider.setValue(200)
        self.left_temp_slider.setFixedHeight(170)

        # Left body visual block
        self.left_body_label = QLabel()
        self.left_body_label.setFixedSize(130, 170)
        self.left_body_label.setStyleSheet(
            "background-color: rgb(255, 0, 0); border: 2px solid #94a3b8; border-radius: 10px;"
        )

        # Center bridge + conductivity input
        bridge_layout = QVBoxLayout()
        bridge_layout.setSpacing(8)
        bridge_layout.addStretch()

        conductivity_label = QLabel("Conductivity")
        conductivity_label.setObjectName("conductivity_title")
        conductivity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.conductivity_spinbox = QDoubleSpinBox()
        self.conductivity_spinbox.setRange(0.01, 1000.0)
        self.conductivity_spinbox.setDecimals(2)
        self.conductivity_spinbox.setSingleStep(0.1)
        self.conductivity_spinbox.setValue(1.00)
        self.conductivity_spinbox.setSuffix(" J/s°C")
        self.conductivity_spinbox.setFixedWidth(135)

        self.thermal_bridge_label = QLabel()
        self.thermal_bridge_label.setObjectName("thermal_bridge")
        self.thermal_bridge_label.setFixedHeight(26)

        bridge_layout.addWidget(conductivity_label)
        bridge_layout.addWidget(self.conductivity_spinbox, alignment=Qt.AlignmentFlag.AlignCenter)
        bridge_layout.addSpacing(4)
        bridge_layout.addWidget(self.thermal_bridge_label)
        bridge_layout.addStretch()

        # Right body visual block
        self.right_body_label = QLabel()
        self.right_body_label.setFixedSize(130, 170)
        self.right_body_label.setStyleSheet(
            "background-color: rgb(0, 0, 0); border: 2px solid #94a3b8; border-radius: 10px;"
        )

        # Right slider (Body 2 temperature: 0 to 200 °C)
        self.right_temp_slider = QSlider(Qt.Orientation.Vertical)
        self.right_temp_slider.setRange(0, 200)
        self.right_temp_slider.setValue(0)
        self.right_temp_slider.setFixedHeight(170)

        stage_layout.addWidget(self.left_temp_slider)
        stage_layout.addWidget(self.left_body_label)
        stage_layout.addLayout(bridge_layout, 1)
        stage_layout.addWidget(self.right_body_label)
        stage_layout.addWidget(self.right_temp_slider)
        stage_card.setLayout(stage_layout)

        # ----- Bottom controls: Body 1 parameters | Action buttons | Body 2 parameters -----
        controls_card = QFrame()
        controls_card.setObjectName("controls_card")
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(20, 16, 20, 16)
        controls_layout.setSpacing(20)

        # Left body controls
        left_grid = QGridLayout()
        left_grid.setHorizontalSpacing(10)
        left_grid.setVerticalSpacing(10)

        left_title = QLabel("Body 1")
        left_title.setObjectName("section_title")
        left_grid.addWidget(left_title, 0, 0, 1, 2)

        self.left_temp_display = QDoubleSpinBox()
        self.left_temp_display.setRange(0.0, 200.0)
        self.left_temp_display.setDecimals(1)
        self.left_temp_display.setValue(200.0)
        self.left_temp_display.setSuffix(" °C")
        self.left_temp_display.setReadOnly(True)
        self.left_temp_display.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)

        self.left_mass_spinbox = QDoubleSpinBox()
        self.left_mass_spinbox.setRange(0.01, 10000.0)
        self.left_mass_spinbox.setDecimals(2)
        self.left_mass_spinbox.setSingleStep(1.0)
        self.left_mass_spinbox.setValue(10.00)
        self.left_mass_spinbox.setSuffix(" kg")

        self.left_heat_capacity_spinbox = QDoubleSpinBox()
        self.left_heat_capacity_spinbox.setRange(0.01, 10000.0)
        self.left_heat_capacity_spinbox.setDecimals(2)
        self.left_heat_capacity_spinbox.setSingleStep(0.1)
        self.left_heat_capacity_spinbox.setValue(0.40)
        self.left_heat_capacity_spinbox.setSuffix(" J/kg°C")

        left_grid.addWidget(QLabel("Temp."), 1, 0)
        left_grid.addWidget(self.left_temp_display, 1, 1)
        left_grid.addWidget(QLabel("Mass"), 2, 0)
        left_grid.addWidget(self.left_mass_spinbox, 2, 1)
        left_grid.addWidget(QLabel("H. Cap."), 3, 0)
        left_grid.addWidget(self.left_heat_capacity_spinbox, 3, 1)

        # Center action buttons
        center_buttons_layout = QVBoxLayout()
        center_buttons_layout.setSpacing(10)
        center_buttons_layout.addStretch()

        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.setObjectName("start_stop_button")
        self.start_stop_button.setCheckable(True)
        self.start_stop_button.setFixedWidth(130)

        self.graphs_button = QPushButton("Graphs")
        self.graphs_button.setObjectName("graphs_button")
        self.graphs_button.setFixedWidth(130)

        self.about_button = QPushButton("About")
        self.about_button.setFixedWidth(130)
        self.about_button.clicked.connect(self.open_about_window)

        center_buttons_layout.addWidget(self.start_stop_button, alignment=Qt.AlignmentFlag.AlignCenter)
        center_buttons_layout.addWidget(self.graphs_button, alignment=Qt.AlignmentFlag.AlignCenter)
        center_buttons_layout.addWidget(self.about_button, alignment=Qt.AlignmentFlag.AlignCenter)
        center_buttons_layout.addStretch()

        # Right body controls
        right_grid = QGridLayout()
        right_grid.setHorizontalSpacing(10)
        right_grid.setVerticalSpacing(10)

        right_title = QLabel("Body 2")
        right_title.setObjectName("section_title")
        right_grid.addWidget(right_title, 0, 0, 1, 2)

        self.right_temp_display = QDoubleSpinBox()
        self.right_temp_display.setRange(0.0, 200.0)
        self.right_temp_display.setDecimals(1)
        self.right_temp_display.setValue(0.0)
        self.right_temp_display.setSuffix(" °C")
        self.right_temp_display.setReadOnly(True)
        self.right_temp_display.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)

        self.right_mass_spinbox = QDoubleSpinBox()
        self.right_mass_spinbox.setRange(0.01, 10000.0)
        self.right_mass_spinbox.setDecimals(2)
        self.right_mass_spinbox.setSingleStep(1.0)
        self.right_mass_spinbox.setValue(10.00)
        self.right_mass_spinbox.setSuffix(" kg")

        self.right_heat_capacity_spinbox = QDoubleSpinBox()
        self.right_heat_capacity_spinbox.setRange(0.01, 10000.0)
        self.right_heat_capacity_spinbox.setDecimals(2)
        self.right_heat_capacity_spinbox.setSingleStep(0.1)
        self.right_heat_capacity_spinbox.setValue(0.40)
        self.right_heat_capacity_spinbox.setSuffix(" J/kg°C")

        right_grid.addWidget(self.right_temp_display, 1, 0)
        right_grid.addWidget(QLabel("Temp."), 1, 1)
        right_grid.addWidget(self.right_mass_spinbox, 2, 0)
        right_grid.addWidget(QLabel("Mass"), 2, 1)
        right_grid.addWidget(self.right_heat_capacity_spinbox, 3, 0)
        right_grid.addWidget(QLabel("H. Cap."), 3, 1)

        controls_layout.addLayout(left_grid, 1)
        controls_layout.addLayout(center_buttons_layout)
        controls_layout.addLayout(right_grid, 1)
        controls_card.setLayout(controls_layout)

        main_layout.addWidget(stage_card)
        main_layout.addWidget(controls_card)
        self.setLayout(main_layout)

    def open_about_window(self):
        self.about_window.show()

    def closeEvent(self, event):
        self.about_window.close()


if __name__ == "__main__":
    app = QApplication()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(current_dir, "style.qss")
    with open(style_path, "r") as f:
        app.setStyleSheet(f.read())

    window = HeatTransfer()
    window.show()
    app.exec()
