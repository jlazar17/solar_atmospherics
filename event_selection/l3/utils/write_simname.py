def write_simname(frame, simname):
    from icecube import dataclasses
    if frame['I3EventHeader'].sub_event_stream != 'TTrigger':
        return True
    frame.Put("Simname", dataclasses.I3String(simname))
    return True
