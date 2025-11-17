"""
Distance sensor for stroke progression.

Reads accumulated distance traveled and can create fade effects.
"""

from brush_studio.sensors.sensor_base import BaseSensor
from brush_studio.models.sensor_data import SensorData


class DistanceSensor(BaseSensor):
    """
    Distance sensor reads accumulated distance in stroke.
    
    Can be used to:
    - Fade out brush over distance (like running out of ink)
    - Cycle texture patterns based on distance
    - Create periodic size/opacity variations
    """
    
    def __init__(self, max_distance: float = 1000.0, mode: str = 'linear', **kwargs):
        """
        Initialize distance sensor.
        
        Args:
            max_distance: Distance value that maps to 1.0 (pixels)
            mode: How to interpret distance:
                  - 'linear': Direct mapping 0 to max_distance
                  - 'fade': Inverse mapping (1 at start, 0 at max_distance)
                  - 'periodic': Cycles from 0 to 1 repeatedly
            **kwargs: Passed to BaseSensor
        """
        super().__init__(**kwargs)
        self.max_distance = max_distance
        self.mode = mode
    
    def compute(self, sensor_data: SensorData) -> float:
        """
        Compute distance value from sensor data.
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Distance-based value 0.0-1.0
        """
        # Normalize distance to 0-1 range
        normalized = sensor_data.distance / self.max_distance
        
        if self.mode == 'fade':
            # Inverse: 1.0 at start, 0.0 at max_distance
            return max(0.0, 1.0 - normalized)
        
        elif self.mode == 'periodic':
            # Cycle from 0 to 1 repeatedly
            return normalized % 1.0
        
        else:  # linear
            # Direct mapping, clamped to 0-1
            return max(0.0, min(1.0, normalized))

