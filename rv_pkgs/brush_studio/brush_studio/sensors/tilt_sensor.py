"""
Tilt sensor for stylus orientation.

Reads tilt angle from stylus and can modulate brush size, rotation, etc.
"""

import math
from brush_studio.sensors.sensor_base import BaseSensor
from brush_studio.models.sensor_data import SensorData


class TiltSensor(BaseSensor):
    """
    Tilt sensor reads stylus tilt angle.
    
    Can be used to:
    - Increase brush size when pen is tilted (like a real brush)
    - Rotate brush based on tilt direction
    - Fade opacity when pen is perpendicular
    """
    
    def __init__(self, mode: str = 'magnitude', **kwargs):
        """
        Initialize tilt sensor.
        
        Args:
            mode: How to compute tilt value:
                  - 'magnitude': Total tilt amount (0=vertical, 1=horizontal)
                  - 'x': X-axis tilt only
                  - 'y': Y-axis tilt only
            **kwargs: Passed to BaseSensor
        """
        super().__init__(**kwargs)
        self.mode = mode
    
    def compute(self, sensor_data: SensorData) -> float:
        """
        Compute tilt value from sensor data.
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Tilt value 0.0-1.0
        """
        if self.mode == 'x':
            # X-axis tilt only (-1 to 1 -> 0 to 1)
            return (sensor_data.tilt_x + 1.0) * 0.5
        
        elif self.mode == 'y':
            # Y-axis tilt only (-1 to 1 -> 0 to 1)
            return (sensor_data.tilt_y + 1.0) * 0.5
        
        else:  # magnitude
            # Total tilt magnitude (0 = vertical, 1 = fully tilted)
            magnitude = math.sqrt(
                sensor_data.tilt_x ** 2 + sensor_data.tilt_y ** 2
            )
            # Normalize to 0-1 range (max tilt is sqrt(2) ≈ 1.414)
            return min(1.0, magnitude / 1.414)

