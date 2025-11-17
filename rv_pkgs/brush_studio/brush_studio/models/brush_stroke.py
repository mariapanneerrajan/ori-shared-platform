"""
Brush stroke data model.

Stores stroke points and metadata for a single brush stroke.
"""

from dataclasses import dataclass, field
from typing import List, Tuple
from brush_studio.models.sensor_data import SensorData


@dataclass
class StrokePoint:
    """
    Single point in a brush stroke with sensor data.
    """
    x: float                    # Normalized X coordinate (0-1)
    y: float                    # Normalized Y coordinate (0-1)
    sensor_data: SensorData     # Sensor readings at this point
    
    def to_tuple(self) -> Tuple[float, float, SensorData]:
        """Convert to tuple for easy unpacking."""
        return (self.x, self.y, self.sensor_data)


@dataclass
class BrushStroke:
    """
    Complete brush stroke with points and configuration.
    
    Stores all points in a stroke along with the brush preset
    used and timestamp information.
    """
    
    points: List[StrokePoint] = field(default_factory=list)
    preset_name: str = "Basic"
    color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)  # RGBA color used for this stroke
    texture_type: str = "soft_circle"  # Brush tip texture used
    size: float = 25.0  # Size used for this stroke
    opacity: float = 1.0  # Opacity used
    hardness: float = 0.5  # Hardness used
    flow: float = 1.0  # Flow used
    frame: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    
    def add_point(self, x: float, y: float, sensor_data: SensorData):
        """
        Add point to stroke.
        
        Args:
            x, y: Normalized coordinates (0-1)
            sensor_data: Sensor readings at this point
        """
        point = StrokePoint(x, y, sensor_data.copy())
        self.points.append(point)
    
    def get_num_points(self) -> int:
        """Get number of points in stroke."""
        return len(self.points)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get bounding box of stroke.
        
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        if not self.points:
            return (0, 0, 0, 0)
        
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        
        return (min(xs), min(ys), max(xs), max(ys))
    
    def clear(self):
        """Clear all points from stroke."""
        self.points.clear()

