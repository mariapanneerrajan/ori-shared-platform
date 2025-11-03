from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attrs.utils import \
    get_key_out, get_key_in

class ClipAttrDissolveStart:

    def __init__(self):
        print("ClipAttrDissolveStart initialized")
        self.__initialized = False

    @property
    def id_(self)->str:
        return "dissolve_start"

    @property
    def name(self)->str:
        return "Dissolve Start"

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
        return 1001

    @property
    def dependent_attr_ids(self):
        return ["dissolve_length"]

    def set_value(self, source_group:str, value:int)->bool:        
        key_in = get_key_in(source_group)
        key_out = get_key_out(source_group)
        if value > key_out or value < key_in:
            print(f"dissolve start is out of range: {value} is not between {key_in} and {key_out}")
            return False        
        commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.startFrame", [float(value - key_in + 1)], True)
        dissolve_length = key_out - value + 1
        commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.numFrames", [float(dissolve_length)], True)
        commands.setIntProperty(f"{source_group}_cross_dissolve.node.active", [1], True)
        return True
        
    def get_value(self, source_group:str)->int:
        key_in = get_key_in(source_group)
        if not self.__initialized:
            self.__initialized = True            
            commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.startFrame", [float(0)], True)
            commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.numFrames", [float(0)], True)
            commands.setIntProperty(f"{source_group}_cross_dissolve.node.active", [0], True)
            return 0
        
        value = commands.getFloatProperty(f"{source_group}_cross_dissolve.parameters.startFrame")[0]
        value = key_in + value - 1
        return int(value)

ClipAttrApiCore.get_instance()._add_attr(ClipAttrDissolveStart())
