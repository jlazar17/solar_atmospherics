def write_corsika_set(frame, corsika_set):
    from icecube import dataclasses
    if frame['I3EventHeader'].sub_event_stream != 'TTrigger':
        return True
    frame.Put("CORSIKASet", dataclasses.I3UInt64(corsika_set))
    return True
