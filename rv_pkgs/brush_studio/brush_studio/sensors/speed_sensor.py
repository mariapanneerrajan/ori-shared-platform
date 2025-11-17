"""
Speed sensor for drawing velocity.

Reads drawing speed and can modulate brush opacity, size, etc.
"""

from brush_studio.sensors.sensor_base import BaseSensor
from brush_studio.models.sensor_data import SensorData


class SpeedSensor(BaseSensor):
    """
    Speed sensor reads drawing velocity (pixels per second).
    
    Can be used to:
    - Fade opacity when drawing fast (like a dry brush)
    - Increase size when drawing fast (momentum effect)
    - Create speed-based texture effects
    """
    
    def __init__(self, max_speed: float = 1000.0, **kwargs):
        """
        Initialize speed sensor.
        
        Args:
            max_speed: Speed value that maps to 1.0 (pixels/sec)
            **kwargs: Passed to BaseSensor
        """
        super().__init__(**kwargs)
        self.max_speed = max_speed
    
    def compute(self, sensor_data: SensorData) -> float:
        """
        Compute speed value from sensor data.
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Normalized speed 0.0-1.0
        """
        # Normalize speed to 0-1 range
        normalized = sensor_data.speed / self.max_speed
        
        # Clamp to 0-1
        return max(0.0, min(1.0, normalized))

