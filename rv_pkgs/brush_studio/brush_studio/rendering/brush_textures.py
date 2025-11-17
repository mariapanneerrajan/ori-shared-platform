"""
Procedural brush texture generation.
"""

import numpy as np
from typing import Tuple
from OpenGL.GL import *


class BrushTextureGenerator:
    """
    Generates procedural brush textures.
    
    Creates various brush tip patterns (soft circle, hard circle,
    pencil texture, etc.) as OpenGL textures.
    """
    
    @staticmethod
    def create_soft_circle(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create soft circular brush texture with smooth falloff.
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        # Create texture data
        data = np.zeros((size, size), dtype=np.float32)
        center = size / 2.0
        radius = size / 2.0
        
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                dist = np.sqrt(dx * dx + dy * dy)
                
                # Smooth falloff
                if dist < radius:
                    alpha = 1.0 - (dist / radius) ** 2
                    data[y, x] = max(0.0, alpha)
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_hard_circle(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create hard-edged circular brush texture.
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center = size / 2.0
        radius = size / 2.0 - 1.0  # Slight inset for antialiasing
        
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                dist = np.sqrt(dx * dx + dy * dy)
                
                # Hard edge with minimal antialiasing
                if dist < radius:
                    data[y, x] = 1.0
                elif dist < radius + 1.0:
                    # 1-pixel antialiasing
                    data[y, x] = radius + 1.0 - dist
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_noise_texture(size: int = 256, scale: float = 0.1) -> Tuple[int, np.ndarray]:
        """
        Create noisy brush texture (for pencil, charcoal effects).
        
        Args:
            size: Texture size in pixels (square)
            scale: Noise scale (lower = coarser)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        # Generate random noise
        np.random.seed(42)  # Reproducible
        data = np.random.rand(size, size).astype(np.float32)
        
        # Apply gaussian blur for smoother noise
        from scipy.ndimage import gaussian_filter
        data = gaussian_filter(data, sigma=scale * size)
        
        # Normalize to 0-1
        data = (data - data.min()) / (data.max() - data.min())
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_square_hard(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create hard-edged square brush texture.
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center = size / 2.0
        half_size = size / 2.0 - 1.0  # Slight inset for antialiasing
        
        for y in range(size):
            for x in range(size):
                dx = abs(x - center)
                dy = abs(y - center)
                
                # Hard edge square
                if dx < half_size and dy < half_size:
                    data[y, x] = 1.0
                elif dx < half_size + 1.0 and dy < half_size + 1.0:
                    # 1-pixel antialiasing
                    fade_x = max(0.0, half_size + 1.0 - dx)
                    fade_y = max(0.0, half_size + 1.0 - dy)
                    data[y, x] = min(fade_x, fade_y)
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_square_soft(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create soft-edged square brush texture with gradient falloff.
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center = size / 2.0
        half_size = size / 2.0
        
        for y in range(size):
            for x in range(size):
                dx = abs(x - center)
                dy = abs(y - center)
                
                # Soft falloff from center
                max_dist = max(dx, dy)
                if max_dist < half_size:
                    alpha = 1.0 - (max_dist / half_size) ** 2
                    data[y, x] = max(0.0, alpha)
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_triangle(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create triangular brush texture.
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center_x = size / 2.0
        center_y = size / 2.0
        radius = size / 2.0 - 2.0
        
        # Equilateral triangle vertices (pointing up)
        v1_x, v1_y = center_x, center_y - radius
        v2_x, v2_y = center_x - radius * 0.866, center_y + radius * 0.5
        v3_x, v3_y = center_x + radius * 0.866, center_y + radius * 0.5
        
        def sign(px, py, x1, y1, x2, y2):
            return (px - x2) * (y1 - y2) - (x1 - x2) * (py - y2)
        
        for y in range(size):
            for x in range(size):
                # Check if point is inside triangle
                d1 = sign(x, y, v1_x, v1_y, v2_x, v2_y)
                d2 = sign(x, y, v2_x, v2_y, v3_x, v3_y)
                d3 = sign(x, y, v3_x, v3_y, v1_x, v1_y)
                
                has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
                has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
                
                if not (has_neg and has_pos):
                    data[y, x] = 1.0
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_star(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create 5-pointed star brush texture.
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center_x = size / 2.0
        center_y = size / 2.0
        outer_radius = size / 2.0 - 2.0
        inner_radius = outer_radius * 0.4
        
        # Generate 5-pointed star vertices
        vertices = []
        for i in range(5):
            # Outer point
            angle = (i * 2.0 * np.pi / 5.0) - np.pi / 2.0
            vertices.append((
                center_x + outer_radius * np.cos(angle),
                center_y + outer_radius * np.sin(angle)
            ))
            # Inner point
            angle = ((i + 0.5) * 2.0 * np.pi / 5.0) - np.pi / 2.0
            vertices.append((
                center_x + inner_radius * np.cos(angle),
                center_y + inner_radius * np.sin(angle)
            ))
        
        def point_in_polygon(x, y, vertices):
            n = len(vertices)
            inside = False
            p1x, p1y = vertices[0]
            for i in range(1, n + 1):
                p2x, p2y = vertices[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            return inside
        
        for y in range(size):
            for x in range(size):
                if point_in_polygon(x, y, vertices):
                    data[y, x] = 1.0
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_splatter(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create splatter brush texture with random particle scatter.
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center = size / 2.0
        radius = size / 2.0
        
        # Generate random splatter particles
        np.random.seed(123)  # Reproducible
        num_particles = 80
        
        for _ in range(num_particles):
            # Random position within circle
            angle = np.random.uniform(0, 2 * np.pi)
            dist = np.random.uniform(0, radius * 0.9)
            px = int(center + dist * np.cos(angle))
            py = int(center + dist * np.sin(angle))
            
            # Random particle size
            particle_size = np.random.uniform(2, 8)
            intensity = np.random.uniform(0.3, 1.0)
            
            # Draw particle with soft edges
            for dy in range(int(-particle_size), int(particle_size) + 1):
                for dx in range(int(-particle_size), int(particle_size) + 1):
                    x = px + dx
                    y = py + dy
                    if 0 <= x < size and 0 <= y < size:
                        dist_from_center = np.sqrt(dx * dx + dy * dy)
                        if dist_from_center < particle_size:
                            falloff = 1.0 - (dist_from_center / particle_size)
                            data[y, x] = max(data[y, x], intensity * falloff)
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_stipple(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create stipple brush texture with dotted pattern.
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center = size / 2.0
        radius = size / 2.0
        
        # Create grid of dots
        dot_spacing = 12
        dot_size = 3
        
        for y in range(0, size, dot_spacing):
            for x in range(0, size, dot_spacing):
                # Check if dot is within circular boundary
                dx = x - center
                dy = y - center
                dist_from_center = np.sqrt(dx * dx + dy * dy)
                
                if dist_from_center < radius * 0.9:
                    # Draw dot with soft edges
                    for dy_dot in range(-dot_size, dot_size + 1):
                        for dx_dot in range(-dot_size, dot_size + 1):
                            px = x + dx_dot
                            py = y + dy_dot
                            if 0 <= px < size and 0 <= py < size:
                                dot_dist = np.sqrt(dx_dot * dx_dot + dy_dot * dy_dot)
                                if dot_dist < dot_size:
                                    falloff = 1.0 - (dot_dist / dot_size) ** 2
                                    data[py, px] = max(data[py, px], falloff)
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_grainy(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create fine-grained texture (like pencil lead).
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center = size / 2.0
        radius = size / 2.0
        
        # Generate fine grain noise
        np.random.seed(456)  # Reproducible
        noise = np.random.rand(size, size).astype(np.float32)
        
        # Apply to circular region with falloff
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                dist = np.sqrt(dx * dx + dy * dy)
                
                if dist < radius:
                    # Soft circular falloff
                    falloff = 1.0 - (dist / radius) ** 2
                    # Fine grain with some smoothing
                    grain_value = noise[y, x] * 0.7 + 0.3
                    data[y, x] = grain_value * falloff
        
        # Slight blur for pencil effect
        from scipy.ndimage import gaussian_filter
        data = gaussian_filter(data, sigma=0.5)
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_scratchy(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create rough, scratchy texture (like charcoal).
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center = size / 2.0
        radius = size / 2.0
        
        # Generate scratchy pattern with elongated noise
        np.random.seed(789)  # Reproducible
        
        # Create directional scratches
        num_scratches = 30
        for _ in range(num_scratches):
            # Random position and angle
            angle = np.random.uniform(0, 2 * np.pi)
            start_dist = np.random.uniform(0, radius * 0.7)
            sx = int(center + start_dist * np.cos(angle))
            sy = int(center + start_dist * np.sin(angle))
            
            # Scratch direction
            scratch_angle = np.random.uniform(0, 2 * np.pi)
            scratch_length = int(np.random.uniform(10, 40))
            scratch_width = np.random.uniform(1.5, 3.0)
            intensity = np.random.uniform(0.4, 1.0)
            
            # Draw scratch
            for step in range(scratch_length):
                px = int(sx + step * np.cos(scratch_angle))
                py = int(sy + step * np.sin(scratch_angle))
                
                # Draw scratch with width
                for dw in range(int(-scratch_width), int(scratch_width) + 1):
                    x = px + int(dw * np.sin(scratch_angle))
                    y = py - int(dw * np.cos(scratch_angle))
                    
                    if 0 <= x < size and 0 <= y < size:
                        # Check if within circular boundary
                        dist_from_center = np.sqrt((x - center)**2 + (y - center)**2)
                        if dist_from_center < radius:
                            falloff = 1.0 - (dist_from_center / radius) ** 2
                            width_falloff = 1.0 - abs(dw) / scratch_width
                            data[y, x] = max(data[y, x], intensity * falloff * width_falloff)
        
        # Add base texture
        base_noise = np.random.rand(size, size).astype(np.float32) * 0.3
        data = np.clip(data + base_noise, 0.0, 1.0)
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data
    
    @staticmethod
    def create_diamond(size: int = 256) -> Tuple[int, np.ndarray]:
        """
        Create diamond/rhombus brush texture.
        
        Args:
            size: Texture size in pixels (square)
        
        Returns:
            Tuple of (texture_id, pixel_data)
        """
        data = np.zeros((size, size), dtype=np.float32)
        center = size / 2.0
        half_size = size / 2.0 - 2.0
        
        # Diamond is a square rotated 45 degrees
        for y in range(size):
            for x in range(size):
                dx = abs(x - center)
                dy = abs(y - center)
                
                # Diamond distance (Manhattan distance)
                dist = dx + dy
                
                if dist < half_size:
                    data[y, x] = 1.0
                elif dist < half_size + 2.0:
                    # Antialiasing
                    data[y, x] = (half_size + 2.0 - dist) / 2.0
        
        # Upload to OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_R32F,
            size, size, 0,
            GL_RED, GL_FLOAT, data
        )
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture_id, data

