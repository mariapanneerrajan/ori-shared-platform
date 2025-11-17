"""
Brush tip thumbnail generator.

Converts procedural texture data to QPixmap for UI display.
"""

import numpy as np
from typing import Dict

try:
    from PySide6.QtGui import QPixmap, QImage
    from PySide6.QtCore import Qt
except ImportError:
    from PySide2.QtGui import QPixmap, QImage
    from PySide2.QtCore import Qt

from brush_studio.rendering.brush_textures import BrushTextureGenerator


class BrushTipThumbnailGenerator:
    """
    Generates thumbnail images of brush tips for UI display.
    
    Converts texture data from BrushTextureGenerator to QPixmap,
    with caching to avoid regeneration.
    """
    
    # Mapping of texture type names to generator methods
    TEXTURE_GENERATORS = {
        'soft_circle': BrushTextureGenerator.create_soft_circle,
        'hard_circle': BrushTextureGenerator.create_hard_circle,
        'noise': BrushTextureGenerator.create_noise_texture,
        'square_hard': BrushTextureGenerator.create_square_hard,
        'square_soft': BrushTextureGenerator.create_square_soft,
        'triangle': BrushTextureGenerator.create_triangle,
        'star': BrushTextureGenerator.create_star,
        'splatter': BrushTextureGenerator.create_splatter,
        'stipple': BrushTextureGenerator.create_stipple,
        'grainy': BrushTextureGenerator.create_grainy,
        'scratchy': BrushTextureGenerator.create_scratchy,
        'diamond': BrushTextureGenerator.create_diamond,
    }
    
    def __init__(self):
        """Initialize thumbnail generator with empty cache."""
        self._thumbnail_cache: Dict[str, QPixmap] = {}
    
    def generate_thumbnail(self, texture_type: str, size: int = 64) -> QPixmap:
        """
        Generate thumbnail image for a brush tip texture.
        
        Args:
            texture_type: Type of texture (e.g., 'soft_circle', 'star')
            size: Thumbnail size in pixels (square)
        
        Returns:
            QPixmap containing thumbnail image
        """
        # Check cache first
        cache_key = f"{texture_type}_{size}"
        if cache_key in self._thumbnail_cache:
            return self._thumbnail_cache[cache_key]
        
        # Generate texture data
        if texture_type not in self.TEXTURE_GENERATORS:
            # Fallback to soft circle for unknown types
            texture_type = 'soft_circle'
        
        generator_func = self.TEXTURE_GENERATORS[texture_type]
        _, texture_data = generator_func(size=128)  # Generate at higher res
        
        # Convert numpy array to QImage
        # texture_data is float32 in range 0-1
        # Convert to 8-bit grayscale (0-255)
        grayscale_data = (texture_data * 255).astype(np.uint8)
        
        # Create QImage from grayscale data
        height, width = grayscale_data.shape
        bytes_per_line = width
        
        # QImage expects data in specific format
        # We'll create an RGBA image for better control
        rgba_data = np.zeros((height, width, 4), dtype=np.uint8)
        rgba_data[:, :, 0] = 0      # R - black
        rgba_data[:, :, 1] = 0      # G - black  
        rgba_data[:, :, 2] = 0      # B - black
        rgba_data[:, :, 3] = grayscale_data  # A - texture as alpha
        
        qimage = QImage(
            rgba_data.tobytes(),
            width,
            height,
            width * 4,
            QImage.Format_RGBA8888
        )
        
        # Scale to target size with smooth transformation
        qimage = qimage.scaled(
            size, size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Convert to pixmap
        pixmap = QPixmap.fromImage(qimage)
        
        # Cache and return
        self._thumbnail_cache[cache_key] = pixmap
        return pixmap
    
    def clear_cache(self):
        """Clear thumbnail cache to free memory."""
        self._thumbnail_cache.clear()
    
    @classmethod
    def get_all_texture_types(cls):
        """
        Get list of all available texture types.
        
        Returns:
            List of texture type names
        """
        return list(cls.TEXTURE_GENERATORS.keys())


# Singleton instance for convenience
_thumbnail_generator = None


def get_thumbnail_generator() -> BrushTipThumbnailGenerator:
    """
    Get singleton thumbnail generator instance.
    
    Returns:
        BrushTipThumbnailGenerator instance
    """
    global _thumbnail_generator
    if _thumbnail_generator is None:
        _thumbnail_generator = BrushTipThumbnailGenerator()
    return _thumbnail_generator

