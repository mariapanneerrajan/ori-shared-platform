import numpy as np
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


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
        return ["cut_length", "length_diff"]

    def set_value(self, source_group:str, value:int)->bool:
        if not isinstance(value, int):
            value = self.default_value

        if not commands.propertyExists(f"{source_group}_source.custom.keyin"):
            commands.newProperty(f"{source_group}_source.custom.keyin", commands.IntType, 1)

        commands.setIntProperty(f"{source_group}_source.custom.keyin", [value], True)
        return True

    def get_value(self, source_group:str)->int:
        cut_in = commands.getIntProperty(f"{source_group}_source.cut.in")[0]
        smi = commands.sourceMediaInfo(f"{source_group}_source")
        key_in = smi.get("startFrame") if cut_in == (np.iinfo(np.int32).max * -1) else cut_in

        if not commands.propertyExists(f"{source_group}_source.custom.keyin"):
            commands.newProperty(f"{source_group}_source.custom.keyin", commands.IntType, 1)
            commands.setIntProperty(f"{source_group}_source.custom.keyin", [key_in], True)
            return key_in
        else:
            initial_value = commands.getIntProperty(f"{source_group}_source.custom.keyin")
            start_frame = smi.get("startFrame")
            if initial_value is None:
                commands.setIntProperty(f"{source_group}_source.custom.keyin", [start_frame], True)

            key_in = commands.getIntProperty(f"{source_group}_source.custom.keyin")[0]
            return key_in


ClipAttrApiCore.get_instance()._add_attr(ClipAttrKeyIn())
