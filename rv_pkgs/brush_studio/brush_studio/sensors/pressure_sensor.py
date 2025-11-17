"""
Pressure sensor for stylus input.

Reads pressure from stylus/tablet and modulates brush parameters.
"""

from brush_studio.sensors.sensor_base import BaseSensor
from brush_studio.models.sensor_data import SensorData


class PressureSensor(BaseSensor):
    """
    Pressure sensor reads stylus pressure (0.0-1.0).
    
    This is the most commonly used sensor, typically affecting
    brush size and opacity to create natural stroke variation.
    """
    
    def compute(self, sensor_data: SensorData) -> float:
        """
        Read pressure value from sensor data.
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Pressure value 0.0-1.0
        """
        # Clamp pressure to valid range
        return max(0.0, min(1.0, sensor_data.pressure))

