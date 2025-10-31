from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attrs.utils import get_key_out


class ClipAttrKeyOut:

    @property
    def id_(self)->str:
        return "key_out"

    @property
    def name(self)->str:
        return "Key Out"

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
        return ["cut_length", "length_diff"]

    def set_value(self, source_group:str, value:int)->bool:
        if not isinstance(value, int):
            value = self.default_value

        if not commands.propertyExists(f"{source_group}_source.custom.keyout"):
            commands.newProperty(f"{source_group}_source.custom.keyout", commands.IntType, 1)

        commands.setIntProperty(f"{source_group}_source.custom.keyout", [value], True)
        return True

    def get_value(self, source_group:str)->int:
        return get_key_out(source_group)


ClipAttrApiCore.get_instance()._add_attr(ClipAttrKeyOut())