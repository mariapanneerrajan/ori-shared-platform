"""
Canvas persistence - save/load FBO textures as PNG files.
"""

from pathlib import Path
from typing import Optional
import numpy as np

try:
    from PIL import Image
except ImportError:
    Image = None  # PIL not available


class CanvasStorage:
    """
    Saves and loads canvas FBO textures as PNG files.
    
    Stores per-frame canvas data in user's home directory.
    """
    
    def __init__(self, session_id: str = "default"):
        """
        Initialize canvas storage.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.storage_dir = Path.home() / ".rv" / "BrushStudio" / session_id
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_frame(self, frame: int, pixel_data: np.ndarray):
        """
        Save frame canvas to PNG.
        
        Args:
            frame: Frame number
            pixel_data: RGBA float array (height, width, 4)
        """
        if Image is None:
            print("Warning: PIL not available, cannot save canvas")
            return
        
        # Convert float [0-1] to uint8 [0-255]
        pixel_data_uint8 = (pixel_data * 255).astype(np.uint8)
        
        # Create PIL image
        img = Image.fromarray(pixel_data_uint8, mode='RGBA')
        
        # Save to PNG
        filepath = self.storage_dir / f"frame_{frame:06d}.png"
        img.save(filepath, 'PNG')
    
    def load_frame(self, frame: int) -> Optional[np.ndarray]:
        """
        Load frame canvas from PNG.
        
        Args:
            frame: Frame number
        
        Returns:
            RGBA float array or None if not found
        """
        if Image is None:
            return None
        
        filepath = self.storage_dir / f"frame_{frame:06d}.png"
        if not filepath.exists():
            return None
        
        # Load PNG
        img = Image.open(filepath)
        
        # Convert to numpy array
        pixel_data_uint8 = np.array(img)
        
        # Convert uint8 [0-255] to float [0-1]
        pixel_data = pixel_data_uint8.astype(np.float32) / 255.0
        
        return pixel_data
    
    def has_frame(self, frame: int) -> bool:
        """Check if frame has saved data."""
        filepath = self.storage_dir / f"frame_{frame:06d}.png"
        return filepath.exists()
    
    def delete_frame(self, frame: int):
        """Delete saved frame data."""
        filepath = self.storage_dir / f"frame_{frame:06d}.png"
        if filepath.exists():
            filepath.unlink()
    
    def clear_all(self):
        """Delete all saved frames."""
        for png_file in self.storage_dir.glob("frame_*.png"):
            png_file.unlink()

