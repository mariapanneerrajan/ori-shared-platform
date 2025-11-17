#version 330 core

// Input from vertex shader
in vec2 uv;  // Texture coordinates (0-1)

// Uniforms
uniform sampler2D canvas_texture;  // FBO texture with accumulated strokes
uniform float global_opacity;      // Global opacity multiplier

// Output
out vec4 fragColor;

void main() {
    // Sample canvas texture
    vec4 canvas_color = texture(canvas_texture, uv);
    
    // Apply global opacity
    canvas_color.a *= global_opacity;
    
    // Output final color
    fragColor = canvas_color;
}

