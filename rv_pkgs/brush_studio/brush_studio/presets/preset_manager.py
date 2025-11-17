"""
Brush preset manager.

Loads, saves, and manages brush presets.
"""

from typing import Dict, List, Optional
from pathlib import Path
from brush_studio.models.brush_preset import BrushPreset


class PresetManager:
    """
    Manages brush presets.
    
    Loads presets from JSON files in the presets directory and
    provides access to them by name.
    """
    
    def __init__(self):
        """Initialize preset manager."""
        self.presets: Dict[str, BrushPreset] = {}
        self.preset_dir = Path(__file__).parent
        self.load_default_presets()
    
    def load_default_presets(self):
        """Load all preset JSON files from presets directory."""
        # Look for .json files in presets directory
        if not self.preset_dir.exists():
            return
        
        for json_file in self.preset_dir.glob("*.json"):
            try:
                preset = BrushPreset.from_json(str(json_file))
                self.presets[preset.name] = preset
            except Exception as e:
                print(f"Warning: Failed to load preset {json_file}: {e}")
    
    def get_preset(self, name: str) -> Optional[BrushPreset]:
        """
        Get preset by name.
        
        Args:
            name: Preset name
        
        Returns:
            BrushPreset if found, None otherwise
        """
        return self.presets.get(name)
    
    def get_all_presets(self) -> List[BrushPreset]:
        """
        Get list of all presets.
        
        Returns:
            List of all loaded presets
        """
        return list(self.presets.values())
    
    def get_preset_names(self) -> List[str]:
        """
        Get list of preset names.
        
        Returns:
            Sorted list of preset names
        """
        return sorted(self.presets.keys())
    
    def add_preset(self, preset: BrushPreset):
        """
        Add or update preset.
        
        Args:
            preset: BrushPreset to add
        """
        self.presets[preset.name] = preset
    
    def save_preset(self, preset: BrushPreset, filepath: Optional[str] = None):
        """
        Save preset to JSON file.
        
        Args:
            preset: Preset to save
            filepath: Optional custom filepath (defaults to presets directory)
        """
        if filepath is None:
            # Generate filename from preset name
            filename = preset.name.lower().replace(" ", "_") + ".json"
            filepath = str(self.preset_dir / filename)
        
        preset.to_json(filepath)
    
    def delete_preset(self, name: str):
        """
        Remove preset from manager.
        
        Args:
            name: Preset name
        """
        if name in self.presets:
            del self.presets[name]

