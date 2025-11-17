"""
Main brush studio UI panel (simplified implementation).
"""

try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                    QPushButton, QSlider, QDoubleSpinBox, QGridLayout,
                                    QGroupBox, QColorDialog)
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QColor
except ImportError:
    from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                    QPushButton, QSlider, QDoubleSpinBox, QGridLayout,
                                    QGroupBox, QColorDialog)
    from PySide2.QtCore import Qt, Signal
    from PySide2.QtGui import QColor

from brush_studio.ui.brush_tip_selector import BrushTipSelector


class BrushStudioPanel(QWidget):
    """
    Main control panel for Brush Studio.
    
    Provides preset selection and parameter controls in a simple layout.
    """
    
    preset_changed = Signal(str)  # Preset name
    size_changed = Signal(float)
    opacity_changed = Signal(float)
    hardness_changed = Signal(float)
    flow_changed = Signal(float)
    color_changed = Signal(tuple)  # (r, g, b, a) floats 0-1
    tip_changed = Signal(str)  # Brush tip texture type
    clear_frame_requested = Signal()  # Request to clear current frame
    save_requested = Signal()  # Request to save annotations
    open_requested = Signal()  # Request to open annotations
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_color = QColor(0, 0, 0, 255)  # Black
        self.current_tip_type = 'soft_circle'  # Default tip type
        
        # Store slider references for programmatic updates
        self.size_slider = None
        self.size_spinbox = None
        self.opacity_slider = None
        self.opacity_spinbox = None
        self.hardness_slider = None
        self.hardness_spinbox = None
        self.flow_slider = None
        self.flow_spinbox = None
        self.sensor_label = None
        
        # Store tip selector reference
        self.tip_selector = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI layout."""
        layout = QVBoxLayout(self)
        
        # ===== Brush Tip Selector (at top) =====
        tip_group = QGroupBox("Brush Tip Shape")
        tip_layout = QVBoxLayout()
        
        # Create brush tip selector
        self.tip_selector = BrushTipSelector()
        self.tip_selector.tip_selected.connect(self.on_tip_selected)
        tip_layout.addWidget(self.tip_selector)
        
        tip_group.setLayout(tip_layout)
        layout.addWidget(tip_group)
        
        # ===== Preset selector =====
        preset_group = QGroupBox("Brush Presets")
        preset_layout = QGridLayout()
        
        presets = ["Basic", "Soft", "Airbrush", "Pencil", "Ink",
                   "Eraser Hard", "Eraser Soft", "Charcoal", "Marker", "Watercolor"]
        
        for i, preset in enumerate(presets):
            btn = QPushButton(preset)
            btn.clicked.connect(lambda checked=False, p=preset: self.preset_changed.emit(p))
            preset_layout.addWidget(btn, i // 3, i % 3)
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # ===== Parameters =====
        params_group = QGroupBox("Brush Parameters")
        params_layout = QVBoxLayout()
        
        # Size
        size_widget, self.size_slider, self.size_spinbox = self._create_slider_control(
            "Size", 1, 100, 25, lambda v: self.size_changed.emit(float(v)))
        params_layout.addWidget(size_widget)
        
        # Opacity
        opacity_widget, self.opacity_slider, self.opacity_spinbox = self._create_slider_control(
            "Opacity", 0, 100, 100, lambda v: self.opacity_changed.emit(v / 100.0))
        params_layout.addWidget(opacity_widget)
        
        # Hardness
        hardness_widget, self.hardness_slider, self.hardness_spinbox = self._create_slider_control(
            "Hardness", 0, 100, 50, lambda v: self.hardness_changed.emit(v / 100.0))
        params_layout.addWidget(hardness_widget)
        
        # Flow
        flow_widget, self.flow_slider, self.flow_spinbox = self._create_slider_control(
            "Flow", 0, 100, 100, lambda v: self.flow_changed.emit(v / 100.0))
        params_layout.addWidget(flow_widget)
        
        # Color picker
        color_widget = QWidget()
        color_layout = QHBoxLayout(color_widget)
        color_layout.addWidget(QLabel("Color:"))
        
        self.color_button = QPushButton()
        self.color_button.setFixedSize(80, 30)
        self.color_button.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.color_button.clicked.connect(self.pick_color)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        
        params_layout.addWidget(color_widget)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # ===== Sensor modulation display =====
        sensor_group = QGroupBox("Active Sensors")
        sensor_layout = QVBoxLayout()
        
        self.sensor_label = QLabel("No preset selected")
        self.sensor_label.setWordWrap(True)
        self.sensor_label.setStyleSheet("QLabel { padding: 5px; background-color: #2b2b2b; }")
        sensor_layout.addWidget(self.sensor_label)
        
        sensor_group.setLayout(sensor_layout)
        layout.addWidget(sensor_group)
        
        # ===== Action Buttons =====
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.setToolTip("Save annotations to JSON file")
        save_button.clicked.connect(lambda: self.save_requested.emit())
        buttons_layout.addWidget(save_button)
        
        # Open button
        open_button = QPushButton("Open")
        open_button.setToolTip("Open annotations from JSON file")
        open_button.clicked.connect(lambda: self.open_requested.emit())
        buttons_layout.addWidget(open_button)
        
        # Clear Frame button
        clear_button = QPushButton("Clear Frame")
        clear_button.setToolTip("Clear all strokes on current frame")
        clear_button.clicked.connect(lambda: self.clear_frame_requested.emit())
        buttons_layout.addWidget(clear_button)
        
        layout.addWidget(buttons_widget)
        
        layout.addStretch()
    
    def _create_slider_control(self, label, min_val, max_val, default, callback):
        """Create slider with label."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        layout.addWidget(QLabel(label + ":"))
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default)
        slider.valueChanged.connect(callback)
        layout.addWidget(slider)
        
        spinbox = QDoubleSpinBox()
        spinbox.setMinimum(float(min_val))
        spinbox.setMaximum(float(max_val))
        spinbox.setValue(float(default))
        spinbox.setDecimals(1)
        
        # Connect spinbox to slider (avoid infinite loops with blockSignals)
        def on_spinbox_changed(value):
            slider.blockSignals(True)
            slider.setValue(int(value))
            slider.blockSignals(False)
        
        def on_slider_changed(value):
            spinbox.blockSignals(True)
            spinbox.setValue(float(value))
            spinbox.blockSignals(False)
        
        spinbox.valueChanged.connect(on_spinbox_changed)
        slider.valueChanged.connect(on_slider_changed)
        
        layout.addWidget(spinbox)
        
        return widget, slider, spinbox
    
    def pick_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self.current_color, self, "Pick Brush Color")
        if color.isValid():
            self.current_color = color
            # Update button color
            self.color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
            )
            # Emit color as normalized RGBA tuple
            r = color.red() / 255.0
            g = color.green() / 255.0
            b = color.blue() / 255.0
            a = color.alpha() / 255.0
            self.color_changed.emit((r, g, b, a))
    
    def on_tip_selected(self, texture_type: str):
        """
        Handle brush tip selection from selector widget.
        
        Args:
            texture_type: Type of texture that was selected
        """
        self.current_tip_type = texture_type
        self.tip_changed.emit(texture_type)
    
    def update_parameters(self, size, opacity, hardness, flow, color):
        """Update UI controls with preset values (without triggering signals)."""
        # Block signals to prevent feedback loops
        self.size_slider.blockSignals(True)
        self.size_spinbox.blockSignals(True)
        self.size_slider.setValue(int(size))
        self.size_spinbox.setValue(size)
        self.size_slider.blockSignals(False)
        self.size_spinbox.blockSignals(False)
        
        # Opacity (0-1 to 0-100)
        self.opacity_slider.blockSignals(True)
        self.opacity_spinbox.blockSignals(True)
        self.opacity_slider.setValue(int(opacity * 100))
        self.opacity_spinbox.setValue(opacity * 100)
        self.opacity_slider.blockSignals(False)
        self.opacity_spinbox.blockSignals(False)
        
        # Hardness (0-1 to 0-100)
        self.hardness_slider.blockSignals(True)
        self.hardness_spinbox.blockSignals(True)
        self.hardness_slider.setValue(int(hardness * 100))
        self.hardness_spinbox.setValue(hardness * 100)
        self.hardness_slider.blockSignals(False)
        self.hardness_spinbox.blockSignals(False)
        
        # Flow (0-1 to 0-100)
        self.flow_slider.blockSignals(True)
        self.flow_spinbox.blockSignals(True)
        self.flow_slider.setValue(int(flow * 100))
        self.flow_spinbox.setValue(flow * 100)
        self.flow_slider.blockSignals(False)
        self.flow_spinbox.blockSignals(False)
        
        # Update color button
        r, g, b, a = color
        self.current_color = QColor(int(r*255), int(g*255), int(b*255), int(a*255))
        self.color_button.setStyleSheet(
            f"background-color: rgb({int(r*255)}, {int(g*255)}, {int(b*255)});"
        )
    
    def update_sensor_display(self, preset):
        """Update sensor modulation display to show what sensors are active."""
        if not preset:
            self.sensor_label.setText("No preset selected")
            return
        
        # Build sensor info text
        sensor_info = []
        
        # Check size modulation
        if preset.size_modulation:
            size_sensors = [s.sensor_type for s in preset.size_modulation if s.enabled]
            if size_sensors:
                sensor_info.append(f"<b>Size:</b> {', '.join(size_sensors)}")
        
        # Check opacity modulation
        if preset.opacity_modulation:
            opacity_sensors = [s.sensor_type for s in preset.opacity_modulation if s.enabled]
            if opacity_sensors:
                sensor_info.append(f"<b>Opacity:</b> {', '.join(opacity_sensors)}")
        
        # Check flow modulation
        if preset.flow_modulation:
            flow_sensors = [s.sensor_type for s in preset.flow_modulation if s.enabled]
            if flow_sensors:
                sensor_info.append(f"<b>Flow:</b> {', '.join(flow_sensors)}")
        
        # Check rotation modulation
        if preset.rotation_modulation:
            rotation_sensors = [s.sensor_type for s in preset.rotation_modulation if s.enabled]
            if rotation_sensors:
                sensor_info.append(f"<b>Rotation:</b> {', '.join(rotation_sensors)}")
        
        if sensor_info:
            self.sensor_label.setText("<br>".join(sensor_info))
        else:
            self.sensor_label.setText("No sensor modulation")

