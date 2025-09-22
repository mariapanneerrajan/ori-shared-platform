from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrMarker:

    @property
    def id_(self)->str:
        return "marker"

    @property
    def name(self)->str:
        return "Marker"

    @property
    def data_type(self):
        return "bool"

    @property
    def is_read_only(self):
        return False

    @property
    def is_keyable(self):
        return False

    @property
    def default_value(self):
        return False

    def set_value(self, source_group:str, value:bool)->bool:
        prop = f"{source_group}_source.attributes.marker"
        if not commands.propertyExists(prop):
            commands.newProperty(prop, commands.IntType, 1)
        commands.setIntProperty(prop, [int(value)], True)
        return True

    def get_value(self, source_group:str)->bool:
        prop = f"{source_group}_source.attributes.marker"
        if not commands.propertyExists(prop):
            return False
        value = commands.getIntProperty(prop)[0]
        return bool(value)


ClipAttrApiCore.get_instance()._add_attr(ClipAttrMarker())
