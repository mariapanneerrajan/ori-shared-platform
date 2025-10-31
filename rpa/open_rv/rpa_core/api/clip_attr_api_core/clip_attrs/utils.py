from rv import commands
import numpy as np


def get_key_in(source_group:str)->int:
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


def get_key_out(source_group:str)->int:
    cut_out = commands.getIntProperty(f"{source_group}_source.cut.out")[0]
    smi = commands.sourceMediaInfo(f"{source_group}_source")
    key_out = smi.get("endFrame") if cut_out == (np.iinfo(np.int32).max) else cut_out

    if not commands.propertyExists(f"{source_group}_source.custom.keyout"):
        commands.newProperty(f"{source_group}_source.custom.keyout", commands.IntType, 1)
        commands.setIntProperty(f"{source_group}_source.custom.keyout", [key_out], True)
        return key_out
    else:
        initial_value = commands.getIntProperty(f"{source_group}_source.custom.keyout")
        end_frame = smi.get("endFrame")
        if initial_value is None:
            commands.setIntProperty(f"{source_group}_source.custom.keyout", [end_frame], True)

        key_out = commands.getIntProperty(f"{source_group}_source.custom.keyout")[0]
        return key_out
