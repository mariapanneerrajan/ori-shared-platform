"""
GLSL shader compilation and management.
"""

from typing import Dict, Optional
from pathlib import Path
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class ShaderManager:
    """
    Manages GLSL shader programs.
    
    Compiles and caches shader programs for efficient reuse.
    """
    
    def __init__(self):
        """Initialize shader manager."""
        self.programs: Dict[str, int] = {}
        self.shader_dir = Path(__file__).parent / "shaders"
    
    def load_shader_file(self, filename: str) -> str:
        """
        Load shader source from file.
        
        Args:
            filename: Shader filename (relative to shaders directory)
        
        Returns:
            Shader source code
        """
        filepath = self.shader_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Shader file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            return f.read()
    
    def compile_shader_from_file(
        self,
        vertex_file: str,
        fragment_file: str,
        program_name: Optional[str] = None
    ) -> int:
        """
        Compile shader program from files.
        
        Args:
            vertex_file: Vertex shader filename
            fragment_file: Fragment shader filename
            program_name: Optional name for caching (defaults to vertex_file)
        
        Returns:
            Compiled shader program ID
        """
        if program_name is None:
            program_name = vertex_file
        
        # Check cache
        if program_name in self.programs:
            return self.programs[program_name]
        
        # Load source code
        vertex_source = self.load_shader_file(vertex_file)
        fragment_source = self.load_shader_file(fragment_file)
        
        # Compile program
        program = self.compile_shader_from_source(
            vertex_source,
            fragment_source
        )
        
        # Cache program
        self.programs[program_name] = program
        
        return program
    
    def compile_shader_from_source(
        self,
        vertex_source: str,
        fragment_source: str
    ) -> int:
        """
        Compile shader program from source code.
        
        Args:
            vertex_source: Vertex shader source
            fragment_source: Fragment shader source
        
        Returns:
            Compiled shader program ID
        """
        try:
            # Compile shaders
            vertex_shader = compileShader(vertex_source, GL_VERTEX_SHADER)
            fragment_shader = compileShader(fragment_source, GL_FRAGMENT_SHADER)
            
            # Link program
            program = compileProgram(vertex_shader, fragment_shader)
            
            # Clean up individual shaders (no longer needed after linking)
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
            
            return program
        
        except Exception as e:
            raise RuntimeError(f"Shader compilation failed: {e}")
    
    def get_program(self, name: str) -> Optional[int]:
        """
        Get cached shader program.
        
        Args:
            name: Program name
        
        Returns:
            Program ID if cached, None otherwise
        """
        return self.programs.get(name)
    
    def use_program(self, program: int):
        """
        Activate shader program.
        
        Args:
            program: Program ID
        """
        glUseProgram(program)
    
    def get_uniform_location(self, program: int, name: str) -> int:
        """
        Get uniform location in shader program.
        
        Args:
            program: Program ID
            name: Uniform name
        
        Returns:
            Uniform location
        """
        location = glGetUniformLocation(program, name)
        if location == -1:
            # Warning: uniform not found (might be optimized out)
            pass
        return location
    
    def set_uniform_float(self, program: int, name: str, value: float):
        """Set float uniform."""
        location = self.get_uniform_location(program, name)
        if location != -1:
            glUniform1f(location, value)
    
    def set_uniform_int(self, program: int, name: str, value: int):
        """Set int uniform."""
        location = self.get_uniform_location(program, name)
        if location != -1:
            glUniform1i(location, value)
    
    def set_uniform_vec4(self, program: int, name: str, value: tuple):
        """Set vec4 uniform."""
        location = self.get_uniform_location(program, name)
        if location != -1:
            glUniform4f(location, value[0], value[1], value[2], value[3])
    
    def set_uniform_matrix4(self, program: int, name: str, matrix):
        """Set mat4 uniform."""
        location = self.get_uniform_location(program, name)
        if location != -1:
            glUniformMatrix4fv(location, 1, GL_FALSE, matrix)
    
    def cleanup(self):
        """Delete all shader programs."""
        for program in self.programs.values():
            glDeleteProgram(program)
        self.programs.clear()

