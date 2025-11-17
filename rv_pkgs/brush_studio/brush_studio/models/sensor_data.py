"""
Sensor data container for brush dynamics.

Stores all sensor readings at a point in time during a brush stroke.
"""

from dataclasses import dataclass, field
import time as time_module


@dataclass
class SensorData:
    """
    Container for all sensor readings at a point in time.
    
    This class stores raw sensor values that are used by sensor
    implementations to modulate brush parameters.
    """
    
    # Stylus sensors
    pressure: float = 1.0          # 0.0 - 1.0
    tilt_x: float = 0.0            # -1.0 to 1.0 (left/right tilt)
    tilt_y: float = 0.0            # -1.0 to 1.0 (forward/back tilt)
    rotation: float = 0.0          # 0.0 - 360.0 degrees (barrel rotation)
    
    # Motion sensors
    speed: float = 0.0             # pixels per second
    distance: float = 0.0          # accumulated distance in stroke (pixels)
    time: float = 0.0              # seconds since stroke start
    
    # Position (for reference, not typically used by sensors)
    x: float = 0.0                 # normalized x coordinate (0.0-1.0)
    y: float = 0.0                 # normalized y coordinate (0.0-1.0)
    
    # Timestamp
    timestamp: float = field(default_factory=time_module.time)
    
    def copy(self) -> 'SensorData':
        """Create a copy of this sensor data."""
        return SensorData(
            pressure=self.pressure,
            tilt_x=self.tilt_x,
            tilt_y=self.tilt_y,
            rotation=self.rotation,
            speed=self.speed,
            distance=self.distance,
            time=self.time,
            x=self.x,
            y=self.y,
            timestamp=self.timestamp
        )

