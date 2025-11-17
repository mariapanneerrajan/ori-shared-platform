"""
Brush Studio - Main RV MinorMode Entry Point

Professional raster brush painting system for OpenRV with GPU acceleration.
"""

import rv.commands as rvc
import rv.rvtypes as rvt
import rv.qtutils
from OpenGL.GL import *
from OpenGL.GLU import *

try:
    from PySide6.QtWidgets import QDockWidget
    from PySide6.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QDockWidget
    from PySide2.QtCore import Qt

# Ensure package path
import sys
from pathlib import Path
pkg_root = Path(__file__).resolve().parent
if str(pkg_root.parent) not in sys.path:
    sys.path.insert(0, str(pkg_root.parent))

from brush_studio.models.canvas import Canvas
from brush_studio.models.brush_preset import BrushPreset
from brush_studio.rendering.brush_renderer import BrushRenderer
from brush_studio.tools.raster_brush_tool import RasterBrushTool
from brush_studio.presets.preset_manager import PresetManager
from brush_studio.ui.brush_studio_panel import BrushStudioPanel
from brush_studio.persistence.canvas_storage import CanvasStorage
from brush_studio.utils.coordinate_transform import screen_to_itview


class BrushStudioMode(rvt.MinorMode):
    """
    Main mode for Brush Studio.
    
    Provides GPU-accelerated raster brush painting with full sensor support.
    """
    
    def __init__(self):
        rvt.MinorMode.__init__(self)
        
        self.init(
            "Brush Studio",
            [
                ("brush-studio-toggle", self.toggle, "Toggle Brush Studio"),
                ("render", self.render, "Render brush strokes"),
                ("frame-changed", self.on_frame_changed, "Frame changed"),
                # Mouse/stylus events
                ("pointer-1--push", self.mouse_press, "Mouse press"),
                ("pointer-1--drag", self.mouse_drag, "Mouse drag"),
                ("pointer-1--release", self.mouse_release, "Mouse release"),
                ("stylus-pen--push", self.mouse_press, "Stylus press"),
                ("stylus-pen--drag", self.mouse_drag, "Stylus drag"),
                ("stylus-pen--release", self.mouse_release, "Stylus release"),
            ],
            [
                ("key-down--F8", self.toggle, "Toggle Brush Studio with F8"),
            ],
            [
                ("Tools", [
                    ("_", None, None, None),
                    ("Brush Studio", self.toggle, None, None),
                ])
            ]
        )
        
        # Components
        self.canvas = Canvas()
        self.canvas.current_frame = 0
        self.renderer = BrushRenderer()
        self.tool = RasterBrushTool()
        self.tool.renderer = self.renderer
        self.preset_manager = PresetManager()
        self.storage = CanvasStorage()
        
        # UI
        self.dock_widget = None
        self.panel = None
        
        # State
        self.current_frame = 0
        self.is_drawing = False
        self.user_selected_color = (0.0, 0.0, 0.0, 1.0)  # User's chosen color (persists across presets)
        self.user_selected_tip = 'soft_circle'  # User's chosen brush tip (persists across presets)
        
        # Set default preset
        basic_preset = self.preset_manager.get_preset("Basic")
        if basic_preset:
            # Apply user's selected tip to initial preset
            basic_preset.texture_type = self.user_selected_tip
            self.tool.set_preset(basic_preset)
    
    def toggle(self, event=None):
        """Toggle brush studio on/off."""
        if self.isActive():
            self.deactivate()
        else:
            self.activate()
        rvc.redraw()
    
    def activate(self):
        """Activate mode."""
        if not self.isActive():
            super().activate()
        
        # Create UI if needed
        if self.dock_widget is None:
            self.create_ui()
        
        # Show UI
        if self.dock_widget:
            self.dock_widget.show()
            self.dock_widget.raise_()
        
        # Load current frame
        self.current_frame = rvc.frame()
        self.canvas.current_frame = self.current_frame
    
    def deactivate(self):
        """Deactivate mode."""
        if self.isActive():
            super().deactivate()
        
        # Hide UI
        if self.dock_widget:
            self.dock_widget.hide()
    
    def create_ui(self):
        """Create dockable UI."""
        try:
            main_window = rv.qtutils.sessionWindow()
            
            self.dock_widget = QDockWidget("Brush Studio", main_window)
            self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            
            self.panel = BrushStudioPanel()
            self.panel.preset_changed.connect(self.on_preset_changed)
            self.panel.size_changed.connect(self.on_size_changed)
            self.panel.opacity_changed.connect(self.on_opacity_changed)
            self.panel.hardness_changed.connect(self.on_hardness_changed)
            self.panel.flow_changed.connect(self.on_flow_changed)
            self.panel.color_changed.connect(self.on_color_changed)
            self.panel.tip_changed.connect(self.on_tip_changed)
            self.panel.clear_frame_requested.connect(self.clear_frame)
            self.panel.save_requested.connect(self.save_annotations)
            self.panel.open_requested.connect(self.open_annotations)
            
            # Initialize tip selector with current user selection
            if self.panel.tip_selector:
                self.panel.tip_selector.set_selected_tip(self.user_selected_tip)
            
            self.dock_widget.setWidget(self.panel)
            main_window.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
            
            # Don't show dock widget here - let activate() handle it
            self.dock_widget.hide()
        except Exception as e:
            pass  # UI creation failed silently
    
    def render(self, event):
        """Render brush strokes."""
        if not self.isActive():
            return
        
        try:
            # Get source
            sources = rvc.sourcesAtFrame(rvc.frame())
            if len(sources) != 1:
                return
            
            # Get viewport dimensions and setup projection
            domain = event.domain()
            width = domain[0]
            height = domain[1]
            
            # Setup OpenGL projection for 2D drawing
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0.0, width, 0.0, height, -1.0, 1.0)
            
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            # Set source transform
            self.renderer.set_source_transform(sources[0])
            
            # Render frame
            self.renderer.render_frame(self.current_frame)
            
            # Restore matrices
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            
        except Exception as e:
            pass  # Render error silently
    
    def on_frame_changed(self, event):
        """Handle frame change."""
        if not self.isActive():
            return
        
        self.current_frame = rvc.frame()
        self.canvas.current_frame = self.current_frame
        rvc.redraw()
    
    def mouse_press(self, event):
        """Handle mouse/stylus press."""
        if not self.isActive():
            event.reject()
            return
        
        try:
            x, y = self._get_image_coords(event)
            if self.tool.current_preset is None:
                event.reject()
                return
            self.tool.on_press(event, self.canvas, x, y)
            self.is_drawing = True
            rvc.redraw()
        except Exception as e:
            event.reject()
    
    def mouse_drag(self, event):
        """Handle mouse/stylus drag."""
        if not self.isActive() or not self.is_drawing:
            event.reject()
            return
        
        try:
            x, y = self._get_image_coords(event)
            self.tool.on_drag(event, self.canvas, x, y)
            rvc.redraw()
        except Exception as e:
            pass
    
    def mouse_release(self, event):
        """Handle mouse/stylus release."""
        if not self.isActive():
            event.reject()
            return
        
        try:
            x, y = self._get_image_coords(event)
            self.tool.on_release(event, self.canvas, x, y)
            self.is_drawing = False
            rvc.redraw()
        except Exception as e:
            pass
    
    def _get_image_coords(self, event):
        """Get normalized image coordinates from event."""
        pointer = event.pointer()
        
        # Apply device pixel ratio
        try:
            state = rvc.data()
            dpr = state.devicePixelRatio if hasattr(state, 'devicePixelRatio') else 1.0
        except:
            dpr = 1.0
        
        event_x = pointer[0] * dpr
        event_y = pointer[1] * dpr
        
        # Get source geometry
        sources = rvc.sourcesAtFrame(rvc.frame())
        if len(sources) != 1:
            return (0.5, 0.5)
        
        try:
            geometry = rvc.imageGeometry(sources[0])
            norm_x, norm_y = screen_to_itview(geometry, event_x, event_y)
            return (norm_x, norm_y)
        except:
            return (0.5, 0.5)
    
    def clear_frame(self, event=None):
        """Clear current frame."""
        self.renderer.clear_frame(self.current_frame)
        self.canvas.clear_frame(self.current_frame)
        rvc.redraw()
    
    def on_preset_changed(self, preset_name):
        """Handle preset selection."""
        preset = self.preset_manager.get_preset(preset_name)
        if preset:
            self.tool.set_preset(preset)
            
            # Apply user's selected color (don't reset to preset default)
            preset.color = self.user_selected_color
            
            # Apply user's selected tip (global override)
            preset.texture_type = self.user_selected_tip
            
            # Update UI with preset values (using user's color, not preset default)
            if self.panel:
                self.panel.update_parameters(
                    preset.size,
                    preset.opacity,
                    preset.hardness,
                    preset.flow,
                    self.user_selected_color  # Use user's color, not preset.color
                )
                self.panel.update_sensor_display(preset)
    
    def on_tip_changed(self, texture_type):
        """
        Handle brush tip selection.
        
        Args:
            texture_type: Type of texture that was selected
        """
        self.user_selected_tip = texture_type
        if self.tool.current_preset:
            self.tool.current_preset.texture_type = texture_type
            # Clear any cached textures in renderer to force regeneration
            if self.tool.renderer and hasattr(self.tool.renderer, 'brush_textures'):
                # Don't clear cache, just ensure the preset is updated
                pass
    
    def on_size_changed(self, size):
        """Handle size change."""
        if self.tool.current_preset:
            self.tool.current_preset.size = size
    
    def on_opacity_changed(self, opacity):
        """Handle opacity change."""
        if self.tool.current_preset:
            self.tool.current_preset.opacity = opacity
    
    def on_hardness_changed(self, hardness):
        """Handle hardness change."""
        if self.tool.current_preset:
            self.tool.current_preset.hardness = hardness
    
    def on_flow_changed(self, flow):
        """Handle flow change."""
        if self.tool.current_preset:
            self.tool.current_preset.flow = flow
    
    def on_color_changed(self, color):
        """Handle color change."""
        # Store user's selected color (persists across preset changes)
        self.user_selected_color = color
        
        # Apply to current preset
        if self.tool.current_preset:
            self.tool.current_preset.color = color
    
    def save_annotations(self):
        """Save all annotations to JSON file."""
        try:
            from PySide2.QtWidgets import QFileDialog
        except ImportError:
            from PySide6.QtWidgets import QFileDialog
        
        import json
        from pathlib import Path
        
        try:
            # Get save file path
            main_window = rv.qtutils.sessionWindow()
            file_path, _ = QFileDialog.getSaveFileName(
                main_window,
                "Save Annotations",
                str(Path.home() / "brush_studio_annotations.json"),
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Serialize canvas data
            data = {
                "version": "1.0",
                "frames": {}
            }
            
            for frame_num in self.canvas.get_all_frames():
                strokes = self.canvas.get_strokes(frame_num)
                frame_data = []
                
                for stroke in strokes:
                    stroke_data = {
                        "preset_name": stroke.preset_name,
                        "color": list(stroke.color),  # Convert tuple to list for JSON
                        "texture_type": stroke.texture_type,
                        "size": stroke.size,
                        "opacity": stroke.opacity,
                        "hardness": stroke.hardness,
                        "flow": stroke.flow,
                        "start_time": stroke.start_time,
                        "end_time": stroke.end_time,
                        "points": []
                    }
                    
                    for point in stroke.points:
                        point_data = {
                            "x": point.x,
                            "y": point.y,
                            "sensor": {
                                "pressure": point.sensor_data.pressure,
                                "tilt_x": point.sensor_data.tilt_x,
                                "tilt_y": point.sensor_data.tilt_y,
                                "rotation": point.sensor_data.rotation,
                                "speed": point.sensor_data.speed,
                                "distance": point.sensor_data.distance,
                                "time": point.sensor_data.time,
                                "timestamp": point.sensor_data.timestamp
                            }
                        }
                        stroke_data["points"].append(point_data)
                    
                    frame_data.append(stroke_data)
                
                data["frames"][str(frame_num)] = frame_data
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            pass  # Silent failure
    
    def open_annotations(self):
        """Load annotations from JSON file."""
        try:
            from PySide2.QtWidgets import QFileDialog
        except ImportError:
            from PySide6.QtWidgets import QFileDialog
        
        import json
        from pathlib import Path
        from brush_studio.models.brush_stroke import BrushStroke, StrokePoint
        from brush_studio.models.sensor_data import SensorData
        
        try:
            # Get open file path
            main_window = rv.qtutils.sessionWindow()
            file_path, _ = QFileDialog.getOpenFileName(
                main_window,
                "Open Annotations",
                str(Path.home()),
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Load JSON
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear current canvas
            self.canvas.clear_all()
            self.renderer.fbo_manager.clear_all()
            
            # Reconstruct strokes and replay through renderer
            for frame_str, frame_strokes in data.get("frames", {}).items():
                frame_num = int(frame_str)
                
                for stroke_data in frame_strokes:
                    # Get preset for this stroke (for sensor modulation settings)
                    preset = self.preset_manager.get_preset(stroke_data["preset_name"])
                    if not preset:
                        preset = self.preset_manager.get_preset("Basic")
                    
                    # Get saved properties or use defaults
                    saved_color = tuple(stroke_data.get("color", [0.0, 0.0, 0.0, 1.0]))
                    if len(saved_color) == 4:
                        stroke_color = saved_color
                    else:
                        stroke_color = (0.0, 0.0, 0.0, 1.0)
                    
                    saved_texture_type = stroke_data.get("texture_type", "soft_circle")
                    saved_size = stroke_data.get("size", 25.0)
                    saved_opacity = stroke_data.get("opacity", 1.0)
                    saved_hardness = stroke_data.get("hardness", 0.5)
                    saved_flow = stroke_data.get("flow", 1.0)
                    
                    # Create a temporary preset with saved values for rendering
                    # (We need to do this because the renderer uses preset properties)
                    preset.color = stroke_color
                    preset.texture_type = saved_texture_type
                    preset.size = saved_size
                    preset.opacity = saved_opacity
                    preset.hardness = saved_hardness
                    preset.flow = saved_flow
                    
                    # Create stroke object with all saved properties
                    stroke = BrushStroke(
                        preset_name=stroke_data["preset_name"],
                        color=stroke_color,
                        texture_type=saved_texture_type,
                        size=saved_size,
                        opacity=saved_opacity,
                        hardness=saved_hardness,
                        flow=saved_flow,
                        frame=frame_num,
                        start_time=stroke_data.get("start_time", 0.0),
                        end_time=stroke_data.get("end_time", 0.0)
                    )
                    
                    # Recreate points
                    for point_data in stroke_data["points"]:
                        sensor = SensorData(
                            pressure=point_data["sensor"]["pressure"],
                            tilt_x=point_data["sensor"]["tilt_x"],
                            tilt_y=point_data["sensor"]["tilt_y"],
                            rotation=point_data["sensor"]["rotation"],
                            speed=point_data["sensor"]["speed"],
                            distance=point_data["sensor"]["distance"],
                            time=point_data["sensor"]["time"],
                            timestamp=point_data["sensor"]["timestamp"]
                        )
                        stroke.add_point(point_data["x"], point_data["y"], sensor)
                    
                    # Add stroke to canvas
                    if frame_num not in self.canvas.strokes_by_frame:
                        self.canvas.strokes_by_frame[frame_num] = []
                    self.canvas.strokes_by_frame[frame_num].append(stroke)
                    
                    # Replay stroke through renderer to recreate FBO
                    self.renderer.set_source_transform(rvc.sources()[0] if rvc.sources() else None)
                    self.renderer.begin_stroke(preset, frame_num)
                    
                    for point in stroke.points:
                        # Calculate modulated values
                        size = preset.size
                        opacity = preset.opacity
                        flow = preset.flow
                        
                        # Apply sensor modulation
                        for mod in preset.size_modulation:
                            if mod.enabled:
                                sensor_val = getattr(point.sensor_data, mod.sensor_type, 0.0)
                                size *= (1.0 + (sensor_val - 0.5) * 2.0 * mod.strength)
                        
                        for mod in preset.opacity_modulation:
                            if mod.enabled:
                                sensor_val = getattr(point.sensor_data, mod.sensor_type, 0.0)
                                opacity *= sensor_val ** (1.0 / max(0.1, mod.strength))
                        
                        # Stamp to renderer using the saved stroke color
                        self.renderer.stamp_brush(
                            point.x, point.y,
                            max(1.0, size),
                            opacity,
                            stroke.color,  # Use saved color from stroke
                            preset.hardness,
                            frame_num
                        )
                    
                    self.renderer.end_stroke()
            
            # Redraw
            rvc.redraw()
            
        except Exception as e:
            pass  # Silent failure


def createMode():
    """Factory function called by RV to create mode."""
    return BrushStudioMode()

