"""
Interpolation utilities for smooth brush strokes.
"""

import math
from typing import List, Tuple


def interpolate_points(
    x1: float, y1: float, 
    x2: float, y2: float, 
    spacing: float
) -> List[Tuple[float, float]]:
    """
    Interpolate points between two coordinates based on spacing.
    
    This ensures smooth brush strokes by adding intermediate points
    when the distance between consecutive input points is large.
    
    Args:
        x1, y1: Starting point coordinates
        x2, y2: Ending point coordinates
        spacing: Desired spacing between points (0.0-1.0, relative to brush size)
    
    Returns:
        List of (x, y) tuples representing interpolated points
    """
    # Calculate distance between points
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    
    # If points are very close, no interpolation needed
    if dist < spacing * 0.5:
        return []
    
    # Calculate number of intermediate points needed
    num_points = max(1, int(dist / spacing))
    
    # Generate interpolated points
    points = []
    for i in range(1, num_points + 1):
        t = i / num_points
        x = x1 + dx * t
        y = y1 + dy * t
        points.append((x, y))
    
    return points


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values.
    
    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0.0-1.0)
    
    Returns:
        Interpolated value
    """
    return a + (b - a) * t


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """
    Smooth Hermite interpolation between 0 and 1.
    
    Args:
        edge0: Lower edge of interpolation range
        edge1: Upper edge of interpolation range
        x: Value to interpolate
    
    Returns:
        Smoothly interpolated value (0.0-1.0)
    """
    # Clamp x to range [edge0, edge1]
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    # Evaluate polynomial
    return t * t * (3.0 - 2.0 * t)

