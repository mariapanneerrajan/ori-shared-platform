"""
Sensor system for brush dynamics.
"""

from brush_studio.sensors.sensor_base import BaseSensor
from brush_studio.sensors.pressure_sensor import PressureSensor
from brush_studio.sensors.tilt_sensor import TiltSensor
from brush_studio.sensors.rotation_sensor import RotationSensor
from brush_studio.sensors.speed_sensor import SpeedSensor
from brush_studio.sensors.distance_sensor import DistanceSensor
from brush_studio.sensors.time_sensor import TimeSensor

__all__ = [
    'BaseSensor',
    'PressureSensor',
    'TiltSensor',
    'RotationSensor',
    'SpeedSensor',
    'DistanceSensor',
    'TimeSensor'
]

