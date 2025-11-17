"""
Framebuffer Object (FBO) manager for GPU canvas rendering.

Manages per-frame FBOs with LRU caching for memory efficiency.
"""

from typing import Dict, Optional, Tuple
from collections import OrderedDict
from OpenGL.GL import *
import numpy as np


class FBO:
    """
    Wrapper for OpenGL Framebuffer Object.
    
    Each FBO contains a texture that accumulates brush strokes for a frame.
    """
    
    def __init__(self, width: int, height: int):
        """
        Create FBO with RGBA texture.
        
        Args:
            width: Texture width in pixels
            height: Texture height in pixels
        """
        self.width = width
        self.height = height
        self.fbo_id = None
        self.texture_id = None
        self.is_dirty = False  # Whether canvas has been modified
        
        self._create()
    
    def _create(self):
        """Create OpenGL FBO and texture resources."""
        # Generate texture
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        # Allocate texture storage (RGBA32F for high quality)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA32F,
            self.width, self.height, 0,
            GL_RGBA, GL_FLOAT, None
        )
        
        # Generate FBO
        self.fbo_id = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo_id)
        
        # Attach texture to FBO
        glFramebufferTexture2D(
            GL_FRAMEBUFFER,
            GL_COLOR_ATTACHMENT0,
            GL_TEXTURE_2D,
            self.texture_id,
            0
        )
        
        # Check FBO completeness
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"FBO incomplete: {status}")
        
        # Clear to transparent
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Unbind
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def bind(self):
        """Bind this FBO for rendering."""
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo_id)
        glViewport(0, 0, self.width, self.height)
    
    def unbind(self):
        """Unbind this FBO (return to default framebuffer)."""
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def bind_texture(self, texture_unit: int = 0):
        """
        Bind this FBO's texture for reading.
        
        Args:
            texture_unit: OpenGL texture unit (0-31)
        """
        glActiveTexture(GL_TEXTURE0 + texture_unit)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
    
    def unbind_texture(self):
        """Unbind texture."""
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def clear(self):
        """Clear FBO to transparent."""
        self.bind()
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.unbind()
        self.is_dirty = False
    
    def read_pixels(self) -> np.ndarray:
        """
        Read FBO pixels to numpy array.
        
        Returns:
            RGBA float array of shape (height, width, 4)
        """
        self.bind()
        pixels = glReadPixels(
            0, 0, self.width, self.height,
            GL_RGBA, GL_FLOAT
        )
        self.unbind()
        
        # Convert to numpy array and reshape
        data = np.frombuffer(pixels, dtype=np.float32)
        data = data.reshape((self.height, self.width, 4))
        
        # Flip vertically (OpenGL bottom-left origin)
        data = np.flipud(data)
        
        return data
    
    def upload_pixels(self, data: np.ndarray):
        """
        Upload pixel data to FBO texture.
        
        Args:
            data: RGBA float array of shape (height, width, 4)
        """
        if data.shape != (self.height, self.width, 4):
            raise ValueError(f"Data shape mismatch: {data.shape} vs ({self.height}, {self.width}, 4)")
        
        # Flip vertically for OpenGL
        data = np.flipud(data)
        
        # Upload to texture
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexSubImage2D(
            GL_TEXTURE_2D, 0, 0, 0,
            self.width, self.height,
            GL_RGBA, GL_FLOAT,
            data
        )
        glBindTexture(GL_TEXTURE_2D, 0)
        
        self.is_dirty = True
    
    def destroy(self):
        """Destroy OpenGL resources."""
        if self.fbo_id is not None:
            glDeleteFramebuffers(1, [self.fbo_id])
            self.fbo_id = None
        
        if self.texture_id is not None:
            glDeleteTextures([self.texture_id])
            self.texture_id = None


class FBOManager:
    """
    Manages per-frame FBOs with LRU caching.
    
    Creates FBOs lazily on first stroke and maintains an LRU cache
    to limit memory usage with many frames.
    """
    
    def __init__(self, max_cached_frames: int = 50):
        """
        Initialize FBO manager.
        
        Args:
            max_cached_frames: Maximum number of frames to keep in cache
        """
        self.max_cached_frames = max_cached_frames
        self.fbos: OrderedDict[int, FBO] = OrderedDict()
        self.current_size: Optional[Tuple[int, int]] = None
    
    def get_or_create_fbo(self, frame: int, width: int, height: int) -> FBO:
        """
        Get FBO for frame, creating if necessary.
        
        Args:
            frame: Frame number
            width: FBO width in pixels
            height: FBO height in pixels
        
        Returns:
            FBO for this frame
        """
        # Check if size changed (source image changed)
        if self.current_size != (width, height):
            # Clear all FBOs (size mismatch)
            self.clear_all()
            self.current_size = (width, height)
        
        # Check if FBO exists
        if frame in self.fbos:
            # Move to end (most recently used)
            self.fbos.move_to_end(frame)
            return self.fbos[frame]
        
        # Create new FBO
        fbo = FBO(width, height)
        self.fbos[frame] = fbo
        
        # Enforce cache size limit (LRU eviction)
        while len(self.fbos) > self.max_cached_frames:
            # Remove oldest (least recently used)
            oldest_frame, oldest_fbo = self.fbos.popitem(last=False)
            oldest_fbo.destroy()
        
        return fbo
    
    def has_fbo(self, frame: int) -> bool:
        """
        Check if FBO exists for frame.
        
        Args:
            frame: Frame number
        
        Returns:
            True if FBO exists
        """
        return frame in self.fbos
    
    def get_fbo(self, frame: int) -> Optional[FBO]:
        """
        Get FBO for frame without creating.
        
        Args:
            frame: Frame number
        
        Returns:
            FBO if exists, None otherwise
        """
        if frame in self.fbos:
            self.fbos.move_to_end(frame)
            return self.fbos[frame]
        return None
    
    def clear_frame(self, frame: int):
        """
        Clear FBO for frame.
        
        Args:
            frame: Frame number
        """
        if frame in self.fbos:
            self.fbos[frame].clear()
    
    def delete_frame(self, frame: int):
        """
        Delete FBO for frame.
        
        Args:
            frame: Frame number
        """
        if frame in self.fbos:
            fbo = self.fbos.pop(frame)
            fbo.destroy()
    
    def clear_all(self):
        """Clear all FBOs."""
        for fbo in self.fbos.values():
            fbo.clear()
    
    def destroy_all(self):
        """Destroy all FBOs and free GPU memory."""
        for fbo in self.fbos.values():
            fbo.destroy()
        self.fbos.clear()
        self.current_size = None
    
    def get_memory_usage(self) -> int:
        """
        Estimate memory usage in bytes.
        
        Returns:
            Estimated GPU memory usage
        """
        if not self.current_size:
            return 0
        
        width, height = self.current_size
        bytes_per_pixel = 4 * 4  # RGBA32F = 4 channels * 4 bytes
        bytes_per_fbo = width * height * bytes_per_pixel
        
        return len(self.fbos) * bytes_per_fbo

