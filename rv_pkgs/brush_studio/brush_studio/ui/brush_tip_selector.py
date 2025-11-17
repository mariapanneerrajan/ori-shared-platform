"""
Brush tip selector widget.

Grid-based selector for brush tip textures with visual thumbnails.
"""

try:
    from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout
    from PySide6.QtCore import Signal, Qt
    from PySide6.QtGui import QIcon
except ImportError:
    from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout
    from PySide2.QtCore import Signal, Qt
    from PySide2.QtGui import QIcon

from brush_studio.ui.brush_tip_thumbnail import get_thumbnail_generator


class BrushTipSelector(QWidget):
    """
    Grid-based brush tip selector widget.
    
    Displays thumbnails of all available brush tips in a 4x3 grid.
    Emits signal when a tip is selected.
    """
    
    # Signal emitted when tip is selected (texture_type)
    tip_selected = Signal(str)
    
    # All texture types in display order (4 cols x 3 rows)
    TEXTURE_TYPES = [
        'soft_circle', 'hard_circle', 'square_soft', 'square_hard',
        'triangle', 'diamond', 'star', 'noise',
        'splatter', 'stipple', 'grainy', 'scratchy',
    ]
    
    # Human-readable labels for each texture type
    TEXTURE_LABELS = {
        'soft_circle': 'Soft Circle',
        'hard_circle': 'Hard Circle',
        'square_soft': 'Soft Square',
        'square_hard': 'Hard Square',
        'triangle': 'Triangle',
        'diamond': 'Diamond',
        'star': 'Star',
        'noise': 'Noise',
        'splatter': 'Splatter',
        'stipple': 'Stipple',
        'grainy': 'Grainy',
        'scratchy': 'Scratchy',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thumbnail_generator = get_thumbnail_generator()
        self.selected_texture_type = 'soft_circle'  # Default selection
        self.buttons = {}  # Map texture_type -> button
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI with grid of brush tip buttons."""
        layout = QVBoxLayout(self)
        
        # Title label
        title = QLabel("Select Brush Tip Shape")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        # Grid of brush tip buttons
        grid = QGridLayout()
        grid.setSpacing(8)
        
        thumbnail_size = 64
        
        for idx, texture_type in enumerate(self.TEXTURE_TYPES):
            row = idx // 4
            col = idx % 4
            
            # Create button with thumbnail icon
            button = QPushButton()
            button.setFixedSize(thumbnail_size + 16, thumbnail_size + 16)
            button.setToolTip(self.TEXTURE_LABELS.get(texture_type, texture_type))
            
            # Generate and set thumbnail icon
            pixmap = self.thumbnail_generator.generate_thumbnail(texture_type, thumbnail_size)
            button.setIcon(QIcon(pixmap))
            button.setIconSize(pixmap.size())
            
            # Connect signal
            button.clicked.connect(lambda checked=False, tt=texture_type: self.on_tip_clicked(tt))
            
            # Store button reference
            self.buttons[texture_type] = button
            
            # Add to grid
            grid.addWidget(button, row, col)
        
        layout.addLayout(grid)
        
        # Selected tip label
        self.selected_label = QLabel(f"Selected: {self.TEXTURE_LABELS[self.selected_texture_type]}")
        self.selected_label.setStyleSheet("font-style: italic;")
        layout.addWidget(self.selected_label)
        
        # Apply initial selection styling
        self.update_button_styles()
    
    def on_tip_clicked(self, texture_type: str):
        """
        Handle brush tip button click.
        
        Args:
            texture_type: Type of texture that was clicked
        """
        self.selected_texture_type = texture_type
        self.update_button_styles()
        self.selected_label.setText(f"Selected: {self.TEXTURE_LABELS[texture_type]}")
        self.tip_selected.emit(texture_type)
    
    def update_button_styles(self):
        """Update button styles to show selection state."""
        for texture_type, button in self.buttons.items():
            if texture_type == self.selected_texture_type:
                # Selected state: highlighted border
                button.setStyleSheet("""
                    QPushButton {
                        border: 3px solid #4A90E2;
                        background-color: #E8F0FE;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #D0E3FF;
                    }
                """)
            else:
                # Normal state: subtle border
                button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #CCCCCC;
                        background-color: #FFFFFF;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        border: 2px solid #999999;
                        background-color: #F5F5F5;
                    }
                """)
    
    def set_selected_tip(self, texture_type: str):
        """
        Programmatically set the selected tip.
        
        Args:
            texture_type: Type of texture to select
        """
        if texture_type in self.buttons:
            self.selected_texture_type = texture_type
            self.update_button_styles()
            self.selected_label.setText(f"Selected: {self.TEXTURE_LABELS[texture_type]}")
    
    def get_selected_tip(self) -> str:
        """
        Get currently selected tip type.
        
        Returns:
            Texture type string
        """
        return self.selected_texture_type

