def parse_boolean(value):
    if value in [None, '', 'True', 'true', '1', 'yes', 'y', 'Y', 1, True]:
        return True
    elif value in ['False', 'flase', '0', 'no', 'n', 'N', 0, False]:
        return False
    else:
        raise TypeError("option %s: invalid boolean value: %r" % (self.long, value))

def check_write_permissions(path):
    import os
    if os.path.isdir(path):
        outdir = path
    else:
        outdir = '/'.join(path.split('/')[:-1])
    return os.access(outdir, os.W_OK)

truecondition=lambda frame: True
