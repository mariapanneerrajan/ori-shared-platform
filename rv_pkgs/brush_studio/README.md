# Brush Studio for OpenRV

Professional GPU-accelerated raster brush painting system with full pressure sensitivity support.

## Features

- **GPU FBO-based rendering** for lag-free performance (60+ FPS with 100+ strokes)
- **12 diverse brush tips**: soft/hard circles, squares, triangle, diamond, star, splatter, stipple, grainy, scratchy, noise
- **Full sensor system**: pressure, tilt, rotation, speed, distance, time
- **10 essential brush presets**: Basic, Soft, Airbrush, Pencil, Ink, Erasers, Charcoal, Marker, Watercolor
- **Pressure-sensitive painting** with accurate opacity and width modulation
- **Coordinate transformation** ensures strokes stick to image during pan/zoom/rotate
- **Per-frame canvas management** with automatic persistence
- **F8 hotkey** for quick toggle on/off
- **Visual brush tip selector** with thumbnail previews

## Installation

1. Copy the `brush_studio` directory to your RV packages directory:
   - Linux/Mac: `~/.rv/Packages/`
   - Windows: `%USERPROFILE%\.rv\Packages\`

2. Or install via RV Package Manager:
   - Package → Manage → Add → Browse to `brush_studio` directory

3. Restart OpenRV

## Usage

### Quick Start

1. Press **F8** to toggle Brush Studio on/off (or use **Tools → Brush Studio** menu)
2. Select a brush tip shape from the top section
3. Select a brush preset from the panel
4. Adjust size, opacity, hardness, flow, and color as needed
5. Draw with mouse or pressure-sensitive stylus (Wacom, etc.)
6. Strokes automatically stick to image during viewport manipulation
7. Click **Clear Frame** button at bottom to erase all strokes on current frame

### Usage Notes

- Press **F8** or use **Tools → Brush Studio** menu to toggle on/off
- Mouse/Stylus events are captured when mode is active
- Selected brush tip applies to all presets (global override)
- Color and tip selections persist across preset changes
- Use **Clear Frame** button to clear current frame

### Brush Presets

1. **Basic** - Hard-edged brush with strong pressure on size
2. **Soft** - Soft-edged brush, great for blending
3. **Airbrush** - Very soft with low flow for airbrushing effects
4. **Pencil** - Small textured brush for sketching
5. **Ink** - Hard-edged ink pen, only opacity pressure
6. **Eraser Hard** - Hard-edged eraser
7. **Eraser Soft** - Soft-edged eraser
8. **Charcoal** - Textured with tilt support
9. **Marker** - High flow marker for bold strokes
10. **Watercolor** - Very soft with low flow for watercolor effects

### Brush Parameters

- **Size**: Brush size in pixels (1-100)
- **Opacity**: Overall opacity (0-100%)
- **Hardness**: Edge softness (0-100%, 0=very soft, 100=hard edge)
- **Flow**: Paint accumulation rate (0-100%)

### Pressure Sensitivity

All presets support pressure sensitivity for various parameters:
- Most affect **size** and **opacity** based on stylus pressure
- Some affect **flow** for accumulation effects
- Charcoal supports **tilt** for width and rotation
- Pencil uses **speed** for opacity variation

## Architecture

```
BrushStudioMode (MinorMode entry point)
├── Canvas (frame-based stroke storage)
├── BrushRenderer (GPU rendering engine)
│   ├── FBOManager (per-frame framebuffers)
│   ├── ShaderManager (GLSL shader programs)
│   └── BrushTextureGenerator (procedural textures)
├── RasterBrushTool (stroke input handling)
│   └── Sensors (6 sensor types for dynamics)
├── PresetManager (brush configurations)
└── UI (Qt panels)
```

## Performance

- **GPU-accelerated**: All rendering happens on GPU using OpenGL FBOs
- **Single draw call per frame**: Entire canvas rendered as one textured quad
- **LRU caching**: Keeps 50 frames in memory for instant switching
- **Expected performance**: 60+ FPS with hundreds of strokes per frame

## File Storage

Canvas data is automatically saved to:
```
~/.rv/BrushStudio/<session_id>/frame_NNNNNN.png
```

Each frame is saved as a PNG file with RGBA channels for easy export/backup.

## Technical Details

### Coordinate System

Uses normalized itview space (0.0-1.0) for resolution-independent coordinates:
- Strokes automatically transform with viewport pan/zoom/rotate
- Same coordinate system as vector_draw package

### Sensor System

Modular sensor architecture inspired by Krita:
- **PressureSensor**: Stylus pressure (0-1)
- **TiltSensor**: Stylus tilt angle
- **RotationSensor**: Barrel rotation (0-360°)
- **SpeedSensor**: Drawing velocity (pixels/sec)
- **DistanceSensor**: Accumulated stroke distance
- **TimeSensor**: Time since stroke start

### GPU Rendering Pipeline

1. **FBO Creation**: Create offscreen framebuffer per frame (lazy)
2. **Brush Stamping**: Render brush quads to FBO with shader
3. **Accumulation**: Alpha blending composites strokes
4. **Display**: Render FBO texture as screen-aligned quad

## Requirements

- OpenRV 3.0.0+
- Python 3.7+
- PyOpenGL
- PySide2 or PySide6 (included with RV)
- PIL/Pillow (optional, for canvas persistence)

## Known Limitations

- UI is simplified (functional but not fancy)
- No undo/redo (yet)
- No brush preview cursor (yet)
- Eraser uses white color instead of blend mode

## Future Enhancements

- Undo/redo system
- Brush preview cursor
- Custom brush texture import
- Blend modes for eraser
- Brush library with more presets
- Curve editor for sensor dynamics
- Brush size by keyboard shortcuts
- Export canvas as image sequence

## Credits

Developed using proven patterns from vector_draw package.
GPU rendering inspired by "Efficient Rendering of Linear Brush Strokes" paper.
Sensor system architecture inspired by Krita's paintop system.

## License

Apache-2.0

## Version

1.0.0

