# Brush Studio Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      BrushStudioMode                            │
│                   (RV MinorMode Entry Point)                    │
│  - Event handling (mouse, stylus, render, frame-changed)       │
│  - Coordinate transformation                                    │
│  - Component orchestration                                      │
└──────────┬──────────────────────────────────────────┬───────────┘
           │                                          │
           ├──────────────────┬───────────────────────┤
           │                  │                       │
           ▼                  ▼                       ▼
    ┌──────────┐      ┌──────────────┐      ┌──────────────┐
    │  Canvas  │      │ BrushRenderer│      │ BrushTool    │
    └──────────┘      └──────────────┘      └──────────────┘
           │                  │                       │
           │                  │                       │
           ▼                  ▼                       ▼
    ┌──────────┐      ┌──────────────┐      ┌──────────────┐
    │ Strokes  │      │  FBOManager  │      │   Sensors    │
    │Per-Frame │      │  (GPU FBOs)  │      │   (6 types)  │
    └──────────┘      └──────────────┘      └──────────────┘
                              │
                              ├──────────────┬────────────────┐
                              ▼              ▼                ▼
                       ┌───────────┐  ┌───────────┐  ┌───────────┐
                       │  Shader   │  │  Texture  │  │   FBO     │
                       │  Manager  │  │ Generator │  │  Cache    │
                       └───────────┘  └───────────┘  └───────────┘
```

## Component Responsibilities

### BrushStudioMode (Main Controller)
**File**: `brush_studio_mode.py`

**Responsibilities**:
- RV MinorMode entry point
- Event routing (mouse, stylus, render, frame change)
- Coordinate transformation (screen → normalized itview space)
- Component lifecycle management
- UI integration

**Key Methods**:
- `mouse_press()`, `mouse_drag()`, `mouse_release()` - Input handling
- `render()` - Frame rendering callback
- `_get_image_coords()` - Screen to normalized space conversion

---

### Canvas (Data Model)
**File**: `models/canvas.py`

**Responsibilities**:
- Frame-based stroke storage
- Current stroke management
- Per-frame stroke queries

**Data Structure**:
```python
{
    frame_1: [stroke1, stroke2, ...],
    frame_2: [stroke3, stroke4, ...],
    ...
}
```

---

### BrushRenderer (Rendering Engine)
**File**: `rendering/brush_renderer.py`

**Responsibilities**:
- GPU rendering coordination
- FBO management for frames
- Shader program execution
- Brush stamping to FBO
- Final compositing to screen

**Rendering Pipeline**:
1. Get/Create FBO for current frame
2. Bind FBO for offscreen rendering
3. Stamp brush using shader
4. Accumulate via alpha blending
5. Render FBO texture to screen

---

### FBOManager (GPU Memory Manager)
**File**: `rendering/fbo_manager.py`

**Responsibilities**:
- Per-frame FBO creation
- LRU caching (max 50 frames)
- GPU memory management
- Texture lifecycle

**Cache Strategy**:
- Lazy creation (on first stroke)
- LRU eviction (oldest first)
- Automatic size adjustment

---

### ShaderManager (GLSL Compiler)
**File**: `rendering/shader_manager.py`

**Responsibilities**:
- GLSL shader compilation
- Shader program caching
- Uniform management
- Error handling

**Shader Programs**:
1. **brush_stamp** - Renders brush quads with soft/hard edges
2. **composite** - Final screen compositing (optional)

---

### RasterBrushTool (Interaction Handler)
**File**: `tools/raster_brush_tool.py`

**Responsibilities**:
- Stroke input processing
- Sensor data reading
- Point interpolation (spacing-based)
- Brush parameter modulation
- Renderer coordination

**Stroke Processing**:
1. Read sensor data from event
2. Calculate speed, distance, time
3. Interpolate points based on spacing
4. Apply sensor modulation to parameters
5. Stamp brush via renderer

---

### Sensor System (Dynamics Engine)
**Files**: `sensors/*.py`

**Responsibilities**:
- Input data reading
- Normalized value computation (0-1)
- Dynamics curve application
- Parameter modulation

**Sensor Types**:
1. **PressureSensor** - Stylus pressure (0-1)
2. **TiltSensor** - Stylus tilt angles
3. **RotationSensor** - Barrel rotation (0-360°)
4. **SpeedSensor** - Drawing velocity
5. **DistanceSensor** - Accumulated distance
6. **TimeSensor** - Time since stroke start

---

### BrushPreset (Configuration)
**File**: `models/brush_preset.py`

**Responsibilities**:
- Brush parameter storage
- Sensor modulation configuration
- JSON serialization/deserialization

**Parameters**:
- Base: size, opacity, flow, hardness, spacing, color
- Sensors: per-parameter modulation configs

---

### PresetManager (Preset Library)
**File**: `presets/preset_manager.py`

**Responsibilities**:
- Preset loading from JSON
- Preset lookup by name
- Preset saving

**Presets**:
10 JSON files in `presets/` directory

---

## Data Flow

### 1. Input Event → Stroke Point

```
Input Event (mouse/stylus)
    ↓
BrushStudioMode._get_image_coords()
    ↓
screen_to_itview() [normalized coordinates]
    ↓
RasterBrushTool.on_press/drag/release()
    ↓
Sensor data reading (pressure, tilt, rotation, speed, distance, time)
    ↓
Stroke point with sensor data
```

### 2. Stroke Point → GPU Rendering

```
Stroke point + sensor data
    ↓
RasterBrushTool._apply_sensor_modulation()
    ↓
Modulated parameters (size, opacity, flow)
    ↓
BrushRenderer.stamp_brush()
    ↓
FBOManager.get_or_create_fbo(frame)
    ↓
Shader execution (brush_stamp.vert + brush_stamp.frag)
    ↓
GPU FBO accumulation
```

### 3. Frame Rendering → Display

```
RV render event
    ↓
BrushStudioMode.render()
    ↓
BrushRenderer.render_frame()
    ↓
Get FBO for current frame
    ↓
Bind FBO texture
    ↓
Render screen-aligned quad with itview transform
    ↓
Display (strokes stick to image during pan/zoom/rotate)
```

---

## Coordinate Spaces

### 1. Screen Space
- Raw pixel coordinates from input events
- Device pixel ratio applied
- Origin: varies by platform

### 2. Normalized itview Space (0.0-1.0)
- Resolution-independent
- Used for all brush strokes
- Origin: bottom-left (0, 0), top-right (1, 1)
- **Key feature**: Automatically transforms with viewport

### 3. FBO Texture Space
- Internal GPU texture coordinates
- Matches source image resolution
- Used for brush stamping

### Transformations

```
screen_to_itview():
    screen coords → normalized coords (0-1)
    Uses rvc.imageGeometry() for current transform

itview_to_screen():
    normalized coords → screen coords
    For rendering FBO texture to display

image_to_itview():
    image pixels → normalized coords
    For brush size conversion
```

---

## GPU Rendering Pipeline

### Offscreen Rendering (Stroke Stamping)

```
1. Get/Create FBO for frame
   └─ RGBA32F texture (high precision)
   └─ Framebuffer object

2. Bind FBO
   └─ Redirect rendering to texture

3. Setup blending
   └─ GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA

4. Use brush_stamp shader
   └─ Vertex shader: positions brush quad
   └─ Fragment shader: soft/hard edge, opacity

5. Draw quad at brush center
   └─ Size modulated by pressure
   └─ Opacity modulated by pressure

6. Unbind FBO
   └─ Stroke accumulated in texture
```

### Onscreen Rendering (Display)

```
1. Get FBO for current frame

2. Bind FBO texture

3. Calculate screen-aligned quad corners
   └─ Uses itview_to_screen() with current geometry
   └─ Automatically handles pan/zoom/rotate

4. Render textured quad
   └─ GL_TEXTURE_2D with FBO texture
   └─ GL_BLEND for transparency

5. Result: Strokes stick to image
```

---

## Memory Management

### FBO Cache (LRU)

```
Max cached frames: 50
Per-frame memory: ~32MB (1920x1080 RGBA32F)
Total max memory: ~1.6GB

Eviction strategy:
- Track last access time
- When cache full, remove oldest
- Lazy creation (only on first stroke)

Frame switching:
- Instant (no re-render needed)
- FBO already contains accumulated strokes
```

---

## Performance Characteristics

### Stroke Rendering
- **Complexity**: O(1) per stamp
- **GPU operations**: 1 draw call per stamp
- **Bottleneck**: Fragment shader (parallelized on GPU)

### Frame Rendering
- **Complexity**: O(1) regardless of stroke count
- **GPU operations**: 1 draw call per frame
- **Bottleneck**: Texture sampling (very fast)

### Expected Performance
- **Stamping**: 1000+ stamps/sec
- **Display**: 60+ FPS with 100+ strokes/frame
- **Memory**: Linear with cached frame count

---

## Extension Points

### Adding New Sensors
1. Create subclass of `BaseSensor`
2. Implement `compute(sensor_data) -> float`
3. Add to `RasterBrushTool.sensors` dict
4. Use in preset JSON files

### Adding New Brush Textures
1. Add method to `BrushTextureGenerator`
2. Generate OpenGL texture
3. Reference in preset's `texture_type`

### Adding New Presets
1. Create JSON file in `presets/`
2. Configure parameters and sensor modulation
3. PresetManager auto-loads on startup

### Adding UI Controls
1. Add widget to `BrushStudioPanel`
2. Connect signal to mode method
3. Update preset parameters

---

## SOLID Principles Application

### Single Responsibility
- ✅ Each class has one clear purpose
- Example: FBOManager only manages FBOs, not rendering

### Open/Closed
- ✅ Extensible without modification
- Example: Add sensors without changing BaseSensor

### Liskov Substitution
- ✅ All sensors can replace BaseSensor
- Example: Any sensor works in modulation system

### Interface Segregation
- ✅ Minimal, focused interfaces
- Example: Sensors only expose compute() and get_value()

### Dependency Inversion
- ✅ Depend on abstractions
- Example: RasterBrushTool depends on BaseSensor, not concrete sensors

---

## Summary

Brush Studio's architecture achieves:
- **Performance**: GPU-accelerated, lag-free painting
- **Flexibility**: Modular sensor system, extensible presets
- **Correctness**: Proper coordinate transforms, viewport handling
- **Maintainability**: Clean separation of concerns, SOLID principles
- **Scalability**: LRU caching, lazy initialization, efficient rendering

The system is production-ready and designed for professional use!

