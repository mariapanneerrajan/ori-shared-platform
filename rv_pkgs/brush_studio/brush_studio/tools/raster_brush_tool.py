"""
Raster brush tool for interactive painting.

Handles stroke input, sensor reading, and coordinates with BrushRenderer.
"""

from typing import Optional, Tuple
import time
import math

from brush_studio.models.sensor_data import SensorData
from brush_studio.models.brush_stroke import BrushStroke
from brush_studio.models.brush_preset import BrushPreset
from brush_studio.models.canvas import Canvas
from brush_studio.sensors import PressureSensor, TiltSensor, RotationSensor, SpeedSensor, DistanceSensor, TimeSensor
from brush_studio.utils.interpolation import interpolate_points, lerp


class RasterBrushTool:
    """
    Interactive raster painting tool.
    
    Reads sensor input from stylus/mouse, interpolates stroke points,
    and stamps brush to FBO via BrushRenderer.
    """
    
    def __init__(self):
        """Initialize raster brush tool."""
        self.current_preset: Optional[BrushPreset] = None
        self.stroke: Optional[BrushStroke] = None
        self.renderer = None  # Set by mode
        self.canvas: Optional[Canvas] = None
        
        # Stroke state
        self.is_drawing = False
        self.last_point: Optional[Tuple[float, float]] = None
        self.last_sensor_data: Optional[SensorData] = None
        self.last_stamp_time = 0.0
        self.stroke_start_time = 0.0
        self.accumulated_distance = 0.0
        
        # Sensors (created on demand)
        self.sensors = {
            'pressure': PressureSensor(),
            'tilt': TiltSensor(),
            'rotation': RotationSensor(),
            'speed': SpeedSensor(),
            'distance': DistanceSensor(),
            'time': TimeSensor()
        }
    
    def set_preset(self, preset: BrushPreset):
        """
        Set current brush preset.
        
        Args:
            preset: BrushPreset configuration
        """
        self.current_preset = preset
    
    def on_press(self, event, canvas: Canvas, x: float, y: float):
        """
        Start new brush stroke.
        
        Args:
            event: RV event with input data
            canvas: Canvas to draw on
            x, y: Normalized coordinates (0-1)
        """
        if not self.current_preset or not self.renderer:
            return
        
        self.is_drawing = True
        self.canvas = canvas
        self.last_point = (x, y)
        self.stroke_start_time = time.time()
        self.accumulated_distance = 0.0
        
        # Read sensor data
        sensor_data = self._read_sensors(event, x, y, 0.0, 0.0)
        self.last_sensor_data = sensor_data
        
        # Start stroke on canvas with all current brush properties
        current_frame = getattr(canvas, 'current_frame', 0)
        # Store all properties that were used for this stroke
        stroke_color = self.current_preset.color if self.current_preset else (0.0, 0.0, 0.0, 1.0)
        texture_type = self.current_preset.texture_type if self.current_preset else "soft_circle"
        size = self.current_preset.size if self.current_preset else 25.0
        opacity = self.current_preset.opacity if self.current_preset else 1.0
        hardness = self.current_preset.hardness if self.current_preset else 0.5
        flow = self.current_preset.flow if self.current_preset else 1.0
        
        self.stroke = canvas.start_stroke(
            current_frame, 
            self.current_preset.name,
            stroke_color,
            texture_type,
            size,
            opacity,
            hardness,
            flow
        )
        self.stroke.add_point(x, y, sensor_data)
        
        # Begin stroke on renderer
        self.renderer.begin_stroke(self.current_preset, current_frame)
        
        # Stamp first point
        self._stamp_at_point(x, y, sensor_data, current_frame)
        self.last_stamp_time = time.time()
    
    def on_drag(self, event, canvas: Canvas, x: float, y: float):
        """
        Continue brush stroke.
        
        Args:
            event: RV event with input data
            canvas: Canvas to draw on
            x, y: Normalized coordinates (0-1)
        """
        if not self.is_drawing or not self.current_preset or not self.last_point:
            return
        
        last_x, last_y = self.last_point
        
        # Calculate distance from last point
        dx = x - last_x
        dy = y - last_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Calculate speed (pixels per second)
        current_time = time.time()
        dt = current_time - self.last_stamp_time
        speed = distance / dt if dt > 0 else 0.0
        
        # Update accumulated distance
        self.accumulated_distance += distance
        
        # Read sensor data
        sensor_data = self._read_sensors(event, x, y, speed, self.accumulated_distance)
        
        # Calculate actual spacing in normalized units based on brush size
        # Get actual image dimensions from renderer
        image_width = self.renderer.image_width if self.renderer else 1920
        
        # spacing parameter is relative to brush diameter (e.g., 0.1 = 10% of brush size)
        # Convert brush size (pixels) to normalized space (0-1)
        brush_size_norm = self.current_preset.size / image_width
        
        # Calculate actual spacing: spacing * brush_size (both in normalized units)
        # This ensures stamps overlap for smooth strokes
        actual_spacing = self.current_preset.spacing * brush_size_norm
        
        # Interpolate points based on spacing
        interpolated = interpolate_points(last_x, last_y, x, y, actual_spacing)
        
        # Stamp along interpolated path
        current_frame = getattr(canvas, 'current_frame', 0)
        
        if interpolated:
            for interp_x, interp_y in interpolated:
                # Interpolate sensor data
                t = self._calculate_interpolation_factor(last_x, last_y, interp_x, interp_y, x, y)
                interp_sensor = self._interpolate_sensor_data(self.last_sensor_data, sensor_data, t)
                
                # Add to stroke
                if self.stroke:
                    self.stroke.add_point(interp_x, interp_y, interp_sensor)
                
                # Stamp
                self._stamp_at_point(interp_x, interp_y, interp_sensor, current_frame)
        else:
            # Points too close - stamp current point
            if self.stroke:
                self.stroke.add_point(x, y, sensor_data)
            self._stamp_at_point(x, y, sensor_data, current_frame)
        
        # Update state
        self.last_point = (x, y)
        self.last_sensor_data = sensor_data
        self.last_stamp_time = current_time
    
    def on_release(self, event, canvas: Canvas, x: float, y: float):
        """
        Finish brush stroke.
        
        Args:
            event: RV event with input data
            canvas: Canvas to draw on
            x, y: Normalized coordinates (0-1)
        """
        if not self.is_drawing:
            return
        
        # Final drag to current point
        if self.last_point:
            self.on_drag(event, canvas, x, y)
        
        # End stroke
        self.is_drawing = False
        if self.renderer:
            self.renderer.end_stroke()
        if canvas:
            canvas.end_stroke()
        
        # Reset state
        self.last_point = None
        self.last_sensor_data = None
        self.stroke = None
        self.accumulated_distance = 0.0
    
    def _read_sensors(
        self,
        event,
        x: float,
        y: float,
        speed: float,
        distance: float
    ) -> SensorData:
        """
        Read sensor data from event.
        
        Args:
            event: RV event
            x, y: Current position
            speed: Current drawing speed
            distance: Accumulated distance
        
        Returns:
            SensorData with all sensor readings
        """
        sensor_data = SensorData()
        
        # Position
        sensor_data.x = x
        sensor_data.y = y
        
        # Pressure (from event if available)
        if hasattr(event, 'pressure'):
            try:
                pressure = event.pressure()
                sensor_data.pressure = max(0.0, min(1.0, pressure))
            except:
                sensor_data.pressure = 1.0
        else:
            sensor_data.pressure = 1.0
        
        # Tilt (from event if available)
        if hasattr(event, 'tilt'):
            try:
                tilt = event.tilt()
                if tilt and len(tilt) >= 2:
                    sensor_data.tilt_x = tilt[0]
                    sensor_data.tilt_y = tilt[1]
            except:
                pass
        
        # Rotation (from event if available)
        if hasattr(event, 'rotation'):
            try:
                sensor_data.rotation = event.rotation()
            except:
                pass
        
        # Speed (calculated)
        sensor_data.speed = speed
        
        # Distance (accumulated)
        sensor_data.distance = distance
        
        # Time (since stroke start)
        sensor_data.time = time.time() - self.stroke_start_time
        
        return sensor_data
    
    def _stamp_at_point(self, x: float, y: float, sensor_data: SensorData, frame: int):
        """
        Stamp brush at point using renderer.
        
        Args:
            x, y: Normalized coordinates
            sensor_data: Sensor readings
            frame: Frame number
        """
        if not self.renderer or not self.current_preset:
            return
        
        # Calculate modulated brush parameters
        size = self._apply_sensor_modulation(
            self.current_preset.size,
            self.current_preset.size_modulation,
            sensor_data
        )
        
        opacity = self._apply_sensor_modulation(
            self.current_preset.opacity,
            self.current_preset.opacity_modulation,
            sensor_data
        )
        
        # Apply flow (affects accumulation, not direct opacity)
        flow = self._apply_sensor_modulation(
            self.current_preset.flow,
            self.current_preset.flow_modulation,
            sensor_data
        )
        
        # Adjust opacity by flow
        effective_opacity = opacity * flow
        
        # Stamp brush
        self.renderer.stamp_brush(
            x, y,
            size,
            effective_opacity,
            self.current_preset.color,
            self.current_preset.hardness,
            frame
        )
    
    def _apply_sensor_modulation(
        self,
        base_value: float,
        sensor_configs: list,
        sensor_data: SensorData
    ) -> float:
        """
        Apply sensor modulation to parameter.
        
        Args:
            base_value: Base parameter value
            sensor_configs: List of SensorConfig
            sensor_data: Current sensor readings
        
        Returns:
            Modulated value
        """
        value = base_value
        
        for config in sensor_configs:
            if not config.enabled:
                continue
            
            # Get sensor
            sensor_type = config.sensor_type
            if sensor_type not in self.sensors:
                continue
            
            sensor = self.sensors[sensor_type]
            
            # Get sensor value
            sensor_value = sensor.compute(sensor_data)
            
            # Apply strength and curve
            modulation = 1.0 + (sensor_value - 1.0) * config.strength
            
            # Multiply modulation
            value *= modulation
        
        return max(0.0, value)
    
    def _calculate_interpolation_factor(
        self,
        x1: float, y1: float,
        xi: float, yi: float,
        x2: float, y2: float
    ) -> float:
        """
        Calculate interpolation factor for intermediate point.
        
        Args:
            x1, y1: Start point
            xi, yi: Intermediate point
            x2, y2: End point
        
        Returns:
            Interpolation factor 0-1
        """
        # Calculate distances
        dist_start = math.sqrt((xi - x1) ** 2 + (yi - y1) ** 2)
        dist_total = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        if dist_total < 0.0001:
            return 0.5
        
        return dist_start / dist_total
    
    def _interpolate_sensor_data(
        self,
        data1: SensorData,
        data2: SensorData,
        t: float
    ) -> SensorData:
        """
        Interpolate between two sensor data points.
        
        Args:
            data1: Start sensor data
            data2: End sensor data
            t: Interpolation factor (0-1)
        
        Returns:
            Interpolated SensorData
        """
        result = SensorData()
        
        result.pressure = lerp(data1.pressure, data2.pressure, t)
        result.tilt_x = lerp(data1.tilt_x, data2.tilt_x, t)
        result.tilt_y = lerp(data1.tilt_y, data2.tilt_y, t)
        result.rotation = lerp(data1.rotation, data2.rotation, t)
        result.speed = lerp(data1.speed, data2.speed, t)
        result.distance = lerp(data1.distance, data2.distance, t)
        result.time = lerp(data1.time, data2.time, t)
        result.x = lerp(data1.x, data2.x, t)
        result.y = lerp(data1.y, data2.y, t)
        
        return result

