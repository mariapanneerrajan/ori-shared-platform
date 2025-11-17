"""
Sensor control widgets (stub implementation).
"""

try:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtCore import Signal
except ImportError:
    from PySide2.QtWidgets import QWidget
    from PySide2.QtCore import Signal


class SensorControls(QWidget):
    """Sensor controls (can be added to panel later)."""
    sensor_changed = Signal(str, bool, float)

