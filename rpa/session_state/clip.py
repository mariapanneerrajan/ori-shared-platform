from rpa.session_state.transforms import \
    Interpolator, RotationInterpolator, DYNAMIC_TRANSFORM_ATTRS
from rpa.session_state.color_corrections import ColorCorrections
from rpa.session_state.annotations import Annotations
import copy


class Clip:
    id_to_self = {}
    def __init__(self, playlist_id, id, path):
        Clip.id_to_self[id] = self
        self.__playlist_id = playlist_id
        self.__id = id
        self.path = path
        self.__attrs = {}
        self.__custom_attrs = {}
        self.__color_corrections = ColorCorrections()
        self.__annotations = Annotations()

        # frame edits        
        self.__source_frames = []
        self.__timewarp_map = {}        

    @property
    def id(self):
        return self.__id

    @property
    def playlist_id(self):
        return self.__playlist_id

    @property
    def color_corrections(self):
        return self.__color_corrections

    @property
    def annotations(self):
        return self.__annotations

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def set_attr_value(self, id, value):
        self.__attrs[id] = value

        if id in ("key_in", "key_out"):
            key_in = self.__attrs.get("key_in")
            key_out = self.__attrs.get("key_out")
            if None in (key_in, key_out):
                return
            self.__source_frames = list(range(key_in, key_out + 1))

    def get_attr_value(self, id):
        return self.__attrs.get(id)

    def set_attr_value_at(self, id, frame, value):
        if id in DYNAMIC_TRANSFORM_ATTRS:
            self.__attrs[id]["key_values"][frame] = value
            self.update_interpolation(id)

    def get_attr_value_at(self, id, frame):
        if id in DYNAMIC_TRANSFORM_ATTRS:
            raw_attr_value = self.__attrs.get(id)
            if not raw_attr_value:
                return None
            key_values = raw_attr_value.get("key_values")
            if not key_values:
                return raw_attr_value.get("value")

            frame_values = raw_attr_value.get("frame_values")
            keys = list(key_values.keys())
            first_key = min(keys)
            last_key = max(keys)
            if frame <= first_key:
                value_at = key_values[first_key]
            elif frame >= last_key:
                value_at = key_values[last_key]
            else:
                value_at = frame_values.get(frame)
        else:
            value_at = self.get_attr_value(id)
        
        return value_at

    def clear_attr_value_at(self, id, frame):
        if id in DYNAMIC_TRANSFORM_ATTRS:
            key_values = self.__attrs.get(id).get("key_values")
            key_values.pop(frame, None)

    def get_key_values(self, id):
        if id in DYNAMIC_TRANSFORM_ATTRS:
            key_values = self.__attrs.get(id).get("key_values", {}) if self.__attrs.get(id) else {}
            return dict(sorted(key_values.items()))
        else:
            return {}

    def update_keyable_attrs(self, id, value):
        self.__attrs[id]["value"] = value
        self.__attrs[id]["key_values"] = {}
        self.__attrs[id]["frame_values"] = {}

    def update_interpolation(self, id):
        sorted_items = dict(sorted(self.__attrs[id].get("key_values").items()))
        keys = list(sorted_items.keys())
        values = list(sorted_items.values())

        first_key = keys[0]
        last_key = keys[-1]

        interpolated_values = {}

        if id == "dynamic_rotation":
            interpolator = RotationInterpolator(keys, values)
        else:
            interpolator = Interpolator(keys, values)

        for frame in range(first_key, last_key + 1):
            interpolated_values[frame] = interpolator.get(frame)

        self.__attrs[id]["frame_values"] = interpolated_values

    def has_frame_edits(self):
        if not self.__attrs:
            return False

        for index in range(len(self.__source_frames)):
            if index < len(self.__source_frames) - 2:
                if self.__source_frames[index] == self.__source_frames[index + 1]:
                    return True
        return False

    def edit_frames(self, edit, local_frame, num_frames):        
        if edit not in (1, -1): return        
        if local_frame <= 0 or local_frame > len(self.__source_frames): return
        if num_frames <= 0: return
                    
        frame_index = local_frame - 1
        if edit == 1: # hold
            source_frame = self.__source_frames[frame_index]
            hold_frames = [source_frame] * num_frames
            # Insert values after the current frame using slice assignment
            self.__source_frames[frame_index + 1:frame_index + 1] = hold_frames
        elif edit == -1: # drop            
            del self.__source_frames[frame_index:frame_index + num_frames]        
        
        self.__set_timewarp_attr_values()

    def reset_frames(self):        
        start = self.__attrs.get("key_in")
        end = self.__attrs.get("key_out")        
        self.__source_frames = list(range(start, end + 1))
        
        self.__set_timewarp_attr_values()

    def get_source_frames(self):
        return self.__source_frames

    def __set_timewarp_attr_values(self):
        key_in = self.__attrs.get("key_in")
        if key_in is None: return

        if self.has_frame_edits():            
            tw_in = self.__source_frames[0]
            tw_out = tw_in - 1
            for _ in self.__source_frames:
                tw_out += 1
            tw_length = tw_out - tw_in + 1
        
            self.set_attr_value("timewarp_in", tw_in)
            self.set_attr_value("timewarp_out", tw_out)
            self.set_attr_value("timewarp_length", tw_length)
        else:
            self.set_attr_value("timewarp_in", None)
            self.set_attr_value("timewarp_out", None)
            self.set_attr_value("timewarp_length", None)

    def get_attrs(self):
        return copy.deepcopy(self.__attrs)

    def delete(self):
        self.__playlist_id = None
        self.path = None
        self.__attrs.clear()
        self.__custom_attrs.clear()
        self.__color_corrections.delete()
        self.__annotations.delete()
        del Clip.id_to_self[self.__id]
        self.__id = None
        del self

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path
