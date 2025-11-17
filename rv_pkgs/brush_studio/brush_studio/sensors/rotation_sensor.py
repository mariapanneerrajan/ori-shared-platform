"""
Rotation sensor for stylus barrel rotation.

Reads barrel rotation angle and can rotate brush accordingly.
"""

from brush_studio.sensors.sensor_base import BaseSensor
from brush_studio.models.sensor_data import SensorData


class RotationSensor(BaseSensor):
    """
    Rotation sensor reads stylus barrel rotation (0-360 degrees).
    
    Commonly used to rotate asymmetric brush tips (e.g., calligraphy pen)
    to match the pen's physical rotation.
    """
    
    def compute(self, sensor_data: SensorData) -> float:
        """
        Compute rotation value from sensor data.
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Normalized rotation 0.0-1.0 (0°-360° mapped to 0-1)
        """
        # Normalize rotation from 0-360 degrees to 0-1 range
        rotation = sensor_data.rotation % 360.0
        return rotation / 360.0
    
    def get_rotation_degrees(self, sensor_data: SensorData) -> float:
        """
        Get rotation in degrees directly (for brush rendering).
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Rotation angle in degrees (0-360)
        """
        if not self.enabled:
            return 0.0
        
        return sensor_data.rotation % 360.0

