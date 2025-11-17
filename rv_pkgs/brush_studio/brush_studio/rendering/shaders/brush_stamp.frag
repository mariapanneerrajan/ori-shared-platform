#version 330 core

// Input from vertex shader
in vec2 uv;         // Texture coordinates (0-1)
in float opacity;    // Opacity for this stamp

// Uniforms
uniform vec4 brush_color;    // RGBA brush color
uniform float hardness;      // Edge hardness (0.0 = soft, 1.0 = hard)
uniform sampler2D brush_texture;  // Optional brush texture
uniform int use_texture;     // Whether to use texture (0 or 1)

// Output
out vec4 fragColor;

void main() {
    float alpha;
    
    // Use texture if enabled, otherwise use circular falloff
    if (use_texture == 1) {
        // Use texture as primary alpha source
        vec4 tex_color = texture(brush_texture, uv);
        alpha = tex_color.r;  // Texture is single-channel (red)
    } else {
        // Calculate distance from center
        vec2 center = vec2(0.5);
        float dist = length(uv - center);
        
        // Calculate alpha based on distance and hardness
        // hardness controls the transition zone:
        // - hardness = 0.0: smooth falloff from center to edge
        // - hardness = 1.0: hard edge
        float inner_radius = hardness * 0.5;
        float outer_radius = 0.5;
        
        if (dist < inner_radius) {
            // Inside hard core
            alpha = 1.0;
        } else if (dist < outer_radius) {
            // Transition zone - smooth falloff
            float t = (dist - inner_radius) / (outer_radius - inner_radius);
            alpha = 1.0 - smoothstep(0.0, 1.0, t);
        } else {
            // Outside brush
            alpha = 0.0;
        }
    }
    
    // Apply opacity modulation
    alpha *= opacity;
    
    // Final color
    fragColor = vec4(brush_color.rgb, brush_color.a * alpha);
}

