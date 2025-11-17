#version 330 core

// Vertex attributes
layout(location = 0) in vec2 position;       // Quad corners (-0.5 to 0.5)
layout(location = 1) in vec2 brush_center;   // Stamp center in normalized space
layout(location = 2) in float brush_size;    // Pressure-modulated size
layout(location = 3) in float brush_opacity; // Pressure-modulated opacity

// Uniforms
uniform mat4 projection;  // Orthographic projection matrix

// Output to fragment shader
out vec2 uv;           // Texture coordinates (0-1)
out float opacity;      // Opacity for this stamp

void main() {
    // Calculate final vertex position
    // Scale quad by brush size and translate to brush center
    vec2 offset = position * brush_size;
    vec2 final_pos = brush_center + offset;
    
    // Apply projection
    gl_Position = projection * vec4(final_pos, 0.0, 1.0);
    
    // Pass texture coordinates to fragment shader
    // Map from [-0.5, 0.5] to [0, 1]
    uv = position + vec2(0.5);
    
    // Pass opacity to fragment shader
    opacity = brush_opacity;
}

