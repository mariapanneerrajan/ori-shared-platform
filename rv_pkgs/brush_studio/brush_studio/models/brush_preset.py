"""
Brush preset configuration.

Stores complete brush settings including base parameters and sensor modulation.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import json


@dataclass
class SensorConfig:
    """
    Configuration for sensor modulation of a brush parameter.
    """
    sensor_type: str  # 'pressure', 'tilt', 'rotation', 'speed', 'distance', 'time'
    enabled: bool = True
    strength: float = 1.0  # 0.0-1.0
    curve: str = 'linear'  # 'linear', 'ease_in', 'ease_out', 'ease_in_out'


@dataclass
class BrushPreset:
    """
    Complete brush configuration.
    
    Stores all parameters needed to define a brush, including base
    properties and sensor modulation settings.
    """
    
    # Preset metadata
    name: str = "Untitled Brush"
    icon_path: str = ""  # Path to preset thumbnail (optional)
    
    # Base brush parameters
    size: float = 20.0              # Base size in pixels
    opacity: float = 1.0            # Base opacity 0.0-1.0
    flow: float = 1.0               # Paint accumulation 0.0-1.0
    hardness: float = 0.5           # Edge softness 0.0-1.0
    spacing: float = 0.15           # Distance between stamps (0.0-1.0)
    
    # Brush appearance
    color: tuple = (0.0, 0.0, 0.0, 1.0)  # RGBA color
    texture_type: str = "soft_circle"     # "soft_circle", "hard_circle", "noise"
    
    # Sensor modulation settings
    size_modulation: List[SensorConfig] = field(default_factory=list)
    opacity_modulation: List[SensorConfig] = field(default_factory=list)
    flow_modulation: List[SensorConfig] = field(default_factory=list)
    rotation_modulation: List[SensorConfig] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """
        Convert preset to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation
        """
        data = asdict(self)
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BrushPreset':
        """
        Create preset from dictionary.
        
        Args:
            data: Dictionary from JSON
        
        Returns:
            BrushPreset instance
        """
        # Convert sensor configs
        for key in ['size_modulation', 'opacity_modulation', 'flow_modulation', 'rotation_modulation']:
            if key in data and isinstance(data[key], list):
                data[key] = [
                    SensorConfig(**item) if isinstance(item, dict) else item
                    for item in data[key]
                ]
        
        # Convert color tuple
        if 'color' in data and isinstance(data['color'], list):
            data['color'] = tuple(data['color'])
        
        return cls(**data)
    
    def to_json(self, filepath: str):
        """
        Save preset to JSON file.
        
        Args:
            filepath: Path to save file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_json(cls, filepath: str) -> 'BrushPreset':
        """
        Load preset from JSON file.
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            BrushPreset instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def add_size_sensor(self, sensor_type: str, enabled: bool = True, strength: float = 1.0, curve: str = 'linear'):
        """Add sensor modulation for size parameter."""
        self.size_modulation.append(SensorConfig(sensor_type, enabled, strength, curve))
    
    def add_opacity_sensor(self, sensor_type: str, enabled: bool = True, strength: float = 1.0, curve: str = 'linear'):
        """Add sensor modulation for opacity parameter."""
        self.opacity_modulation.append(SensorConfig(sensor_type, enabled, strength, curve))
    
    def add_flow_sensor(self, sensor_type: str, enabled: bool = True, strength: float = 1.0, curve: str = 'linear'):
        """Add sensor modulation for flow parameter."""
        self.flow_modulation.append(SensorConfig(sensor_type, enabled, strength, curve))
    
    def add_rotation_sensor(self, sensor_type: str, enabled: bool = True, strength: float = 1.0, curve: str = 'linear'):
        """Add sensor modulation for rotation parameter."""
        self.rotation_modulation.append(SensorConfig(sensor_type, enabled, strength, curve))

