"""
Base sensor class for brush dynamics.

All sensors inherit from BaseSensor and implement the compute() method.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
from brush_studio.models.sensor_data import SensorData


class BaseSensor(ABC):
    """
    Abstract base class for all sensors.
    
    Sensors read input state and output a normalized value (0.0-1.0)
    that can modulate brush parameters like size, opacity, flow, etc.
    """
    
    def __init__(
        self,
        enabled: bool = True,
        strength: float = 1.0,
        curve: Optional[Callable[[float], float]] = None
    ):
        """
        Initialize sensor.
        
        Args:
            enabled: Whether this sensor is active
            strength: Multiplier for sensor output (0.0-1.0)
            curve: Optional dynamics curve function for non-linear mapping
        """
        self.enabled = enabled
        self.strength = strength
        self.curve = curve or self._linear_curve
    
    @abstractmethod
    def compute(self, sensor_data: SensorData) -> float:
        """
        Compute sensor value from input data.
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Normalized value 0.0-1.0
        """
        pass
    
    def get_value(self, sensor_data: SensorData) -> float:
        """
        Get final sensor value with curve and strength applied.
        
        Args:
            sensor_data: Current sensor readings
        
        Returns:
            Final modulated value 0.0-1.0
        """
        if not self.enabled:
            return 1.0  # No modulation
        
        # Get raw value from sensor
        raw_value = self.compute(sensor_data)
        
        # Apply dynamics curve
        curved_value = self.apply_curve(raw_value)
        
        # Apply strength
        # Strength interpolates between no effect (1.0) and full effect (curved_value)
        return 1.0 + (curved_value - 1.0) * self.strength
    
    def apply_curve(self, value: float) -> float:
        """
        Apply dynamics curve to raw sensor value.
        
        Args:
            value: Raw sensor value 0.0-1.0
        
        Returns:
            Curved value 0.0-1.0
        """
        return self.curve(value)
    
    @staticmethod
    def _linear_curve(value: float) -> float:
        """Linear curve (no modification)."""
        return value
    
    @staticmethod
    def ease_in_curve(value: float) -> float:
        """Ease-in curve (slow start, fast end)."""
        return value * value
    
    @staticmethod
    def ease_out_curve(value: float) -> float:
        """Ease-out curve (fast start, slow end)."""
        return 1.0 - (1.0 - value) * (1.0 - value)
    
    @staticmethod
    def ease_in_out_curve(value: float) -> float:
        """Ease-in-out curve (slow start and end, fast middle)."""
        if value < 0.5:
            return 2.0 * value * value
        else:
            return 1.0 - 2.0 * (1.0 - value) * (1.0 - value)

