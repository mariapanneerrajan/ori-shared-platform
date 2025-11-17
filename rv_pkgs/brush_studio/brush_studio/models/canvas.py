"""
Canvas model for frame-based brush stroke storage.

Manages brush strokes across multiple frames.
"""

from typing import Dict, List, Optional
from brush_studio.models.brush_stroke import BrushStroke


class Canvas:
    """
    Canvas manages brush strokes across frames.
    
    Stores stroke data per frame for easy serialization and management.
    Note: Actual pixel data is stored in FBOs managed by BrushRenderer.
    """
    
    def __init__(self):
        """Initialize canvas."""
        self.strokes_by_frame: Dict[int, List[BrushStroke]] = {}
        self.current_stroke: Optional[BrushStroke] = None
    
    def start_stroke(
        self, 
        frame: int, 
        preset_name: str, 
        color: tuple = (0.0, 0.0, 0.0, 1.0),
        texture_type: str = "soft_circle",
        size: float = 25.0,
        opacity: float = 1.0,
        hardness: float = 0.5,
        flow: float = 1.0
    ) -> BrushStroke:
        """
        Start a new stroke on given frame.
        
        Args:
            frame: Frame number
            preset_name: Name of brush preset
            color: RGBA color tuple (r, g, b, a) used for this stroke
            texture_type: Brush tip texture type
            size: Brush size
            opacity: Brush opacity
            hardness: Brush hardness
            flow: Brush flow
        
        Returns:
            New BrushStroke instance
        """
        self.current_stroke = BrushStroke(
            preset_name=preset_name,
            frame=frame,
            color=color,
            texture_type=texture_type,
            size=size,
            opacity=opacity,
            hardness=hardness,
            flow=flow
        )
        return self.current_stroke
    
    def end_stroke(self):
        """
        Finish current stroke and add to canvas.
        """
        if self.current_stroke is None:
            return
        
        frame = self.current_stroke.frame
        if frame not in self.strokes_by_frame:
            self.strokes_by_frame[frame] = []
        
        # Only add if stroke has points
        if self.current_stroke.get_num_points() > 0:
            self.strokes_by_frame[frame].append(self.current_stroke)
        
        self.current_stroke = None
    
    def get_strokes(self, frame: int) -> List[BrushStroke]:
        """
        Get all strokes for a frame.
        
        Args:
            frame: Frame number
        
        Returns:
            List of strokes (empty if none)
        """
        return self.strokes_by_frame.get(frame, [])
    
    def has_strokes(self, frame: int) -> bool:
        """
        Check if frame has any strokes.
        
        Args:
            frame: Frame number
        
        Returns:
            True if frame has strokes
        """
        return frame in self.strokes_by_frame and len(self.strokes_by_frame[frame]) > 0
    
    def clear_frame(self, frame: int):
        """
        Clear all strokes from frame.
        
        Args:
            frame: Frame number
        """
        if frame in self.strokes_by_frame:
            del self.strokes_by_frame[frame]
    
    def clear_all(self):
        """Clear all strokes from all frames."""
        self.strokes_by_frame.clear()
        self.current_stroke = None
    
    def get_all_frames(self) -> List[int]:
        """
        Get list of all frames with strokes.
        
        Returns:
            Sorted list of frame numbers
        """
        return sorted(self.strokes_by_frame.keys())

