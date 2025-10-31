from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attrs.utils import get_key_in


class ClipAttrKeyIn:

    @property
    def id_(self)->str:
        return "key_in"

    @property
    def name(self)->str:
        return "Key In"

    @property
    def data_type(self):
        return "int"

    @property
    def is_read_only(self):
        return False

    @property
    def is_keyable(self):
        return False

    @property
    def default_value(self):
        return 0

    @property
    def dependent_attr_ids(self):
        return ["cut_length", "length_diff", "dissolve_start", "dissolve_length"]

    def set_value(self, source_group:str, value:int)->bool:
        if not isinstance(value, int):
            value = self.default_value

        if not commands.propertyExists(f"{source_group}_source.custom.keyin"):
            commands.newProperty(f"{source_group}_source.custom.keyin", commands.IntType, 1)

        commands.setIntProperty(f"{source_group}_source.custom.keyin", [value], True)
        
        # Update dissolve_start and dissolve_length
        dissolve_start = commands.getFloatProperty(f"{source_group}_cross_dissolve.parameters.startFrame")[0]
        dissolve_start = value + dissolve_start - 1
        
        return True

    def get_value(self, source_group:str)->int:
        return get_key_in(source_group)


ClipAttrApiCore.get_instance()._add_attr(ClipAttrKeyIn())
