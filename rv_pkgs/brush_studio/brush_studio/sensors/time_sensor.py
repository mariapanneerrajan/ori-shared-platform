"""
Time sensor for temporal brush effects.

Reads time since stroke start and can create time-based modulation.
"""

import math
from brush_studio.sensors.sensor_base import BaseSensor
from brush_studio.models.sensor_data import SensorData


class TimeSensor(BaseSensor):
    """
    Time sensor reads elapsed time since stroke start.
    
    Can be used to:
    - Fade in brush at stroke start
    - Fade out over time (like running out of paint)
    - Create pulsing/oscillating effects
    """
    
    def __init__(self, max_time: float = 5.0, mode: str = 'linear', **kwargs):
        """
        Initialize time sensor.
        
        Args:
            max_time: Time value that maps to 1.0 (seconds)
            mode: How to interpret time:
                  - 'linear': Direct mapping 0 to max_time
                  - 'fade': Inverse mapping (1 at start, 0 at max_time)
                  - 'oscillate': Sine wave oscillation
            **kwargs: Passed to BaseSensor
        """
        super().__init__(**kwargs)
        self.max_time = max_time
        self.mode = mode
    
    def compute(self, sensor_data: SensorData) -> float:
        """
        Compute time value from sensor data.
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Time-based value 0.0-1.0
        """
        # Normalize time to 0-1 range
        normalized = sensor_data.time / self.max_time
        
        if self.mode == 'fade':
            # Inverse: 1.0 at start, 0.0 at max_time
            return max(0.0, 1.0 - normalized)
        
        elif self.mode == 'oscillate':
            # Sine wave: oscillates between 0 and 1
            # Frequency: 1 complete cycle per max_time
            return (math.sin(2.0 * math.pi * normalized) + 1.0) * 0.5
        
        else:  # linear
            # Direct mapping, clamped to 0-1
            return max(0.0, min(1.0, normalized))

