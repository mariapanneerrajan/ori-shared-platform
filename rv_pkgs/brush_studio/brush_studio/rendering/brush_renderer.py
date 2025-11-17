"""
Main GPU rendering engine for brush strokes.

Coordinates FBOManager, ShaderManager, and brush textures to render
pressure-sensitive brush strokes to GPU framebuffers.
"""

from typing import Optional, List, Tuple
import numpy as np
from OpenGL.GL import *

try:
    import rv.commands as rvc
except ImportError:
    rvc = None

from brush_studio.rendering.fbo_manager import FBOManager, FBO
from brush_studio.rendering.shader_manager import ShaderManager
from brush_studio.rendering.brush_textures import BrushTextureGenerator
from brush_studio.utils.coordinate_transform import itview_to_screen


class BrushRenderer:
    """
    Main rendering engine for brush strokes.
    
    Uses GPU FBO-based accumulation for lag-free performance with many strokes.
    """
    
    def __init__(self):
        """Initialize brush renderer."""
        self.fbo_manager = FBOManager(max_cached_frames=50)
        self.shader_manager = ShaderManager()
        self.texture_generator = BrushTextureGenerator()
        
        # Shader programs (lazy initialization)
        self.brush_stamp_program: Optional[int] = None
        self.composite_program: Optional[int] = None
        
        # Current state
        self.source_name: Optional[str] = None
        self.geometry: Optional[List] = None
        self.current_frame: int = 0
        self.image_width: int = 1920
        self.image_height: int = 1080
        
        # Brush textures (lazy initialization)
        self.brush_textures: dict = {}
        
        # VBO for quad rendering
        self.quad_vbo: Optional[int] = None
        self.quad_vao: Optional[int] = None
        
        # Current stroke state
        self.is_drawing: bool = False
        self.current_preset = None
    
    def initialize_shaders(self):
        """Initialize shader programs."""
        if self.brush_stamp_program is None:
            self.brush_stamp_program = self.shader_manager.compile_shader_from_file(
                "brush_stamp.vert",
                "brush_stamp.frag",
                "brush_stamp"
            )
        
        # Note: composite shader not needed for initial implementation
        # (we'll render FBO texture directly)
    
    def initialize_quad_geometry(self):
        """Initialize quad geometry for rendering."""
        if self.quad_vao is not None:
            return  # Already initialized
        
        # Quad vertices (covering full normalized space 0-1)
        vertices = np.array([
            # Position (x, y)
            0.0, 0.0,
            1.0, 0.0,
            1.0, 1.0,
            0.0, 1.0,
        ], dtype=np.float32)
        
        # Create VAO and VBO
        self.quad_vao = glGenVertexArrays(1)
        self.quad_vbo = glGenBuffers(1)
        
        glBindVertexArray(self.quad_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.quad_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, ctypes.c_void_p(0))
        
        glBindVertexArray(0)
    
    def set_source_transform(self, source_name: str):
        """
        Set source and fetch current geometry for coordinate transformation.
        
        Args:
            source_name: RV source node name
        """
        self.source_name = source_name
        if rvc and source_name:
            try:
                # Get image geometry (4 corner points in screen space)
                self.geometry = rvc.imageGeometry(source_name)
                
                # Get image dimensions
                info = rvc.sourceImageInfo(source_name)
                if info and len(info) >= 2:
                    self.image_width = info[0]
                    self.image_height = info[1]
            except Exception:
                pass
    
    def begin_stroke(self, preset, frame: int):
        """
        Begin a new brush stroke.
        
        Args:
            preset: BrushPreset configuration
            frame: Current frame number
        """
        self.is_drawing = True
        self.current_preset = preset
        self.current_frame = frame
        
        # Initialize shaders if needed
        self.initialize_shaders()
        self.initialize_quad_geometry()
        
        # Get or create FBO for this frame
        fbo = self.fbo_manager.get_or_create_fbo(
            frame,
            self.image_width,
            self.image_height
        )
    
    def get_brush_texture(self, texture_type: str) -> int:
        """
        Get or create brush texture by type.
        
        Args:
            texture_type: Type of texture (e.g., 'soft_circle', 'star')
        
        Returns:
            OpenGL texture ID
        """
        # Check cache
        if texture_type in self.brush_textures:
            return self.brush_textures[texture_type]
        
        # Map texture type to generator method
        texture_generators = {
            'soft_circle': self.texture_generator.create_soft_circle,
            'hard_circle': self.texture_generator.create_hard_circle,
            'noise': self.texture_generator.create_noise_texture,
            'square_hard': self.texture_generator.create_square_hard,
            'square_soft': self.texture_generator.create_square_soft,
            'triangle': self.texture_generator.create_triangle,
            'star': self.texture_generator.create_star,
            'splatter': self.texture_generator.create_splatter,
            'stipple': self.texture_generator.create_stipple,
            'grainy': self.texture_generator.create_grainy,
            'scratchy': self.texture_generator.create_scratchy,
            'diamond': self.texture_generator.create_diamond,
        }
        
        # Get generator (with fallback to soft_circle)
        if texture_type not in texture_generators:
            texture_type = 'soft_circle'  # Fallback
        
        generator_func = texture_generators[texture_type]
        texture_id, _ = generator_func()
        
        # Cache texture
        self.brush_textures[texture_type] = texture_id
        
        return texture_id
    
    def stamp_brush(
        self,
        x: float,
        y: float,
        size: float,
        opacity: float,
        color: Tuple[float, float, float, float],
        hardness: float,
        frame: int
    ):
        """
        Stamp brush at given location to FBO.
        
        Args:
            x, y: Position in normalized itview space (0-1)
            size: Brush size in pixels
            opacity: Brush opacity (0-1)
            color: RGBA color tuple
            hardness: Edge hardness (0-1)
            frame: Frame number
        """
        # Get FBO for this frame
        fbo = self.fbo_manager.get_or_create_fbo(
            frame,
            self.image_width,
            self.image_height
        )
        
        # Bind FBO for rendering
        fbo.bind()
        
        # Setup blending for accumulation
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Use brush stamp shader
        self.shader_manager.use_program(self.brush_stamp_program)
        
        # Get and bind brush texture if current preset has one
        if self.current_preset and hasattr(self.current_preset, 'texture_type'):
            texture_id = self.get_brush_texture(self.current_preset.texture_type)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            use_texture = 1
        else:
            use_texture = 0
        
        # Setup orthographic projection (0-1 normalized space)
        projection = self._create_ortho_matrix(0, 1, 0, 1, -1, 1)
        self.shader_manager.set_uniform_matrix4(
            self.brush_stamp_program,
            "projection",
            projection
        )
        
        # Set uniforms
        self.shader_manager.set_uniform_vec4(
            self.brush_stamp_program,
            "brush_color",
            color
        )
        self.shader_manager.set_uniform_float(
            self.brush_stamp_program,
            "hardness",
            hardness
        )
        self.shader_manager.set_uniform_int(
            self.brush_stamp_program,
            "use_texture",
            use_texture
        )
        if use_texture:
            self.shader_manager.set_uniform_int(
                self.brush_stamp_program,
                "brush_texture",
                0  # Texture unit 0
            )
        
        # Convert size from pixels to normalized space
        size_norm = size / self.image_width
        
        # Create quad for brush stamp (centered at brush position)
        vertices = np.array([
            # Position (offset from center), brush_center, brush_size, brush_opacity
            -0.5, -0.5, x, y, size_norm, opacity,
            0.5, -0.5, x, y, size_norm, opacity,
            0.5, 0.5, x, y, size_norm, opacity,
            -0.5, 0.5, x, y, size_norm, opacity,
        ], dtype=np.float32)
        
        # Create temporary VBO for this stamp
        vbo = glGenBuffers(1)
        vao = glGenVertexArrays(1)
        
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STREAM_DRAW)
        
        # Setup vertex attributes
        stride = 6 * 4  # 6 floats per vertex
        glEnableVertexAttribArray(0)  # position
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)  # brush_center
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(2 * 4))
        glEnableVertexAttribArray(2)  # brush_size
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(4 * 4))
        glEnableVertexAttribArray(3)  # brush_opacity
        glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(5 * 4))
        
        # Draw quad
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        
        # Cleanup
        glBindVertexArray(0)
        glDeleteBuffers(1, [vbo])
        glDeleteVertexArrays(1, [vao])
        
        # Unbind FBO
        fbo.unbind()
        glDisable(GL_BLEND)
        
        # Mark FBO as dirty
        fbo.is_dirty = True
    
    def end_stroke(self):
        """End current brush stroke."""
        self.is_drawing = False
        self.current_preset = None
    
    def render_frame(self, frame: int):
        """
        Render accumulated brush strokes for frame.
        
        This renders the FBO texture as a screen-aligned quad
        that transforms with viewport pan/zoom/rotate.
        
        Args:
            frame: Frame number to render
        """
        # Check if FBO exists for this frame
        fbo = self.fbo_manager.get_fbo(frame)
        if fbo is None or not fbo.is_dirty:
            return  # No strokes on this frame
        
        # Setup OpenGL state
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Bind FBO texture
        fbo.bind_texture(0)
        
        # Use simple texture rendering
        # (We'll render the texture directly without shader for simplicity)
        glEnable(GL_TEXTURE_2D)
        
        # Get geometry for coordinate transformation
        if not self.geometry:
            return
        
        # Calculate screen coordinates for quad corners
        bl = itview_to_screen(self.geometry, 0, 0)  # Bottom-left
        br = itview_to_screen(self.geometry, 1, 0)  # Bottom-right
        tr = itview_to_screen(self.geometry, 1, 1)  # Top-right
        tl = itview_to_screen(self.geometry, 0, 1)  # Top-left
        
        # Render textured quad
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(bl[0], bl[1])
        glTexCoord2f(1, 0)
        glVertex2f(br[0], br[1])
        glTexCoord2f(1, 1)
        glVertex2f(tr[0], tr[1])
        glTexCoord2f(0, 1)
        glVertex2f(tl[0], tl[1])
        glEnd()
        
        # Cleanup
        glDisable(GL_TEXTURE_2D)
        fbo.unbind_texture()
        glDisable(GL_BLEND)
    
    def clear_frame(self, frame: int):
        """
        Clear all brush strokes from frame.
        
        Args:
            frame: Frame number
        """
        self.fbo_manager.clear_frame(frame)
    
    def _create_ortho_matrix(
        self,
        left: float,
        right: float,
        bottom: float,
        top: float,
        near: float,
        far: float
    ) -> np.ndarray:
        """
        Create orthographic projection matrix.
        
        Args:
            left, right: Horizontal bounds
            bottom, top: Vertical bounds
            near, far: Depth bounds
        
        Returns:
            4x4 projection matrix
        """
        matrix = np.identity(4, dtype=np.float32)
        
        matrix[0, 0] = 2.0 / (right - left)
        matrix[1, 1] = 2.0 / (top - bottom)
        matrix[2, 2] = -2.0 / (far - near)
        matrix[3, 0] = -(right + left) / (right - left)
        matrix[3, 1] = -(top + bottom) / (top - bottom)
        matrix[3, 2] = -(far + near) / (far - near)
        
        return matrix
    
    def cleanup(self):
        """Cleanup OpenGL resources."""
        self.fbo_manager.destroy_all()
        self.shader_manager.cleanup()
        
        if self.quad_vao is not None:
            glDeleteVertexArrays(1, [self.quad_vao])
            self.quad_vao = None
        
        if self.quad_vbo is not None:
            glDeleteBuffers(1, [self.quad_vbo])
            self.quad_vbo = None

