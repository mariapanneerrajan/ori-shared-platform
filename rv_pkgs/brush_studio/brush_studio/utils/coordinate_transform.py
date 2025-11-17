"""
Coordinate transformation utilities for brush studio.

These functions convert between different coordinate spaces to ensure
drawings transform correctly with viewport pan/zoom/rotate operations.

Reused from vector_draw package (proven implementation).
"""

from typing import Tuple, Optional, List


def image_to_itview(width: int, height: int, x: float, y: Optional[float] = None) -> Tuple[float, ...]:
    """
    Convert from image pixel space to normalized itview space (0.0 to 1.0).
    
    Image space: Absolute pixel coordinates (e.g., 1920x1080 image)
    ITView space: Normalized 0.0-1.0 coordinates (resolution-independent)
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        x: X coordinate in pixels (or single dimension if y is None)
        y: Y coordinate in pixels (None for dimension conversion)
    
    Returns:
        Tuple of (x, y) in normalized space, or single dimension if y is None
    """
    if y is None:
        # Convert dimension (e.g., brush size)
        a = image_to_itview(width, height, 0, 0)
        b = image_to_itview(width, height, x, 0)
        return (b[0] - a[0],)
    return (x / width, y / height)


def screen_to_itview(geometry: List[Tuple[float, float]], x: float, y: float) -> Tuple[float, float]:
    """
    Convert from screen/viewport space to normalized itview space (0.0 to 1.0).
    
    Screen space: Actual OpenGL viewport coordinates (with current transform applied)
    ITView space: Normalized 0.0-1.0 coordinates (resolution-independent)
    
    This is the INVERSE transformation of itview_to_screen. It uses the current
    image geometry to compute normalized coordinates that are independent of
    viewport transforms (pan, zoom, rotate).
    
    Args:
        geometry: Image geometry from rvc.imageGeometry() - 4 corner points
        x: X coordinate in screen space
        y: Y coordinate in screen space
    
    Returns:
        Tuple of (norm_x, norm_y) in normalized 0.0-1.0 space
    """
    # Geometry is [bottom-left, bottom-right, top-right, top-left]
    t = geometry[0]  # Origin (bottom-left)
    u = [geometry[1][0] - t[0], geometry[1][1] - t[1]]  # X-axis vector
    v = [geometry[3][0] - t[0], geometry[3][1] - t[1]]  # Y-axis vector
    
    # Inverse transformation: solve for (norm_x, norm_y) where screen = t + norm_x*u + norm_y*v
    k = 1.0 / (u[0] * v[1] - v[0] * u[1])  # Determinant inverse
    d = [x - t[0], y - t[1]]  # Displacement from origin
    
    norm_x = k * (v[1] * d[0] - v[0] * d[1])
    norm_y = k * (u[0] * d[1] - u[1] * d[0])
    
    return (norm_x, norm_y)


def itview_to_screen(geometry: List[Tuple[float, float]], x: float, y: Optional[float] = None) -> Tuple[float, ...]:
    """
    Convert from normalized itview space (0.0 to 1.0) to screen/viewport space.
    
    ITView space: Normalized 0.0-1.0 coordinates (resolution-independent)
    Screen space: Actual OpenGL viewport coordinates (with current transform applied)
    
    This function uses the current image geometry which includes all viewport
    transforms (pan, zoom, rotate), ensuring drawings move with the source.
    
    Args:
        geometry: Image geometry from rvc.imageGeometry() - 4 corner points
        x: X coordinate in normalized space (or dimension if y is None)
        y: Y coordinate in normalized space (None for dimension conversion)
    
    Returns:
        Tuple of (x, y) in screen space, or single dimension if y is None
    """
    if y is None:
        # Convert dimension (e.g., brush size)
        a = itview_to_screen(geometry, 0, 0)
        b = itview_to_screen(geometry, x, 0)
        return (((b[0] - a[0]) ** 2.0 + (b[1] - a[1]) ** 2.0) ** 0.5,)
    
    # Geometry is [bottom-left, bottom-right, top-right, top-left]
    t = geometry[0]  # Origin (bottom-left)
    u = [geometry[1][0] - t[0], geometry[1][1] - t[1]]  # X-axis vector
    v = [geometry[3][0] - t[0], geometry[3][1] - t[1]]  # Y-axis vector
    
    # Linear transformation: screen = t + x*u + y*v
    return (u[0] * x + v[0] * y + t[0], u[1] * x + v[1] * y + t[1])

