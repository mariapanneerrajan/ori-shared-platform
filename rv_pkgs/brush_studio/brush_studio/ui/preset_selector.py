"""
Preset selector widget (stub implementation).
"""

try:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtCore import Signal
except ImportError:
    from PySide2.QtWidgets import QWidget
    from PySide2.QtCore import Signal


class PresetSelector(QWidget):
    """Preset selector (included in BrushStudioPanel)."""
    preset_selected = Signal(str)

