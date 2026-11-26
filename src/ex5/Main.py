import os
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QSlider,
    QDoubleSpinBox,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
)
from PySide6.QtCore import Qt, QTimer

from About import AboutWindow
from GraphWindow import GraphWindow
from Body import Body


class HeatTransfer(QWidget):

    def __init__(self):
        super().__init__()
        self.about_window = AboutWindow()
        self.graph_window = GraphWindow(self)

        self.elapsed_time = 0.0
        self.time_history = []
        self.body1_temp_history = []
        self.body2_temp_history = []
        self.arrow_frame = 0
        self.speed = 1.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_method)
        self.dt = 0.05

        self.setupUI()

    def setupUI(self):
        self.setObjectName("HeatTransferWindow")
        self.setWindowTitle("Heat Transfer")
        self.setGeometry(120, 120, 720, 505)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 16, 20, 20)
        main_layout.setSpacing(14)

        # ----- Compact top header row: title + speed + status pill + elapsed clock -----
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        app_title = QLabel("Heat Transfer Simulator")
        app_title.setObjectName("app_title")

        speed_label = QLabel("Speed")
        speed_label.setObjectName("speed_label")

        self.speed_combo = QComboBox()
        self.speed_combo.setObjectName("speed_combo")
        self.speed_combo.addItems(["0.5x", "1x", "2x", "5x", "10x"])
        self.speed_combo.setCurrentText("1x")
        self.speed_combo.setFixedWidth(68)
        self.speed_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.speed_combo.currentTextChanged.connect(self.speed_changed)

        self.status_pill = QLabel("● Idle")
        self.status_pill.setObjectName("status_pill_idle")

        self.clock_label = QLabel("0.00 s")
        self.clock_label.setObjectName("clock_label")

        header_layout.addWidget(app_title)
        header_layout.addStretch()
        header_layout.addWidget(speed_label)
        header_layout.addWidget(self.speed_combo)
        header_layout.addSpacing(4)
        header_layout.addWidget(self.status_pill)
        header_layout.addWidget(self.clock_label)
        main_layout.addLayout(header_layout)

        # ----- Top visual stage: sliders, two thermal bodies, and conductivity bridge -----
        stage_card = QFrame()
        stage_card.setObjectName("stage_card")
        stage_layout = QHBoxLayout()
        stage_layout.setContentsMargins(22, 22, 22, 22)
        stage_layout.setSpacing(14)

        # Left slider (Body 1 temperature: 0 to 200 °C)
        self.left_temp_slider = QSlider(Qt.Orientation.Vertical)
        self.left_temp_slider.setRange(0, 200)
        self.left_temp_slider.setValue(200)
        self.left_temp_slider.setFixedSize(26, 170)
        self.left_temp_slider.valueChanged.connect(self.left_temp_changed)

        # Left body visual block
        self.left_body_label = QLabel()
        self.left_body_label.setFixedSize(140, 170)
        self.left_body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_body_visual(self.left_body_label, "Body 1", 200.0)

        # Center bridge + conductivity input + live heat-flux readout
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
        self.conductivity_spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)
        self.conductivity_spinbox.setFixedWidth(140)
        self.conductivity_spinbox.valueChanged.connect(self.conductivity_changed)

        self.thermal_bridge_label = QLabel()
        self.thermal_bridge_label.setFixedHeight(30)
        self.thermal_bridge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.flux_label = QLabel("200.0 W")
        self.flux_label.setObjectName("flux_label")
        self.flux_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bridge_layout.addWidget(conductivity_label)
        bridge_layout.addWidget(self.conductivity_spinbox, alignment=Qt.AlignmentFlag.AlignCenter)
        bridge_layout.addSpacing(2)
        bridge_layout.addWidget(self.thermal_bridge_label)
        bridge_layout.addWidget(self.flux_label, alignment=Qt.AlignmentFlag.AlignCenter)
        bridge_layout.addStretch()

        # Right body visual block
        self.right_body_label = QLabel()
        self.right_body_label.setFixedSize(140, 170)
        self.right_body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_body_visual(self.right_body_label, "Body 2", 0.0)

        # Right slider (Body 2 temperature: 0 to 200 °C)
        self.right_temp_slider = QSlider(Qt.Orientation.Vertical)
        self.right_temp_slider.setRange(0, 200)
        self.right_temp_slider.setValue(0)
        self.right_temp_slider.setFixedSize(26, 170)
        self.right_temp_slider.valueChanged.connect(self.right_temp_changed)

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
        controls_layout.setContentsMargins(20, 18, 20, 18)
        controls_layout.setSpacing(20)

        # Left body controls
        left_grid = QGridLayout()
        left_grid.setHorizontalSpacing(10)
        left_grid.setVerticalSpacing(10)
        left_grid.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        left_title = QLabel("Body 1")
        left_title.setObjectName("section_title")
        left_grid.addWidget(left_title, 0, 0, 1, 2)

        self.left_temp_display = QDoubleSpinBox()
        self.left_temp_display.setRange(0.0, 200.0)
        self.left_temp_display.setDecimals(1)
        self.left_temp_display.setValue(200.0)
        self.left_temp_display.setSuffix(" °C")
        self.left_temp_display.setReadOnly(True)

        self.left_mass_spinbox = QDoubleSpinBox()
        self.left_mass_spinbox.setRange(0.01, 10000.0)
        self.left_mass_spinbox.setDecimals(2)
        self.left_mass_spinbox.setSingleStep(1.0)
        self.left_mass_spinbox.setValue(10.00)
        self.left_mass_spinbox.setSuffix(" kg")
        self.left_mass_spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)

        self.left_heat_capacity_spinbox = QDoubleSpinBox()
        self.left_heat_capacity_spinbox.setRange(0.01, 10000.0)
        self.left_heat_capacity_spinbox.setDecimals(2)
        self.left_heat_capacity_spinbox.setSingleStep(0.1)
        self.left_heat_capacity_spinbox.setValue(0.40)
        self.left_heat_capacity_spinbox.setSuffix(" J/kg°C")
        self.left_heat_capacity_spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)

        left_grid.addWidget(QLabel("Temp."), 1, 0)
        left_grid.addWidget(self.left_temp_display, 1, 1)
        left_grid.addWidget(QLabel("Mass"), 2, 0)
        left_grid.addWidget(self.left_mass_spinbox, 2, 1)
        left_grid.addWidget(QLabel("H. Cap."), 3, 0)
        left_grid.addWidget(self.left_heat_capacity_spinbox, 3, 1)

        # Center action buttons
        center_buttons_layout = QVBoxLayout()
        center_buttons_layout.setSpacing(8)
        center_buttons_layout.addStretch()

        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.setObjectName("start_stop_button")
        self.start_stop_button.setCheckable(True)
        self.start_stop_button.setFixedWidth(130)
        self.start_stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_stop_button.clicked.connect(self.start_stop_button_method)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.setFixedWidth(130)
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_button.clicked.connect(self.reset_simulation)

        self.graphs_button = QPushButton("Graphs")
        self.graphs_button.setObjectName("graphs_button")
        self.graphs_button.setFixedWidth(130)
        self.graphs_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.graphs_button.clicked.connect(self.open_graph_window)

        self.about_button = QPushButton("About")
        self.about_button.setFixedWidth(130)
        self.about_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.about_button.clicked.connect(self.open_about_window)

        center_buttons_layout.addWidget(self.start_stop_button, alignment=Qt.AlignmentFlag.AlignCenter)
        center_buttons_layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignCenter)
        center_buttons_layout.addWidget(self.graphs_button, alignment=Qt.AlignmentFlag.AlignCenter)
        center_buttons_layout.addWidget(self.about_button, alignment=Qt.AlignmentFlag.AlignCenter)
        center_buttons_layout.addStretch()

        # Right body controls
        right_grid = QGridLayout()
        right_grid.setHorizontalSpacing(10)
        right_grid.setVerticalSpacing(10)
        right_grid.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        right_title = QLabel("Body 2")
        right_title.setObjectName("section_title")
        right_grid.addWidget(right_title, 0, 0, 1, 2)

        self.right_temp_display = QDoubleSpinBox()
        self.right_temp_display.setRange(0.0, 200.0)
        self.right_temp_display.setDecimals(1)
        self.right_temp_display.setValue(0.0)
        self.right_temp_display.setSuffix(" °C")
        self.right_temp_display.setReadOnly(True)

        self.right_mass_spinbox = QDoubleSpinBox()
        self.right_mass_spinbox.setRange(0.01, 10000.0)
        self.right_mass_spinbox.setDecimals(2)
        self.right_mass_spinbox.setSingleStep(1.0)
        self.right_mass_spinbox.setValue(10.00)
        self.right_mass_spinbox.setSuffix(" kg")
        self.right_mass_spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)

        self.right_heat_capacity_spinbox = QDoubleSpinBox()
        self.right_heat_capacity_spinbox.setRange(0.01, 10000.0)
        self.right_heat_capacity_spinbox.setDecimals(2)
        self.right_heat_capacity_spinbox.setSingleStep(0.1)
        self.right_heat_capacity_spinbox.setValue(0.40)
        self.right_heat_capacity_spinbox.setSuffix(" J/kg°C")
        self.right_heat_capacity_spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)

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
        self.update_thermal_bridge(200.0, 0.0)

    def set_status_pill(self, text, style_name):
        self.status_pill.setText(text)
        self.status_pill.setObjectName(style_name)
        self.status_pill.style().unpolish(self.status_pill)
        self.status_pill.style().polish(self.status_pill)

    def update_body_visual(self, body_label, name, temp):
        red = max(0, min(255, int((temp / 200) * 255)))
        body_label.setStyleSheet(
            f"background-color: rgb({red}, 0, 0); color: #ffffff; "
            f"border: 1px solid #cbd5e1; border-radius: 12px;"
        )
        body_label.setText(
            f"<span style='font-size:11px; color:rgba(255,255,255,0.8);'>{name}</span>"
            f"<br><span style='font-size:20px; font-weight:700; font-family:Consolas;'>{temp:.1f} °C</span>"
        )

    def update_thermal_bridge(self, t1, t2):
        r1 = max(0, min(255, int((t1 / 200) * 255)))
        r2 = max(0, min(255, int((t2 / 200) * 255)))
        self.thermal_bridge_label.setStyleSheet(
            f"background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 rgb({r1}, 0, 0), stop:1 rgb({r2}, 0, 0)); "
            f"color: #ffffff; font-family: Consolas; font-size: 14px; "
            f"font-weight: 700; border-radius: 6px;"
        )

        flux = self.conductivity_spinbox.value() * abs(t1 - t2)
        self.flux_label.setText(f"I = {flux:.1f} W")

        if abs(t1 - t2) < 0.05:
            self.thermal_bridge_label.setText("• • •")
        else:
            frames_right = ["▸ · ·", "▸ ▸ ·", "▸ ▸ ▸", "· ▸ ▸", "· · ▸"]
            frames_left = ["· · ◂", "· ◂ ◂", "◂ ◂ ◂", "◂ ◂ ·", "◂ · ·"]
            idx = self.arrow_frame % len(frames_right)
            self.thermal_bridge_label.setText(frames_right[idx] if t1 > t2 else frames_left[idx])

    def conductivity_changed(self):
        self.update_thermal_bridge(self.left_temp_display.value(), self.right_temp_display.value())

    def left_temp_changed(self):
        curr_temp = float(self.left_temp_slider.value())
        self.left_temp_display.setValue(curr_temp)
        self.update_body_visual(self.left_body_label, "Body 1", curr_temp)
        self.update_thermal_bridge(curr_temp, self.right_temp_display.value())

    def right_temp_changed(self):
        curr_temp = float(self.right_temp_slider.value())
        self.right_temp_display.setValue(curr_temp)
        self.update_body_visual(self.right_body_label, "Body 2", curr_temp)
        self.update_thermal_bridge(self.left_temp_display.value(), curr_temp)

    def timer_method(self):
        step_dt = self.dt * self.speed
        conductivity = self.conductivity_spinbox.value()
        t1 = self.body1.temperature
        t2 = self.body2.temperature
        i1 = conductivity * (t2 - t1)
        i2 = conductivity * (t1 - t2)
        dQ1 = i1 * step_dt
        dQ2 = i2 * step_dt
        new_t1 = self.body1.add_heat(dQ1)
        new_t2 = self.body2.add_heat(dQ2)

        self.arrow_frame += 1
        self.left_temp_display.setValue(new_t1)
        self.right_temp_display.setValue(new_t2)
        self.update_body_visual(self.left_body_label, "Body 1", new_t1)
        self.update_body_visual(self.right_body_label, "Body 2", new_t2)
        self.update_thermal_bridge(new_t1, new_t2)



        self.left_temp_slider.blockSignals(True)
        self.left_temp_slider.setValue(round(new_t1))
        self.left_temp_slider.blockSignals(False)

        self.right_temp_slider.blockSignals(True)
        self.right_temp_slider.setValue(round(new_t2))
        self.right_temp_slider.blockSignals(False)

        self.elapsed_time += step_dt
        self.clock_label.setText(f"{self.elapsed_time:.2f} s")
        self.time_history.append(self.elapsed_time)
        self.body1_temp_history.append(new_t1)
        self.body2_temp_history.append(new_t2)

        if abs(new_t1 - new_t2) < 0.05:
            self.start_stop_button.setChecked(False)
            self.start_stop_button_method()
            self.set_status_pill(f"● Equilibrium ({new_t1:.1f} °C)", "status_pill_equilibrium")
            


    def start_stop_button_method(self):
        if self.start_stop_button.isChecked():
            left_mass = self.left_mass_spinbox.value()
            left_heat_capacity = self.left_heat_capacity_spinbox.value()
            left_temp = self.left_temp_display.value()
            right_mass = self.right_mass_spinbox.value()
            right_heat_capacity = self.right_heat_capacity_spinbox.value()
            right_temp = self.right_temp_display.value()
            self.body1 = Body(left_mass, left_heat_capacity, left_temp)
            self.body2 = Body(right_mass, right_heat_capacity, right_temp)

            self.elapsed_time = 0.0
            self.arrow_frame = 0
            self.clock_label.setText("0.00 s")
            self.time_history = [0.0]
            self.body1_temp_history = [left_temp]
            self.body2_temp_history = [right_temp]

            self.start_stop_button.setText("Stop")
            self.status_pill.setText("● Running")
            self.status_pill.setObjectName("status_pill_running")
            self.status_pill.style().unpolish(self.status_pill)
            self.status_pill.style().polish(self.status_pill)
            self.timer.start(int(self.dt * 1000))
        else:
            self.timer.stop()
            self.start_stop_button.setText("Start")
            self.status_pill.setText("● Idle")
            self.status_pill.setObjectName("status_pill_idle")
            self.status_pill.style().unpolish(self.status_pill)
            self.status_pill.style().polish(self.status_pill)

    def speed_changed(self):
       self.speed = float(self.speed_combo.currentText().replace("x", ""))


    def reset_simulation(self):
        if self.start_stop_button.isChecked():
            self.start_stop_button.setChecked(False)
            self.start_stop_button_method()
        self.left_temp_slider.setValue(200)
        self.right_temp_slider.setValue(0)
        self.left_temp_changed()
        self.right_temp_changed()
        self.speed_combo.setCurrentText("1x")
        self.left_mass_spinbox.setValue(10.00)
        self.right_mass_spinbox.setValue(10.00)
        self.left_heat_capacity_spinbox.setValue(0.40)
        self.right_heat_capacity_spinbox.setValue(0.40)
        self.conductivity_spinbox.setValue(1.0)
        self.elapsed_time = 0.0
        self.arrow_frame = 0
        self.time_history=[]
        self.body1_temp_history=[]
        self.body2_temp_history = []
        self.graph_window.clear_graph()
        self.clock_label.setText("0.00 s")
        self.set_status_pill("● Idle", "status_pill_idle")
        self.update_thermal_bridge(200.0, 0.0)
            

    def open_about_window(self):
        self.about_window.show()

    def open_graph_window(self):
        self.graph_window.show()

    def closeEvent(self, event):
        self.about_window.close()
        self.graph_window.close()


if __name__ == "__main__":
    app = QApplication()
    app.styleHints().setColorScheme(Qt.ColorScheme.Light)
    app.setStyle("Fusion")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(current_dir, "style.qss")
    with open(style_path, "r") as f:
        app.setStyleSheet(f.read())

    window = HeatTransfer()
    window.show()
    app.exec()
